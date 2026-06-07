from __future__ import annotations

import math
import tempfile
from pathlib import Path

import rerun as rr
import rerun.blueprint as rrb

from ..models.schemas import Episode, TimeseriesPoint


TIMELINE = "trajectory"

LINK_LENGTHS = {
    "upper": 0.18,
    "forearm": 0.16,
    "wrist": 0.10,
    "tool": 0.07,
}

LINK_SPECS = {
    "upper": (LINK_LENGTHS["upper"], [56, 189, 248, 255]),
    "forearm": (LINK_LENGTHS["forearm"], [94, 234, 212, 255]),
    "wrist": (LINK_LENGTHS["wrist"], [252, 211, 77, 255]),
    "tool": (LINK_LENGTHS["tool"], [229, 231, 235, 255]),
}


Matrix4 = tuple[tuple[float, float, float, float], ...]
Vec3 = tuple[float, float, float]


def export_episode_rrd(episode: Episode) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".rrd", delete=False) as tmp:
        path = Path(tmp.name)

    try:
        rec = rr.RecordingStream(
            "so101_trajectory_replay",
            recording_id=f"{episode.dataset_id}_{episode.id}",
        )
        rec.save(path)
        _log_static_scene(rec, episode)

        ee_positions: list[Vec3] = []
        for point in episode.timeseries:
            pose = _pose_from_joints(point.joints)
            ee_positions.append(_translation(pose["gripper"]))

        if ee_positions:
            rec.log(
                "world/robot/end_effector_path",
                rr.LineStrips3D([ee_positions], colors=[[34, 211, 238, 180]], radii=[0.003]),
                static=True,
            )

        for frame_index, point in enumerate(episode.timeseries):
            rec.set_time(TIMELINE, duration=float(point.t))
            rec.set_time("frame", sequence=frame_index)
            _log_pose(rec, point)

        rec.flush()
        return path.read_bytes()
    finally:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def _log_static_scene(rec: rr.RecordingStream, episode: Episode) -> None:
    blueprint = rrb.Grid(
        rrb.Spatial3DView(
            name="SO-101 trajectory",
            origin="world",
            contents=["world/**"],
        )
    )
    rec.send_blueprint(blueprint)
    rec.log("world", rr.ViewCoordinates.RIGHT_HAND_Y_UP, static=True)

    rec.log(
        "world/robot/base",
        rr.Boxes3D(
            centers=[[0.0, 0.025, 0.0]],
            sizes=[[0.12, 0.05, 0.12]],
            colors=[[31, 41, 55, 255]],
            labels=["base"],
        ),
        static=True,
    )

    for name, (length, color) in LINK_SPECS.items():
        rec.log(
            f"world/robot/{name}",
            rr.Boxes3D(
                centers=[[length / 2.0, 0.0, 0.0]],
                sizes=[[length, 0.032, 0.036]],
                colors=[color],
                labels=[name],
            ),
            static=True,
        )

    for name, color, radius in [
        ("pan_joint", [34, 211, 238, 255], 0.03),
        ("shoulder_joint", [167, 139, 250, 255], 0.028),
        ("elbow_joint", [52, 211, 153, 255], 0.024),
        ("wrist_joint", [248, 113, 113, 255], 0.021),
    ]:
        rec.log(
            f"world/robot/{name}",
            rr.Points3D([[0.0, 0.0, 0.0]], colors=[color], radii=[radius]),
            static=True,
        )

    for name in ["left_finger", "right_finger"]:
        rec.log(
            f"world/robot/{name}",
            rr.Boxes3D(
                centers=[[0.02, 0.0, 0.0]],
                sizes=[[0.042, 0.01, 0.01]],
                colors=[[229, 231, 235, 255]],
                labels=[name],
            ),
            static=True,
        )

    rec.log(
        "world/metadata",
        rr.TextDocument(
            f"Dataset: {episode.dataset_id}\n"
            f"Trajectory: {episode.id}\n"
            f"Task: {episode.task or 'unlabeled'}\n"
            f"Frames: {len(episode.timeseries)}\n"
            f"Joint units: {episode.joint_units}",
            media_type=rr.MediaType.MARKDOWN,
        ),
        static=True,
    )


def _log_pose(rec: rr.RecordingStream, point: TimeseriesPoint) -> None:
    pose = _pose_from_joints(point.joints)
    for name in [
        "upper",
        "forearm",
        "wrist",
        "tool",
        "pan_joint",
        "shoulder_joint",
        "elbow_joint",
        "wrist_joint",
        "left_finger",
        "right_finger",
    ]:
        rec.log(f"world/robot/{name}", _transform_from_matrix(pose[name]))


def _pose_from_joints(joints: list[float]) -> dict[str, Matrix4]:
    pan = _deg_to_rad(joints[0] if len(joints) > 0 else 0.0)
    shoulder = _deg_to_rad((joints[1] if len(joints) > 1 else -70.0) + 92.0)
    elbow = _deg_to_rad((joints[2] if len(joints) > 2 else 70.0) - 68.0)
    wrist_flex = _deg_to_rad((joints[3] if len(joints) > 3 else 35.0) - 45.0)
    wrist_roll = _deg_to_rad(joints[4] if len(joints) > 4 else 0.0)
    gripper = joints[5] if len(joints) > 5 else 1.0

    root = _matmul(_translation_matrix((0.0, 0.06, 0.0)), _rotation_y(pan))
    shoulder_origin = _matmul(root, _translation_matrix((0.0, 0.035, 0.0)))
    shoulder_frame = _matmul(shoulder_origin, _rotation_z(shoulder))
    elbow_origin = _matmul(shoulder_frame, _translation_matrix((LINK_LENGTHS["upper"], 0.0, 0.0)))
    elbow_frame = _matmul(elbow_origin, _rotation_z(elbow))
    wrist_origin = _matmul(elbow_frame, _translation_matrix((LINK_LENGTHS["forearm"], 0.0, 0.0)))
    wrist_frame = _matmul(wrist_origin, _rotation_z(wrist_flex))
    tool_origin = _matmul(wrist_frame, _translation_matrix((LINK_LENGTHS["wrist"], 0.0, 0.0)))
    tool_frame = _matmul(tool_origin, _rotation_x(wrist_roll))
    gripper_origin = _matmul(tool_frame, _translation_matrix((LINK_LENGTHS["tool"], 0.0, 0.0)))

    opening = 0.014 + _clamp((gripper - 0.8) / 4.8, 0.0, 1.0) * 0.048

    return {
        "upper": shoulder_frame,
        "forearm": elbow_frame,
        "wrist": wrist_frame,
        "tool": tool_frame,
        "pan_joint": root,
        "shoulder_joint": shoulder_origin,
        "elbow_joint": elbow_origin,
        "wrist_joint": wrist_origin,
        "gripper": gripper_origin,
        "left_finger": _matmul(gripper_origin, _translation_matrix((0.0, 0.0, opening))),
        "right_finger": _matmul(gripper_origin, _translation_matrix((0.0, 0.0, -opening))),
    }


def _transform_from_matrix(matrix: Matrix4) -> rr.Transform3D:
    return rr.Transform3D(
        translation=_translation(matrix),
        quaternion=_quaternion_from_matrix(matrix),
    )


def _deg_to_rad(value: float) -> float:
    return value * math.pi / 180.0


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _identity() -> Matrix4:
    return (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )


def _translation_matrix(v: Vec3) -> Matrix4:
    m = [list(row) for row in _identity()]
    m[0][3], m[1][3], m[2][3] = v
    return tuple(tuple(row) for row in m)


def _rotation_x(angle: float) -> Matrix4:
    c = math.cos(angle)
    s = math.sin(angle)
    return (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, c, -s, 0.0),
        (0.0, s, c, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )


def _rotation_y(angle: float) -> Matrix4:
    c = math.cos(angle)
    s = math.sin(angle)
    return (
        (c, 0.0, s, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (-s, 0.0, c, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )


def _rotation_z(angle: float) -> Matrix4:
    c = math.cos(angle)
    s = math.sin(angle)
    return (
        (c, -s, 0.0, 0.0),
        (s, c, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )


def _matmul(a: Matrix4, b: Matrix4) -> Matrix4:
    return tuple(
        tuple(sum(a[row][k] * b[k][col] for k in range(4)) for col in range(4))
        for row in range(4)
    )


def _translation(matrix: Matrix4) -> Vec3:
    return (matrix[0][3], matrix[1][3], matrix[2][3])


def _quaternion_from_matrix(matrix: Matrix4) -> tuple[float, float, float, float]:
    m00, m01, m02 = matrix[0][0], matrix[0][1], matrix[0][2]
    m10, m11, m12 = matrix[1][0], matrix[1][1], matrix[1][2]
    m20, m21, m22 = matrix[2][0], matrix[2][1], matrix[2][2]
    trace = m00 + m11 + m22

    if trace > 0.0:
        s = math.sqrt(trace + 1.0) * 2.0
        w = 0.25 * s
        x = (m21 - m12) / s
        y = (m02 - m20) / s
        z = (m10 - m01) / s
    elif m00 > m11 and m00 > m22:
        s = math.sqrt(1.0 + m00 - m11 - m22) * 2.0
        w = (m21 - m12) / s
        x = 0.25 * s
        y = (m01 + m10) / s
        z = (m02 + m20) / s
    elif m11 > m22:
        s = math.sqrt(1.0 + m11 - m00 - m22) * 2.0
        w = (m02 - m20) / s
        x = (m01 + m10) / s
        y = 0.25 * s
        z = (m12 + m21) / s
    else:
        s = math.sqrt(1.0 + m22 - m00 - m11) * 2.0
        w = (m10 - m01) / s
        x = (m02 + m20) / s
        y = (m12 + m21) / s
        z = 0.25 * s

    return (x, y, z, w)
