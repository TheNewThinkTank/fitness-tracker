# Known Issues

## Issue: Google Drive not mounting / signing in on macOS Ventura 13.3

Google Drive on macOS Ventura 13.4.1 spontaneously switches local mounting point between
`/Users/<USER>/Google Drive/` and
`/Users/<USER>/Library/CloudStorage/GoogleDrive-<EMAIL>/`, or fails to sign in.

**solution**:

* hit `Command + Shift + G`, to open a `Go to Folder` window
* copy and paste path: `~/Library/Application Support/` and hit Enter / Click the Go button
* inside the `Application Supporter` dir, navigate to the Google dir
* move the `DriveFS` dir to the bin / trash
* empty bin / trash and restart computer

## Issue: Mounting directories directly from Google Drive is not supported by Docker Compose

Docker Compose can only mount directories that are accessible on the local filesystem

## Issue: zsh: command not found: docker-compose

**solution**:

```BASH
sudo rm /usr/local/bin/docker-compose

sudo ln -s /Applications/Docker.app/Contents/Resources/cli-plugins/docker-compose /usr/local/bin/docker-compose

# check version:
docker-compose version

# Output should be similar to:
Docker Compose version v2.29.1-desktop.1
```
