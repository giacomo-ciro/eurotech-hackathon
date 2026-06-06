# LeRobot Scripts

All scripts read config from `configs/config.yaml`. User-specific ports and camera index live in `configs/user/<name>.yaml`.

Use the leader arm to control the follower arm live:
```
uv run python scripts/teleoperate.py
```

Record teleoperation episodes into a dataset:
```
uv run python scripts/record.py
```

Replay a recorded episode on the robot:
```
uv run python scripts/replay.py
```

Train an ACT policy on the recorded dataset:
```
uv run python scripts/train.py
```

Run a trained policy on the robot:
```
uv run python scripts/deploy.py
```

Move the robot by hand and save joint angles to a file:
```
uv run python scripts/save_pose.py
uv run python scripts/save_pose.py save_pose.out=dump/rest.yaml
```

Overwrite the dataset instead of appending:
```
uv run python scripts/record.py dataset.overwrite=true
```

Switch user config:
```
uv run python scripts/record.py user=<name>
```
