#!/usr/bin/env bash
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5A680099311 \
  --robot.id=Follower \
  --robot.calibration_dir=/Users/vittorio/Downloads/calibration \
  --robot.cameras="{wrist_cam: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 25}}" \
  --dataset.repo_id=local/eval_act \
  --dataset.root=outputs/eval_data \
  --dataset.num_episodes=1 \
  --dataset.single_task="Pick the pill bottle" \
  --dataset.push_to_hub=false \
  --policy.path=outputs/train/act_blue/checkpoints/010000/pretrained_model
