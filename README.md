# MC BlueBridge Daemon for Batocera 

Pair controllers, adjust their profiles, and update your MC BlueBridge adapter from a browser while the adapter stays plugged into Batocera.

## What you need

- An ARM64 (aarch64) or x64 (x86_64) Batocera system with Python 3 and support for user services. The same download works on both architectures.
- An MC BlueBridge adapter and a USB data cable.
- A phone or computer on the same network as Batocera.

## Install

1. Download the Batocera package from the GitHub release and extract it.
2. Copy the extracted `MC-BlueBridge-Batocera` folder into `/userdata/system/` on Batocera. From Windows, you can open `\\BATOCERA\share\system` in File Explorer. If the hostname does not resolve, replace `BATOCERA` with the device’s IP address.
3. In a Batocera terminal or SSH session, run the following commands.

   ```sh
   cd /userdata/system/MC-BlueBridge-Batocera
   sh install.sh
   ```

4. Plug the BlueBridge adapter into Batocera. Open `http://YOUR-BATOCERA-IP:9191/` in a browser on the same network, replacing `YOUR-BATOCERA-IP` with the IP address shown in Batocera’s **Network Settings**.

The installer starts the service immediately and enables it at boot. The web interface has no login, so use it on a trusted local network.

## Manage your adapter

- Pair controllers and manage paired or blocked devices.
- Set up profiles, remap buttons, and adjust stick deadzones. Turbo and macros are available on supported firmware and modes.
- Test controller input and rumble, check battery status, and download diagnostics.
- Change the adapter’s USB output mode and manage single- or multi-controller operation where supported.
- Check for firmware updates, install a local UF2, or back up and restore the adapter’s configuration.

If more than one adapter is connected, choose the one you want to manage from **Adapter to manage**.

## Update the Batocera service

Download and extract the newer Batocera package, then run its `install.sh` again. The installer preserves service settings and firmware backups.

## Troubleshooting

- **The page won’t open.** Check that the browser is on the same network as Batocera and that you’re using Batocera’s IP address. To check the service, run `sh /userdata/system/services/bluebridge status` in a Batocera terminal or SSH session.
- **The page opens but the adapter is missing.** Check that BlueBridge is plugged into Batocera and that the USB cable supports data.
- **The service won’t start.** Check the log at `/userdata/system/configs/bluebridge/bluebridge.log`. After a reboot, the service also appears in EmulationStation under **System Settings → Services**.

## Uninstall

Run these commands in a Batocera terminal or SSH session.

```sh
batocera-services stop bluebridge
batocera-services disable bluebridge
rm /userdata/system/services/bluebridge
```

These commands remove the service entry and keep your settings and firmware backups for a future reinstall.
