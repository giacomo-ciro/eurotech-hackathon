# Detect port
```
lerobot-find-port
```

# Detect Cameras
To get the available cameras and their indices:
```
lerobot-find-cameras opencv
```

# Follower
On `gciro-macbook`:
```
/dev/tty.usbmodem5A680099311
```
Then run:
```
lerobot-calibrate \
    --robot.type=so101_follower \
    --robot.port=/dev/tty.usbmodem5A680099311 \
    --robot.id=Follower
```

# Leader
On `gciro-macbook`:
```
/dev/tty.usbmodem5A680094911
```
Then run:
```
lerobot-calibrate \
    --teleop.type=so101_leader \
    --teleop.port=/dev/tty.usbmodem5A680094911 \
    --teleop.id=Leader
```

# Teleoperate
Use leader to teleoperate follower via (on `gciro-macbook`):
```
lerobot-teleoperate \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5A680094911 \
  --teleop.id=Leader \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5A680099311 \
  --robot.id=Follower \
  --robot.cameras="{wrist_cam: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 25}, laptop_cam: {type: opencv, index_or_path: 1, width: 1920, height: 1080, fps: 15}}" \
  --display_data=True
```