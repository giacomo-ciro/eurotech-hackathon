export type SessionState =
  | "idle"
  | "recording"
  | "captioning"
  | "saved"
  | "error";

export type AugmentationStatus = "raw" | "augmented" | "fine-tuned";

export type Session = {
  id: string;
  task: string;
  robot: string;
  operator: string;
  dataset_id: string;
  state: SessionState;
  started_at: string;
  episode_count: number;
};

export type Dataset = {
  id: string;
  name: string;
  description: string;
  domain: string;
  robot: string;
  episode_count: number;
  frame_count: number;
  augmentation_status: AugmentationStatus;
  size_mb: number;
  price_usd: number;
  cover_image: string;
  updated_at: string;
};

export type EpisodeSummary = {
  id: string;
  dataset_id: string;
  title: string;
  duration_s: number;
  frame_count: number;
  thumbnail: string;
  task: string;
  video_start_s: number;
  video_end_s: number;
};

export type Caption = {
  t_start: number;
  t_end: number;
  text: string;
  confidence: number;
};

export type TimeseriesPoint = {
  t: number;
  joints: number[];
  gripper: number;
  ee_xyz: [number, number, number];
};

export type Episode = EpisodeSummary & {
  captions: Caption[];
  timeseries: TimeseriesPoint[];
  joint_names: string[];
  joint_units: string;
};

export type DatasetDetail = Dataset & { episodes: EpisodeSummary[] };

export type RobotStateEvent = {
  stage: string;
  detail?: string;
  progress?: number;
  session_id?: string;
  task?: string;
  robot?: string;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type LiveCaption = {
  t: number;
  text: string;
};
