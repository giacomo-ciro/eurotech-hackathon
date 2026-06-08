# EuroTech x HKTE Hackathon: SO-101 Robotic Arm

<div align="center">

[Davide Beltrame](https://davidebeltrame.com) · [Alex John Caldarone](https://www.linkedin.com/in/alexjohncaldarone/) · [Giacomo Cirò](https://giacomociro.com) · [Vittorio Rossi](https://vittoriorossi.com)

</div>

This is our repo for the [EuroTech x HKTE Hackathon](https://www.hkengage.gov.hk/en/events/eurotech-x-hkte-hackathon): a playground for the SO-101 robotic arm where we teleoperated, collected data, and trained policies. We also developed a prototype platform born from the failures we ran into along the way.

We recorded the SO-101 picking up a cube by teleoperating ~100 episodes, then trained [ACT](https://github.com/tonyzhaozh/act) and [SmolVLA](https://huggingfingface.co/blog/smolvla) on the data. Both policies failed, below we elaborate on why. Those struggles felt universal enough to robotics teams that we also prototyped a startup concept around them: a platform for automatic data labeling (business logic and platform only, not a working pipeline, see [`archive/`](archive/)).

<table>
  <tr>
    <th width="50%" align="center"><div align="center">Blue cube pick</div></th>
    <th width="50%" align="center"><div align="center">Red cube pick</div></th>
  </tr>
  <tr>
    <td align="center">
      <img src="public/blue_ext.gif" alt="External view of the blue cube pick" width="320"><br><sub>External&nbsp;camera</sub>
      <br><br>
      <img src="public/blue_pov.gif" alt="First-person view of the blue cube pick" width="320"><br><sub>Wrist-mounted&nbsp;camera</sub>
    </td>
    <td align="center">
      <img src="public/red_ext.gif" alt="External view of the red cube pick" width="320"><br><sub>External&nbsp;camera</sub>
      <br><br>
      <img src="public/red_pov.gif" alt="First-person view of the red cube pick" width="320"><br><sub>Wrist-mounted&nbsp;camera</sub>
    </td>
  </tr>
</table>

*Actions performed in these demos are teleoperated.*

## What we learned

Over 24 hours with the SO-101, we tried a lot and failed a lot. The key lessons:
- **Data collection is everything.** The policy is only as good as the demonstrations, and "enough" good demonstrations is a much higher bar than it looks.
- **Consistency of setup matters more than volume.** We recorded ~100 episodes at 4 a.m., then trained and deployed in the morning at 10 a.m. The lighting had completely changed — shadows on the camera POV were different enough to throw the policy off. Same arm, same task, same data... different light, different result.
- **"Simple" tasks aren't simple.** We started with sorting pills by shape and color. Too ambitious. We scaled down to sorting colored boxes. Still too hard. We scaled down to just picking up a box. Still too hard. We scaled down to pointing at a box. Still hard. Each step down revealed how much is actually happening in what looks like a trivial motion.

## Usage

Sync the environment:
```bash
uv sync
```

Find the USB port for each arm, then calibrate it (see the [SO-101 docs](https://huggingface.co/docs/lerobot/so101) for the full hardware setup):
```bash
lerobot-find-port # follow instructions to detect the port

lerobot-calibrate \
    --robot.type=so101_follower \
    --robot.port=/dev/tty.usbmodem58760431551 \ # replace with your port
    --robot.id=Follower

lerobot-calibrate \
    --teleop.type=so101_leader \
    --teleop.port=/dev/tty.usbmodem58760431551 \  # replace with your port
    --teleop.id=Leader
```

The following scripts read directly from [configs/config.yaml](configs/config.yaml), update it accordingly.

```bash
uv run python scripts/teleoperate.py  # use the leader arm to control the follower arm live
uv run python scripts/record.py       # record teleoperation episodes into a dataset
uv run python scripts/replay.py       # replay a recorded episode on the robot
uv run python scripts/train.py        # train an ACT policy on the recorded dataset
uv run python scripts/deploy.py       # run a trained policy on the robot
```

See [`archive/LEROBOT.md`](archive/LEROBOT.md) for more commands (saving poses, overwriting datasets, switching user configs).