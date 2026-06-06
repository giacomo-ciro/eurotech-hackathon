#!/usr/bin/env bash
# Run SmolVLA inference on a real SO-101 follower arm.
# Usage: ./run_smolvla.sh [OPTIONS]
#
# Required env vars (or edit defaults below):
#   FOLLOWER_PORT   e.g. /dev/ttyACM0
#   LEADER_PORT     e.g. /dev/ttyACM1  (only needed with --teleop)
#   HF_USER         your HuggingFace username
#   POLICY_REPO     HF repo of your fine-tuned model  (default: lerobot/smolvla_base)

set -euo pipefail

# ── Defaults (override via env or flags) ──────────────────────────────────────
FOLLOWER_PORT="${FOLLOWER_PORT:-/dev/ttyACM0}"
FOLLOWER_ID="${FOLLOWER_ID:-my_follower}"
LEADER_PORT="${LEADER_PORT:-/dev/ttyACM1}"
LEADER_ID="${LEADER_ID:-my_leader}"
HF_USER="${HF_USER:-$(huggingface-cli whoami 2>/dev/null | head -1 || echo 'your_hf_username')}"
POLICY_REPO="${POLICY_REPO:-lerobot/smolvla_base}"
TASK="${TASK:-Pick up the object and place it in the bin.}"
NUM_EPISODES="${NUM_EPISODES:-10}"
EPISODE_TIME_S="${EPISODE_TIME_S:-50}"
DATASET_NAME="${DATASET_NAME:-eval_smolvla_$(date +%Y%m%d_%H%M%S)}"

# Camera config — adjust index_or_path to match your setup.
# Use `lerobot-find-cameras opencv` to find the right indices.
CAMERAS="${CAMERAS:-{ front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30} }}"

# ── Flags ─────────────────────────────────────────────────────────────────────
USE_TELEOP=false
DISPLAY=true
PUSH_TO_HUB=false

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --follower-port PORT   Serial port for follower arm  (default: $FOLLOWER_PORT)
  --follower-id   ID     Robot ID for follower         (default: $FOLLOWER_ID)
  --leader-port   PORT   Serial port for leader arm    (default: $LEADER_PORT)
  --leader-id     ID     Robot ID for leader           (default: $LEADER_ID)
  --policy        REPO   HF model repo                 (default: $POLICY_REPO)
  --task          TEXT   Natural language task description
  --episodes      N      Number of eval episodes       (default: $NUM_EPISODES)
  --episode-time  S      Max seconds per episode       (default: $EPISODE_TIME_S)
  --dataset-name  NAME   Local/HF dataset name         (default: auto)
  --cameras       JSON   Camera config JSON string
  --teleop               Enable leader arm teleoperation between episodes
  --no-display           Disable Rerun visualisation
  --push                 Push eval dataset to HF Hub
  -h, --help             Show this help
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --follower-port) FOLLOWER_PORT="$2"; shift 2 ;;
    --follower-id)   FOLLOWER_ID="$2";   shift 2 ;;
    --leader-port)   LEADER_PORT="$2";   shift 2 ;;
    --leader-id)     LEADER_ID="$2";     shift 2 ;;
    --policy)        POLICY_REPO="$2";   shift 2 ;;
    --task)          TASK="$2";          shift 2 ;;
    --episodes)      NUM_EPISODES="$2";  shift 2 ;;
    --episode-time)  EPISODE_TIME_S="$2";shift 2 ;;
    --dataset-name)  DATASET_NAME="$2";  shift 2 ;;
    --cameras)       CAMERAS="$2";       shift 2 ;;
    --teleop)        USE_TELEOP=true;    shift ;;
    --no-display)    DISPLAY=false;      shift ;;
    --push)          PUSH_TO_HUB=true;   shift ;;
    -h|--help)       usage ;;
    *) echo "Unknown flag: $1" >&2; usage ;;
  esac
done

# ── Print config ──────────────────────────────────────────────────────────────
echo "════════════════════════════════════════════════"
echo "  SmolVLA inference"
echo "════════════════════════════════════════════════"
echo "  Policy      : $POLICY_REPO"
echo "  Follower    : $FOLLOWER_PORT  ($FOLLOWER_ID)"
echo "  Task        : $TASK"
echo "  Episodes    : $NUM_EPISODES  x  ${EPISODE_TIME_S}s"
echo "  Dataset     : ${HF_USER}/${DATASET_NAME}"
echo "  Teleop      : $USE_TELEOP"
echo "  Display     : $DISPLAY"
echo "  Push to Hub : $PUSH_TO_HUB"
echo "════════════════════════════════════════════════"
echo ""

# ── Build lerobot-record command ──────────────────────────────────────────────
CMD=(
  lerobot-record
  --robot.type=so101_follower
  "--robot.port=${FOLLOWER_PORT}"
  "--robot.id=${FOLLOWER_ID}"
  "--robot.cameras=${CAMERAS}"
  "--dataset.single_task=${TASK}"
  "--dataset.repo_id=${HF_USER}/${DATASET_NAME}"
  "--dataset.num_episodes=${NUM_EPISODES}"
  "--dataset.episode_time_s=${EPISODE_TIME_S}"
  --dataset.streaming_encoding=true
  --dataset.encoder_threads=2
  "--dataset.push_to_hub=${PUSH_TO_HUB}"
  "--policy.path=${POLICY_REPO}"
  "--display_data=${DISPLAY}"
)

if $USE_TELEOP; then
  CMD+=(
    --teleop.type=so101_leader
    "--teleop.port=${LEADER_PORT}"
    "--teleop.id=${LEADER_ID}"
  )
fi

echo "Running: ${CMD[*]}"
echo ""
exec "${CMD[@]}"
