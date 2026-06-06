from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Optional

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from .. import config
from ..models.schemas import (
    LeRobotEpisodeData,
    LeRobotEpisodeSummary,
    LeRobotInfo,
)


log = logging.getLogger("vla.lerobot_store")

VIDEO_KEY = "observation.images.wrist_cam"


@dataclass(frozen=True)
class _EpisodeIndex:
    episode_index: int
    task: str
    length: int
    data_chunk: int
    data_file: int
    data_from: int
    data_to: int
    video_chunk: int
    video_file: int
    video_from_s: float
    video_to_s: float


def _video_col(name: str) -> str:
    return f"videos/{VIDEO_KEY}/{name}"


class LeRobotStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._loaded = False
        self._root: Path = config.LEROBOT_DATASET_DIR
        self._info: Optional[LeRobotInfo] = None
        self._episodes: dict[int, _EpisodeIndex] = {}

    def available(self) -> bool:
        return (self._root / "meta" / "info.json").exists()

    def load(self) -> None:
        with self._lock:
            if not self.available():
                log.info("LeRobot dataset not present at %s", self._root)
                self._loaded = True
                return

            info_raw = json.loads((self._root / "meta" / "info.json").read_text(encoding="utf-8"))
            features = info_raw.get("features", {})
            joint_names = features.get("action", {}).get("names", [])

            tasks_table = pq.read_table(self._root / "meta" / "tasks.parquet")
            tasks_lookup: dict[int, str] = {}
            schema_names = tasks_table.schema.names
            string_col = next(
                (
                    n
                    for n in schema_names
                    if n != "task_index" and pa.types.is_string(tasks_table.schema.field(n).type)
                ),
                None,
            )
            if string_col is not None:
                idx_list = tasks_table.column("task_index").to_pylist()
                name_list = tasks_table.column(string_col).to_pylist()
                for i, name in zip(idx_list, name_list):
                    if i is None or name is None:
                        continue
                    tasks_lookup[int(i)] = str(name)

            episodes: dict[int, _EpisodeIndex] = {}
            meta_glob = sorted((self._root / "meta" / "episodes").rglob("file-*.parquet"))
            for path in meta_glob:
                table = pq.read_table(
                    path,
                    columns=[
                        "episode_index",
                        "tasks",
                        "length",
                        "data/chunk_index",
                        "data/file_index",
                        "dataset_from_index",
                        "dataset_to_index",
                        _video_col("chunk_index"),
                        _video_col("file_index"),
                        _video_col("from_timestamp"),
                        _video_col("to_timestamp"),
                    ],
                )
                df = table.to_pandas()
                for _, row in df.iterrows():
                    tasks_for_ep = row.get("tasks") or []
                    task_name = ""
                    if len(tasks_for_ep) > 0:
                        task_name = str(tasks_for_ep[0])
                    idx = int(row["episode_index"])
                    episodes[idx] = _EpisodeIndex(
                        episode_index=idx,
                        task=task_name,
                        length=int(row["length"]),
                        data_chunk=int(row["data/chunk_index"]),
                        data_file=int(row["data/file_index"]),
                        data_from=int(row["dataset_from_index"]),
                        data_to=int(row["dataset_to_index"]),
                        video_chunk=int(row[_video_col("chunk_index")]),
                        video_file=int(row[_video_col("file_index")]),
                        video_from_s=float(row[_video_col("from_timestamp")]),
                        video_to_s=float(row[_video_col("to_timestamp")]),
                    )

            self._episodes = dict(sorted(episodes.items()))
            self._info = LeRobotInfo(
                robot_type=info_raw.get("robot_type", "unknown"),
                fps=int(info_raw.get("fps", 30)),
                joint_names=list(joint_names),
                total_episodes=int(info_raw.get("total_episodes", len(self._episodes))),
                total_frames=int(info_raw.get("total_frames", 0)),
                tasks=list(dict.fromkeys(tasks_lookup.values())),
                video_key=VIDEO_KEY,
            )
            self._loaded = True
            log.info(
                "loaded LeRobot dataset: %d episodes, %d frames",
                len(self._episodes),
                self._info.total_frames,
            )

    def info(self) -> Optional[LeRobotInfo]:
        if not self._loaded:
            self.load()
        return self._info

    def summaries(self) -> list[LeRobotEpisodeSummary]:
        if not self._loaded:
            self.load()
        info = self._info
        fps = info.fps if info else 30
        return [
            LeRobotEpisodeSummary(
                episode_index=ep.episode_index,
                task=ep.task,
                length_frames=ep.length,
                duration_s=round(ep.length / fps, 3) if fps else 0.0,
            )
            for ep in self._episodes.values()
        ]

    def episode(self, episode_index: int) -> Optional[LeRobotEpisodeData]:
        if not self._loaded:
            self.load()
        ep = self._episodes.get(episode_index)
        info = self._info
        if ep is None or info is None:
            return None
        action, state = self._read_episode_arrays(ep)
        return LeRobotEpisodeData(
            episode_index=ep.episode_index,
            task=ep.task,
            length_frames=ep.length,
            fps=info.fps,
            joint_names=info.joint_names,
            video_from_s=ep.video_from_s,
            video_to_s=ep.video_to_s,
            action=action,
            state=state,
        )

    def episode_video_path(self, episode_index: int) -> Optional[tuple[Path, float, float]]:
        if not self._loaded:
            self.load()
        ep = self._episodes.get(episode_index)
        if ep is None:
            return None
        path = (
            self._root
            / "videos"
            / VIDEO_KEY
            / f"chunk-{ep.video_chunk:03d}"
            / f"file-{ep.video_file:03d}.mp4"
        )
        if not path.exists():
            return None
        return path, ep.video_from_s, ep.video_to_s

    def _read_episode_arrays(self, ep: _EpisodeIndex) -> tuple[list[list[float]], list[list[float]]]:
        path = (
            self._root
            / "data"
            / f"chunk-{ep.data_chunk:03d}"
            / f"file-{ep.data_file:03d}.parquet"
        )
        table = _read_data_table(path)
        mask = pc.equal(table.column("episode_index"), ep.episode_index)
        slice_t = table.filter(mask)
        action = [list(map(float, v)) for v in slice_t.column("action").to_pylist()]
        state = [list(map(float, v)) for v in slice_t.column("observation.state").to_pylist()]
        return action, state


@lru_cache(maxsize=8)
def _read_data_table(path: Path):
    return pq.read_table(
        path, columns=["episode_index", "action", "observation.state"]
    )


_store = LeRobotStore()


def get_lerobot_store() -> LeRobotStore:
    return _store
