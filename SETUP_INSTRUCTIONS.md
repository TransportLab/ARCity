# How this works
I have the following systemd services running:
 1. Send a webhook on reboot (ARCity-webhook.service)
 2. Run webpack (ARCity-webpack.service)
 3. Run the server (ARCity-server.service)
 4. Open firefox fullscreen in kiosk mode (ARCity-browser.service)
 5. Check the github repo for updates and pull them (ARCity-auto-git-pull.service & ARCity-auto-git-pull.timer)

These need to be copied across to `/etc/systemd/system/` and then enabled and started with `systemctl enable <service-name>`. The git pull service doesnt need to be enabled, just the timer.

We also need to set up the BIOS to restart the computer when it loses power. This is done by going into the BIOS (keep pushing F2 after restart) and setting the power loss option to restart.

In principle from then everything should just work!
