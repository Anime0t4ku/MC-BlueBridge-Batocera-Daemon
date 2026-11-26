#!/bin/sh
set -eu

source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
app_dir=/userdata/system/bluebridge
service_dir=/userdata/system/services
data_dir=/userdata/system/configs/bluebridge
service="$service_dir/bluebridge"

command -v batocera-services >/dev/null 2>&1 || {
    echo 'Run this installer on Batocera v38 or newer.' >&2
    exit 1
}
command -v python3 >/dev/null 2>&1 || {
    echo 'Python 3 is required on this Batocera image.' >&2
    exit 1
}
python3 "$source_dir/bluebridge_daemon.py" --version
sh -n "$source_dir/bluebridge"

mkdir -p "$app_dir" "$service_dir" "$data_dir"
staging=$(mktemp -d "$app_dir/install.XXXXXX")
trap 'rm -rf "$staging"' EXIT
cp "$source_dir/bluebridge_daemon.py" "$source_dir/bluebridge_updater.py" "$source_dir/bluebridge" "$staging/"
chmod +x "$staging/bluebridge"

if [ -f "$service" ]; then
    sh "$service" stop
fi
mv -f "$staging/bluebridge_updater.py" "$app_dir/bluebridge_updater.py"
mv -f "$staging/bluebridge_daemon.py" "$app_dir/bluebridge_daemon.py"
mv -f "$staging/bluebridge" "$service"
batocera-services enable bluebridge
batocera-services start bluebridge
sh "$service" status
printf '%s\n' 'MC BlueBridge installed. Default address: http://YOUR-BATOCERA-IP:9191/'
