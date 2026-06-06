from abc import ABC, abstractmethod
from pathlib import Path

import torch
from lerobot.policies.factory import make_pre_post_processors
from omegaconf import DictConfig

JOINT_NAMES = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
]


class Policy(ABC):
    def load(self, pretrained_path: str, device: str) -> None:
        if not Path(pretrained_path).exists():
            raise FileNotFoundError(f"Checkpoint not found: {pretrained_path}")
        self._device = device
        self._policy = self._policy_class().from_pretrained(pretrained_name_or_path=pretrained_path)
        self._policy.to(device)
        self._policy.eval()
        device_override = {"device_processor": {"device": device}}
        self._pre, self._post = make_pre_post_processors(
            policy_cfg=self._policy.config,
            pretrained_path=pretrained_path,
            preprocessor_overrides=device_override,
            postprocessor_overrides=device_override,
        )

    @abstractmethod
    def _policy_class(self): ...

    @abstractmethod
    def _make_batch(self, raw_obs: dict) -> dict: ...

    def reset(self) -> None:
        self._policy.reset()

    def step(self, raw_obs: dict) -> dict:
        batch = self._pre(self._make_batch(raw_obs))
        batch = {k: v.to(self._device) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}
        with torch.inference_mode():
            action = self._post(self._policy.select_action(batch))
        action = action.squeeze()
        return {f"{j}.pos": action[i].item() for i, j in enumerate(JOINT_NAMES)}


class ACTPolicy(Policy):
    def _policy_class(self):
        from lerobot.policies.act.modeling_act import ACTPolicy as _ACT
        return _ACT

    def _make_batch(self, raw_obs: dict) -> dict:
        state = torch.tensor(
            [raw_obs[f"{j}.pos"] for j in JOINT_NAMES], dtype=torch.float32
        ).unsqueeze(0)
        img = torch.from_numpy(raw_obs["wrist_cam"]).permute(2, 0, 1).float().unsqueeze(0) / 255.0
        return {"observation.images.wrist_cam": img, "observation.state": state}


class SmolVLAPolicy(Policy):
    task: str = ""

    def _policy_class(self):
        from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy as _SmolVLA
        return _SmolVLA

    def _make_batch(self, raw_obs: dict) -> dict:
        state = torch.tensor(
            [raw_obs[f"{j}.pos"] for j in JOINT_NAMES], dtype=torch.float32
        ).unsqueeze(0)
        img = torch.from_numpy(raw_obs["wrist_cam"]).permute(2, 0, 1).float().unsqueeze(0) / 255.0
        image_keys = list(self._policy.config.image_features.keys())
        batch = {"observation.state": state, "task": [self.task]}
        for i, key in enumerate(image_keys):
            if i == 0:
                batch[key] = img
            else:
                batch[key] = torch.zeros_like(img)
                batch[f"{key}_padding_mask"] = torch.zeros(1, dtype=torch.bool)
        return batch


def make_policy(cfg: DictConfig) -> Policy:
    policy = ACTPolicy() if cfg.deploy.policy_type == "act" else SmolVLAPolicy()
    policy.load(cfg.deploy.pretrained_path, cfg.deploy.device)
    return policy


def make_policy_config(policy_type: str):
    from lerobot.policies.act.configuration_act import ACTConfig
    from lerobot.policies.smolvla.configuration_smolvla import SmolVLAConfig

    if policy_type.lower() == "smolvla":
        return SmolVLAConfig(push_to_hub=False)
    return ACTConfig(push_to_hub=False)
