from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.teleoperators.so_leader.config_so_leader import SOLeaderTeleopConfig


def make_robot_config(cfg) -> SOFollowerRobotConfig:
    cameras = {
        "wrist_cam": OpenCVCameraConfig(
            index_or_path=cfg.robot.cam_index,
            width=cfg.robot.cam_width,
            height=cfg.robot.cam_height,
            fps=cfg.robot.fps,
        )
    }
    if hasattr(cfg.robot, "cam2_index") and cfg.robot.cam2_index is not None:
        cameras["camera2"] = OpenCVCameraConfig(
            index_or_path=cfg.robot.cam2_index,
            width=cfg.robot.cam2_width,
            height=cfg.robot.cam2_height,
            fps=cfg.robot.fps,
        )
    return SOFollowerRobotConfig(port=cfg.robot.follower_port, id="Follower", cameras=cameras)


def make_teleop_config(cfg) -> SOLeaderTeleopConfig:
    return SOLeaderTeleopConfig(port=cfg.robot.leader_port, id="Leader")
