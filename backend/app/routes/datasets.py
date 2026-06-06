from __future__ import annotations

import mimetypes

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

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
def get_cover(dataset_id: str) -> Response:
    store = get_store()
    path = store.cover_path(dataset_id)
    if path is None:
        if store.is_generated_cover(dataset_id):
            svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675">
<rect width="1200" height="675" fill="#0b1220"/>
<rect x="80" y="80" width="1040" height="515" rx="28" fill="#111827" stroke="#1f2937" stroke-width="4"/>
<g transform="translate(330 128)" stroke-linecap="round" stroke-linejoin="round">
  <rect x="-70" y="354" width="600" height="36" rx="18" fill="#1f2937"/>
  <circle cx="40" cy="340" r="54" fill="#0f172a" stroke="#22d3ee" stroke-width="8"/>
  <path d="M40 340 L126 250 L242 252 L344 166 L424 208" fill="none" stroke="#22d3ee" stroke-width="34"/>
  <path d="M422 208 L478 186 M422 208 L474 238" stroke="#e5e7eb" stroke-width="16"/>
  <circle cx="126" cy="250" r="28" fill="#111827" stroke="#a78bfa" stroke-width="8"/>
  <circle cx="242" cy="252" r="28" fill="#111827" stroke="#34d399" stroke-width="8"/>
  <circle cx="344" cy="166" r="28" fill="#111827" stroke="#fbbf24" stroke-width="8"/>
</g>
<text x="80" y="605" fill="#e5e7eb" font-size="42" font-family="Arial, sans-serif" font-weight="700">SO-101 Digital Twin</text>
<text x="80" y="640" fill="#94a3b8" font-size="24" font-family="Arial, sans-serif">Kinematic replay from LeRobot trajectories</text>
</svg>"""
            return Response(content=svg, media_type="image/svg+xml")
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
