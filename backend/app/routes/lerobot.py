from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..models.schemas import LeRobotEpisodeData, LeRobotEpisodeSummary, LeRobotInfo
from ..services.lerobot_store import get_lerobot_store


router = APIRouter(prefix="/api/lerobot", tags=["lerobot"])


@router.get("/info", response_model=LeRobotInfo)
def get_info() -> LeRobotInfo:
    info = get_lerobot_store().info()
    if info is None:
        raise HTTPException(status_code=404, detail="LeRobot dataset not present at data/data/")
    return info


@router.get("/episodes", response_model=list[LeRobotEpisodeSummary])
def list_episodes() -> list[LeRobotEpisodeSummary]:
    return get_lerobot_store().summaries()


@router.get("/episodes/{episode_index}", response_model=LeRobotEpisodeData)
def get_episode(episode_index: int) -> LeRobotEpisodeData:
    episode = get_lerobot_store().episode(episode_index)
    if episode is None:
        raise HTTPException(status_code=404, detail=f"Episode {episode_index} not found")
    return episode


@router.get("/episodes/{episode_index}/video")
def get_episode_video(episode_index: int) -> FileResponse:
    found = get_lerobot_store().episode_video_path(episode_index)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Video for episode {episode_index} not found")
    path, _from_s, _to_s = found
    return FileResponse(path, media_type="video/mp4", filename=path.name)
