from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig


def make_robot_config(cfg) -> SOFollowerRobotConfig:
    return SOFollowerRobotConfig(
        port=cfg.robot.follower_port,
        id="Follower",
        cameras={
            "wrist_cam": OpenCVCameraConfig(
                index_or_path=cfg.robot.cam_index,
                width=cfg.robot.cam_width,
                height=cfg.robot.cam_height,
                fps=cfg.robot.fps,
            )
        },
    )


def make_teleop_config(cfg) -> SOLeaderTeleopConfig:
    return SOLeaderTeleopConfig(port=cfg.robot.leader_port, id="Leader")
