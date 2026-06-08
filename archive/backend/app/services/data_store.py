from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Optional

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

IMPORTED_LEROBOT_ID = "imported-lerobot"
LEROBOT_VIDEO_KEY = "observation.images.wrist_cam"


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


def _file_size_mb(paths: list[Path]) -> float:
    total = 0
    for path in paths:
        if path.is_file():
            total += path.stat().st_size
        elif path.is_dir():
            total += sum(p.stat().st_size for p in path.rglob("*") if p.is_file())
    return total / (1024 * 1024)


def _load_parquet_rows(paths: list[Path], columns: list[str] | None = None) -> list[dict[str, Any]]:
    import pyarrow.parquet as pq

    rows: list[dict[str, Any]] = []
    for path in sorted(paths):
        rows.extend(pq.read_table(path, columns=columns).to_pylist())
    return rows


def _load_lerobot_info(root: Path) -> Optional[dict[str, Any]]:
    info_path = root / "meta" / "info.json"
    if not info_path.exists():
        return None
    try:
        return json.loads(info_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _load_lerobot_tasks(root: Path) -> dict[int, str]:
    tasks_path = root / "meta" / "tasks.parquet"
    if not tasks_path.exists():
        return {}
    rows = _load_parquet_rows([tasks_path])
    tasks: dict[int, str] = {}
    for row in rows:
        name = row.get("__index_level_0__")
        task_index = row.get("task_index")
        if name is not None and task_index is not None:
            tasks[int(task_index)] = str(name)
    return tasks


def _load_lerobot_episode_rows(root: Path) -> dict[str, dict[str, Any]]:
    episode_files = sorted((root / "meta" / "episodes").glob("*/*.parquet"))
    if not episode_files:
        return {}
    rows = _load_parquet_rows(
        episode_files,
        columns=[
            "episode_index",
            "tasks",
            "length",
            "data/chunk_index",
            "data/file_index",
            f"videos/{LEROBOT_VIDEO_KEY}/chunk_index",
            f"videos/{LEROBOT_VIDEO_KEY}/file_index",
            f"videos/{LEROBOT_VIDEO_KEY}/from_timestamp",
            f"videos/{LEROBOT_VIDEO_KEY}/to_timestamp",
        ],
    )
    return {str(row["episode_index"]): row for row in sorted(rows, key=lambda r: int(r["episode_index"]))}


def _make_lerobot_dataset(root: Path, info: dict[str, Any]) -> Dataset:
    updated = datetime.fromtimestamp((root / "meta" / "info.json").stat().st_mtime, tz=timezone.utc)
    return Dataset(
        id=IMPORTED_LEROBOT_ID,
        name="Imported SO-101 Trajectories",
        description="Kinematic replay dataset imported from LeRobot parquet robot trajectories.",
        domain="Lab robotics",
        robot=str(info.get("robot_type", "so_follower")).replace("_", "-"),
        episode_count=int(info.get("total_episodes", 0)),
        frame_count=int(info.get("total_frames", 0)),
        augmentation_status="raw",
        size_mb=_file_size_mb([root / "meta", root / "data", root / "videos"]),
        price_usd=0.0,
        cover_image="generated",
        updated_at=updated.isoformat(),
    )


def _lerobot_joint_names(info: dict[str, Any]) -> list[str]:
    features = info.get("features", {})
    state = features.get("observation.state", {})
    names = state.get("names", [])
    return [str(name) for name in names]


def _lerobot_episode_summary(row: dict[str, Any], dataset_id: str, fps: int) -> EpisodeSummary:
    episode_id = str(row["episode_index"])
    tasks = row.get("tasks") or []
    task = str(tasks[0]) if tasks else ""
    length = int(row.get("length") or 0)
    video_start = float(row.get(f"videos/{LEROBOT_VIDEO_KEY}/from_timestamp") or 0.0)
    video_end = float(row.get(f"videos/{LEROBOT_VIDEO_KEY}/to_timestamp") or 0.0)
    return EpisodeSummary(
        id=episode_id,
        dataset_id=dataset_id,
        title=f"Episode {episode_id} · {task or 'unlabeled'}",
        duration_s=length / fps if fps > 0 else max(0.0, video_end - video_start),
        frame_count=length,
        thumbnail="",
        task=task,
        video_start_s=video_start,
        video_end_s=video_end,
    )


class DataStore:
    def __init__(self) -> None:
        self._datasets: dict[str, Dataset] = {}
        self._episode_ids: dict[str, list[str]] = {}
        self._lerobot_info: dict[str, Any] | None = None
        self._lerobot_tasks: dict[int, str] = {}
        self._lerobot_episode_rows: dict[str, dict[str, Any]] = {}
        self._active: Optional[Session] = None
        self._active_mtime: float = 0.0
        self._lock = Lock()
        self._loaded = False

    def load(self) -> None:
        with self._lock:
            self._datasets = {}
            self._episode_ids = {}
            self._lerobot_info = None
            self._lerobot_tasks = {}
            self._lerobot_episode_rows = {}
            if config.DATASETS_DIR.exists():
                for child in sorted(config.DATASETS_DIR.iterdir()):
                    manifest = child / "manifest.json"
                    dataset = _load_manifest(manifest)
                    if dataset is None:
                        continue
                    self._datasets[dataset.id] = dataset
                    self._episode_ids[dataset.id] = _load_dataset_episode_ids(manifest)
            lerobot_info = _load_lerobot_info(config.DATA_DIR)
            if lerobot_info is not None:
                self._lerobot_info = lerobot_info
                self._lerobot_tasks = _load_lerobot_tasks(config.DATA_DIR)
                self._lerobot_episode_rows = _load_lerobot_episode_rows(config.DATA_DIR)
                if self._lerobot_episode_rows:
                    dataset = _make_lerobot_dataset(config.DATA_DIR, lerobot_info)
                    if not dataset.episode_count:
                        dataset = dataset.model_copy(update={"episode_count": len(self._lerobot_episode_rows)})
                    self._datasets[dataset.id] = dataset
                    self._episode_ids[dataset.id] = list(self._lerobot_episode_rows)
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
        if dataset_id == IMPORTED_LEROBOT_ID and self._lerobot_info is not None:
            fps = int(self._lerobot_info.get("fps") or 30)
            episodes = [
                _lerobot_episode_summary(row, dataset_id, fps)
                for row in self._lerobot_episode_rows.values()
            ]
            return DatasetDetail(**dataset.model_dump(), episodes=episodes)

        dataset_dir = config.DATASETS_DIR / dataset_id
        episodes: list[EpisodeSummary] = []
        for ep_id in self._episode_ids.get(dataset_id, []):
            ep = _load_episode_metadata(dataset_dir, ep_id)
            if ep is not None:
                episodes.append(ep)
        return DatasetDetail(**dataset.model_dump(), episodes=episodes)

    def episode(self, dataset_id: str, episode_id: str) -> Optional[Episode]:
        if dataset_id not in self._datasets or episode_id not in self._episode_ids.get(dataset_id, []):
            return None
        if dataset_id == IMPORTED_LEROBOT_ID:
            return self._lerobot_episode(episode_id)

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
        if dataset_id not in self._datasets or episode_id not in self._episode_ids.get(dataset_id, []):
            return None
        if dataset_id == IMPORTED_LEROBOT_ID:
            row = self._lerobot_episode_rows.get(episode_id)
            if row is None:
                return None
            video_chunk = int(row.get(f"videos/{LEROBOT_VIDEO_KEY}/chunk_index") or 0)
            video_file = int(row.get(f"videos/{LEROBOT_VIDEO_KEY}/file_index") or 0)
            path = (
                config.DATA_DIR
                / "videos"
                / LEROBOT_VIDEO_KEY
                / f"chunk-{video_chunk:03d}"
                / f"file-{video_file:03d}.mp4"
            )
            return path if path.exists() else None

        path = config.DATASETS_DIR / dataset_id / "episodes" / episode_id / "video.mp4"
        if not path.exists():
            return None
        return path

    def cover_path(self, dataset_id: str) -> Optional[Path]:
        dataset = self.dataset(dataset_id)
        if dataset is None:
            return None
        if dataset_id == IMPORTED_LEROBOT_ID:
            return None
        candidate = config.DATASETS_DIR / dataset_id / (dataset.cover_image or "cover.svg")
        if not candidate.exists():
            return None
        return candidate

    def is_generated_cover(self, dataset_id: str) -> bool:
        return dataset_id == IMPORTED_LEROBOT_ID and dataset_id in self._datasets

    def _lerobot_episode(self, episode_id: str) -> Optional[Episode]:
        if self._lerobot_info is None:
            return None
        row = self._lerobot_episode_rows.get(episode_id)
        if row is None:
            return None

        import pyarrow.compute as pc
        import pyarrow.parquet as pq

        fps = int(self._lerobot_info.get("fps") or 30)
        summary = _lerobot_episode_summary(row, IMPORTED_LEROBOT_ID, fps)
        data_chunk = int(row.get("data/chunk_index") or 0)
        data_file = int(row.get("data/file_index") or 0)
        data_path = config.DATA_DIR / "data" / f"chunk-{data_chunk:03d}" / f"file-{data_file:03d}.parquet"
        if not data_path.exists():
            return None

        table = pq.read_table(
            data_path,
            columns=["episode_index", "timestamp", "observation.state"],
        )
        filtered = table.filter(pc.equal(table["episode_index"], int(episode_id)))
        rows = filtered.to_pylist()
        points = []
        for frame in rows:
            joints = [float(v) for v in frame["observation.state"]]
            points.append(
                TimeseriesPoint(
                    t=float(frame["timestamp"]),
                    joints=joints,
                    gripper=joints[5] if len(joints) > 5 else 0.0,
                    ee_xyz=(0.0, 0.0, 0.0),
                )
            )

        return Episode(
            **summary.model_dump(),
            captions=[],
            timeseries=points,
            joint_names=_lerobot_joint_names(self._lerobot_info),
            joint_units="degrees",
        )

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
