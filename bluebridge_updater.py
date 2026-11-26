"""GitHub release updates for the Batocera management service."""
import ast
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile

REPO = 'Anime0t4ku/MC-BlueBridge-Batocera-Daemon'
ASSET = 'MC-BlueBridge-Batocera.zip'
MAX_ARCHIVE = 16 * 1024 * 1024
PAYLOADS = ('bluebridge_daemon.py', 'bluebridge_updater.py', 'bluebridge')
PREFIX = 'https://github.com/' + REPO + '/releases/download/'
SERVICE_PATH = Path('/userdata/system/services/bluebridge')


def version(value):
    match = re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)', str(value))
    if not match:
        raise ValueError('Expected a stable daemon version')
    return tuple(int(x) for x in match.groups())


def fetch_json(url):
    request = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'MC-BlueBridge-Batocera-Updater'})
    with urllib.request.urlopen(request, timeout=25) as response:
        data = response.read(2 * 1024 * 1024 + 1)
    if len(data) > 2 * 1024 * 1024:
        raise ValueError('Release metadata is too large')
    return json.loads(data)


def latest(installed):
    release = fetch_json('https://api.github.com/repos/' + REPO + '/releases/latest')
    if release.get('draft') or release.get('prerelease'):
        raise ValueError('No stable daemon release available')
    tag = release.get('tag_name', '')
    newer = version(tag) > version(installed)
    for asset in release.get('assets', []):
        url = asset.get('browser_download_url', '')
        if asset.get('name') == ASSET and url.startswith(PREFIX + tag + '/') and 0 < int(asset.get('size', 0)) <= MAX_ARCHIVE:
            return {'version': tag.lstrip('v'), 'installed': installed, 'update_available': newer,
                    'url': url, 'size': int(asset['size']), 'digest': asset.get('digest'),
                    'notes': str(release.get('body') or '')[:30000]}
    raise ValueError('This release has no ' + ASSET + ' download')


def write_status(data_root, state, message, **extra):
    root = Path(data_root)
    record = dict(state=state, message=message, updated=time.time(), **extra)
    temporary = root / 'daemon-update-status.tmp'
    with temporary.open('w') as stream:
        json.dump(record, stream)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, root / 'daemon-update-status.json')


def update_lock(data_root):
    Path(data_root).mkdir(parents=True, exist_ok=True)
    lock = open(Path(data_root) / 'daemon-update.lock', 'a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        return None
    return lock


def busy(data_root):
    lock = update_lock(data_root)
    if lock is None:
        return True
    lock.close()
    return False


def status(data_root, installed):
    try:
        result = json.loads((Path(data_root) / 'daemon-update-status.json').read_text())
    except (OSError, ValueError):
        result = {'state': 'idle', 'message': 'Ready to check for Batocera daemon updates.'}
    result['busy'] = busy(data_root)
    result['installed'] = installed
    if not result['busy'] and result['state'] in ('starting', 'downloading', 'validating', 'installing', 'restarting', 'rolling_back'):
        result.update(state='error', message='Daemon update was interrupted. Check the daemon update log before retrying.')
    return result


def start(app_root, data_root, installed, expected_version):
    version(expected_version)
    lock = update_lock(data_root)
    if lock is None:
        raise RuntimeError('A Batocera daemon update is already running')
    stage = None
    try:
        stage = Path(tempfile.mkdtemp(prefix='daemon-update-', dir=data_root))
        worker = stage / 'worker.py'
        shutil.copy2(__file__, worker)
        write_status(data_root, 'starting', 'Preparing Batocera daemon update.', version=expected_version)
        with open(Path(data_root) / 'daemon-update.log', 'ab') as log:
            subprocess.Popen([sys.executable, str(worker), '--worker', str(app_root), str(data_root), installed,
                              expected_version, str(lock.fileno())], pass_fds=(lock.fileno(),),
                             stdout=log, stderr=log, start_new_session=True)
    except Exception as error:
        write_status(data_root, 'error', str(error))
        if stage:
            shutil.rmtree(stage, ignore_errors=True)
        raise
    finally:
        lock.close()


def download(info, data_root):
    if not info['url'].startswith(PREFIX):
        raise ValueError('Unexpected daemon download URL')
    chunks, size = [], 0
    request = urllib.request.Request(info['url'], headers={'User-Agent': 'MC-BlueBridge-Batocera-Updater'})
    with urllib.request.urlopen(request, timeout=45) as response:
        if urllib.parse.urlsplit(response.geturl()).scheme != 'https':
            raise ValueError('Daemon download must use HTTPS')
        while True:
            chunk = response.read(65536)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_ARCHIVE or size > info['size']:
                raise ValueError('Daemon download is too large')
            chunks.append(chunk)
            write_status(data_root, 'downloading', 'Downloading Batocera daemon.', version=info['version'], percent=round(size * 100 / info['size']))
    data = b''.join(chunks)
    if len(data) != info['size']:
        raise ValueError('Incomplete daemon download')
    digest = info.get('digest')
    if digest:
        if not digest.startswith('sha256:') or hashlib.sha256(data).hexdigest() != digest[7:]:
            raise ValueError('Daemon download checksum mismatch')
    return data


def unpack(data, stage, expected_version):
    """Read only the three allowlisted payloads; never extract archive paths."""
    payloads = {}
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if len(archive.infolist()) > 1000:
            raise ValueError('Daemon archive has too many entries')
        for entry in archive.infolist():
            path = PurePosixPath(entry.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in entry.filename:
                raise ValueError('Unsafe daemon archive path')
            if path.name not in PAYLOADS or entry.is_dir():
                continue
            if entry.file_size > 4 * 1024 * 1024 or path.name in payloads:
                raise ValueError('Invalid or duplicate daemon payload')
            if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Daemon payload cannot be a symlink')
            payloads[path.name] = archive.read(entry)
    if set(payloads) != set(PAYLOADS):
        raise ValueError('Release is missing daemon update files')
    for name, data in payloads.items():
        if name.endswith('.py'):
            tree = ast.parse(data, filename=name)
            if name == 'bluebridge_daemon.py':
                versions = [ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                            and any(isinstance(t, ast.Name) and t.id == 'DAEMON_VERSION' for t in n.targets)]
                if versions != [expected_version]:
                    raise ValueError('Daemon version does not match release tag')
        (Path(stage) / name).write_bytes(data)
    subprocess.run(['sh', '-n', str(Path(stage) / 'bluebridge')], check=True, timeout=10)
    result = subprocess.run([sys.executable, str(Path(stage) / 'bluebridge_daemon.py'), '--version'],
                            capture_output=True, text=True, check=True, timeout=15)
    if result.stdout.strip() != expected_version:
        raise ValueError('New daemon version check failed')


def run_control(script, action):
    subprocess.run([sys.executable, str(script), '--control', action], check=True, timeout=25)


def health(data_root, expected_version):
    config_path = Path(data_root) / 'config.json'
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    host = config.get('host', '0.0.0.0')
    host = '127.0.0.1' if host in ('0.0.0.0', '') else '::1' if host == '::' else host
    if ':' in host:
        host = '[' + host + ']'
    url = 'http://%s:%d/status' % (host, int(config.get('port', 9191)))
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for _ in range(30):
        try:
            with opener.open(url, timeout=2) as response:
                info = json.load(response)
            if info.get('ok') and info.get('version') == expected_version:
                return
        except (OSError, ValueError):
            pass
        time.sleep(0.5)
    raise RuntimeError('Updated daemon did not pass its health check')


def replace(source, destination):
    destination = Path(destination)
    temporary = destination.with_name(destination.name + '.update-tmp')
    shutil.copy2(source, temporary)
    with temporary.open('rb') as stream:
        os.fsync(stream.fileno())
    os.replace(temporary, destination)


def worker(app_root, data_root, installed, expected_version):
    stage = Path(__file__).resolve().parent
    app_root, data_root = Path(app_root), Path(data_root)
    daemon = app_root / 'bluebridge_daemon.py'
    service = SERVICE_PATH
    backup = data_root / 'daemon-previous'
    targets = {'bluebridge_daemon.py': daemon, 'bluebridge_updater.py': app_root / 'bluebridge_updater.py', 'bluebridge': service}
    stopped = False
    changed = False
    try:
        info = latest(installed)
        if not info['update_available'] or info['version'] != expected_version:
            raise ValueError('Release changed or no newer daemon release is available. Check for updates again.')
        if shutil.disk_usage(data_root).free < 4 * MAX_ARCHIVE:
            raise RuntimeError('Not enough free space for a safe daemon update')
        data = download(info, data_root)
        write_status(data_root, 'validating', 'Verifying Batocera daemon release.', version=expected_version)
        unpack(data, stage, expected_version)
        # Keep a complete previous installation before stopping the running service.
        backup.mkdir(parents=True, exist_ok=True)
        for name, destination in targets.items():
            shutil.copy2(destination, backup / name)
        write_status(data_root, 'installing', 'Installing Batocera daemon. Management will briefly disconnect.', version=expected_version)
        stopped = True
        run_control(daemon, 'stop')
        for name, destination in targets.items():
            changed = True
            replace(stage / name, destination)
        service.chmod(0o755)
        write_status(data_root, 'restarting', 'Restarting Batocera daemon.', version=expected_version)
        run_control(daemon, 'start')
        health(data_root, expected_version)
        write_status(data_root, 'success', 'Batocera daemon updated to v%s. Adapter firmware was not changed.' % expected_version, version=expected_version)
    except Exception as error:
        print('Daemon update failed:', error, flush=True)
        if stopped or changed:
            write_status(data_root, 'rolling_back', 'Restoring previous Batocera daemon.', version=installed)
            try:
                # Use the known previous control implementation even if the new one is broken.
                # Process lookup uses the installed app directory.
                replace(backup / 'bluebridge_daemon.py', daemon)
                run_control(daemon, 'stop')
                for name, destination in targets.items():
                    replace(backup / name, destination)
                run_control(daemon, 'start')
                health(data_root, installed)
                write_status(data_root, 'error', 'Daemon update failed; previous version restored. ' + str(error), rolled_back=True)
            except Exception as rollback_error:
                write_status(data_root, 'error', 'Daemon update failed and automatic recovery needs attention: ' + str(rollback_error) + '. Previous files: ' + str(backup))
        else:
            write_status(data_root, 'error', 'Daemon update failed; installed version unchanged. ' + str(error))
    finally:
        shutil.rmtree(stage, ignore_errors=True)


if __name__ == '__main__':
    if len(sys.argv) != 7 or sys.argv[1] != '--worker':
        raise SystemExit('This helper is started by the Batocera daemon.')
    # Keep the inherited lock alive for the whole update, including the restart.
    with os.fdopen(int(sys.argv[6]), 'a') as update_guard:
        worker(*sys.argv[2:6])
