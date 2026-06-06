from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


SessionState = Literal["idle", "recording", "captioning", "saved", "error"]
AugmentationStatus = Literal["raw", "augmented", "fine-tuned"]


class Session(BaseModel):
    id: str
    task: str
    robot: str
    operator: str
    dataset_id: str
    state: SessionState = "idle"
    started_at: str = ""
    episode_count: int = 0


class Caption(BaseModel):
    t_start: float
    t_end: float
    text: str
    confidence: float = 0.0


class TimeseriesPoint(BaseModel):
    t: float
    joints: list[float] = Field(default_factory=list, description="6 joint values for SO-101")
    gripper: float = 0.0
    ee_xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)


class EpisodeSummary(BaseModel):
    id: str
    dataset_id: str
    title: str
    duration_s: float
    frame_count: int
    thumbnail: str = ""
    task: str = ""
    video_start_s: float = 0.0
    video_end_s: float = 0.0


class Episode(EpisodeSummary):
    captions: list[Caption] = []
    timeseries: list[TimeseriesPoint] = []
    joint_names: list[str] = []
    joint_units: str = "degrees"


class Dataset(BaseModel):
    id: str
    name: str
    description: str
    domain: str
    robot: str
    episode_count: int
    frame_count: int
    augmentation_status: AugmentationStatus
    size_mb: float
    price_usd: float
    cover_image: str = ""
    updated_at: str = ""


class DatasetDetail(Dataset):
    episodes: list[EpisodeSummary] = []


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    session_id: Optional[str] = None
    dataset_id: Optional[str] = None
    episode_id: Optional[str] = None


class CaptionStreamRequest(BaseModel):
    session_id: str


class LeRobotInfo(BaseModel):
    robot_type: str
    fps: int
    joint_names: list[str]
    total_episodes: int
    total_frames: int
    tasks: list[str]
    video_key: str


class LeRobotEpisodeSummary(BaseModel):
    episode_index: int
    task: str
    length_frames: int
    duration_s: float


class LeRobotEpisodeData(BaseModel):
    episode_index: int
    task: str
    length_frames: int
    fps: int
    joint_names: list[str]
    video_from_s: float
    video_to_s: float
    action: list[list[float]]
    state: list[list[float]]
