from __future__ import annotations

import mimetypes

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..models.schemas import Dataset, DatasetDetail, Episode
from ..services.data_store import get_store


router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.get("", response_model=list[Dataset])
def list_datasets() -> list[Dataset]:
    return get_store().datasets()


@router.get("/{dataset_id}", response_model=DatasetDetail)
def get_dataset(dataset_id: str) -> DatasetDetail:
    detail = get_store().dataset_detail(dataset_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    return detail


@router.get("/{dataset_id}/cover")
def get_cover(dataset_id: str) -> FileResponse:
    path = get_store().cover_path(dataset_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Cover not found")
    media_type, _ = mimetypes.guess_type(path.name)
    return FileResponse(path, media_type=media_type or "application/octet-stream")


@router.get("/{dataset_id}/episodes/{episode_id}", response_model=Episode)
def get_episode(dataset_id: str, episode_id: str) -> Episode:
    episode = get_store().episode(dataset_id, episode_id)
    if episode is None:
        raise HTTPException(status_code=404, detail=f"Episode {episode_id} not found")
    return episode


@router.get("/{dataset_id}/episodes/{episode_id}/video")
def get_episode_video(dataset_id: str, episode_id: str) -> FileResponse:
    path = get_store().episode_video_path(dataset_id, episode_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path, media_type="video/mp4", filename=path.name)
