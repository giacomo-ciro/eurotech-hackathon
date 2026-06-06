from __future__ import annotations

import csv
import json
from pathlib import Path
from threading import Lock
from typing import Optional

from .. import config
from ..models.schemas import (
    Caption,
    Dataset,
    DatasetDetail,
    Episode,
    EpisodeSummary,
    Session,
    TimeseriesPoint,
)


def _load_manifest(path: Path) -> Optional[Dataset]:
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw.pop("episodes", None)
    return Dataset(**raw)


def _load_dataset_episode_ids(manifest_path: Path) -> list[str]:
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    return list(raw.get("episodes", []))


def _load_episode_metadata(dataset_dir: Path, episode_id: str) -> Optional[EpisodeSummary]:
    meta_path = dataset_dir / "episodes" / episode_id / "metadata.json"
    if not meta_path.exists():
        return None
    raw = json.loads(meta_path.read_text(encoding="utf-8"))
    return EpisodeSummary(
        id=raw["id"],
        dataset_id=dataset_dir.name,
        title=raw.get("title", ""),
        duration_s=float(raw.get("duration_s", 0.0)),
        frame_count=int(raw.get("frame_count", 0)),
        thumbnail=raw.get("thumbnail", ""),
    )


def _load_captions(path: Path) -> list[Caption]:
    if not path.exists():
        return []
    return [Caption(**row) for row in json.loads(path.read_text(encoding="utf-8"))]


def _load_timeseries(path: Path) -> list[TimeseriesPoint]:
    if not path.exists():
        return []
    rows: list[TimeseriesPoint] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                rows.append(
                    TimeseriesPoint(
                        t=float(row["t"]),
                        joints=[float(row[f"j{i}"]) for i in range(6)],
                        gripper=float(row["gripper"]),
                        ee_xyz=(
                            float(row["ee_x"]),
                            float(row["ee_y"]),
                            float(row["ee_z"]),
                        ),
                    )
                )
            except (KeyError, ValueError):
                continue
    return rows


class DataStore:
    def __init__(self) -> None:
        self._datasets: dict[str, Dataset] = {}
        self._episode_ids: dict[str, list[str]] = {}
        self._active: Optional[Session] = None
        self._active_mtime: float = 0.0
        self._lock = Lock()
        self._loaded = False

    def load(self) -> None:
        with self._lock:
            self._datasets = {}
            self._episode_ids = {}
            if config.DATASETS_DIR.exists():
                for child in sorted(config.DATASETS_DIR.iterdir()):
                    manifest = child / "manifest.json"
                    dataset = _load_manifest(manifest)
                    if dataset is None:
                        continue
                    self._datasets[dataset.id] = dataset
                    self._episode_ids[dataset.id] = _load_dataset_episode_ids(manifest)
            self._refresh_active_locked(force=True)
            self._loaded = True

    def datasets(self) -> list[Dataset]:
        return list(self._datasets.values())

    def dataset(self, dataset_id: str) -> Optional[Dataset]:
        return self._datasets.get(dataset_id)

    def dataset_detail(self, dataset_id: str) -> Optional[DatasetDetail]:
        dataset = self.dataset(dataset_id)
        if dataset is None:
            return None
        dataset_dir = config.DATASETS_DIR / dataset_id
        episodes: list[EpisodeSummary] = []
        for ep_id in self._episode_ids.get(dataset_id, []):
            ep = _load_episode_metadata(dataset_dir, ep_id)
            if ep is not None:
                episodes.append(ep)
        return DatasetDetail(**dataset.model_dump(), episodes=episodes)

    def episode(self, dataset_id: str, episode_id: str) -> Optional[Episode]:
        dataset_dir = config.DATASETS_DIR / dataset_id
        summary = _load_episode_metadata(dataset_dir, episode_id)
        if summary is None:
            return None
        ep_dir = dataset_dir / "episodes" / episode_id
        return Episode(
            **summary.model_dump(),
            captions=_load_captions(ep_dir / "captions.json"),
            timeseries=_load_timeseries(ep_dir / "timeseries.csv"),
        )

    def episode_video_path(self, dataset_id: str, episode_id: str) -> Optional[Path]:
        path = config.DATASETS_DIR / dataset_id / "episodes" / episode_id / "video.mp4"
        if not path.exists():
            return None
        return path

    def cover_path(self, dataset_id: str) -> Optional[Path]:
        dataset = self.dataset(dataset_id)
        if dataset is None:
            return None
        candidate = config.DATASETS_DIR / dataset_id / (dataset.cover_image or "cover.svg")
        if not candidate.exists():
            return None
        return candidate

    def _refresh_active_locked(self, *, force: bool = False) -> None:
        path = config.ACTIVE_SESSION_JSON
        if not path.exists():
            self._active = None
            self._active_mtime = 0.0
            return
        mtime = path.stat().st_mtime
        if not force and mtime == self._active_mtime and self._active is not None:
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._active = Session(**data)
            self._active_mtime = mtime
        except (json.JSONDecodeError, ValueError):
            return

    def active_session(self) -> Optional[Session]:
        with self._lock:
            self._refresh_active_locked()
            return self._active

    def set_session_state(self, state: str, *, episode_count: Optional[int] = None) -> Optional[Session]:
        with self._lock:
            self._refresh_active_locked()
            if self._active is None:
                return None
            updates: dict[str, object] = {"state": state}
            if episode_count is not None:
                updates["episode_count"] = episode_count
            updated = self._active.model_copy(update=updates)
            self._active = updated
            try:
                config.ACTIVE_SESSION_JSON.write_text(
                    json.dumps(updated.model_dump(), indent=2) + "\n",
                    encoding="utf-8",
                )
                self._active_mtime = config.ACTIVE_SESSION_JSON.stat().st_mtime
            except OSError:
                pass
            return updated


_store = DataStore()


def get_store() -> DataStore:
    if not _store._loaded:
        _store.load()
    return _store
