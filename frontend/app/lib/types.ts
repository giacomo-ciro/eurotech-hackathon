export type Patient = {
  id: string;
  name: string;
  name_zh: string | null;
  age: number;
  sex: string;
  language: string;
  languages: string[];
  allergies: string[];
  notes: string;
};

export type Medicine = {
  drug_id: number;
  drug_name: string;
  generic_name: string;
  drug_class: string;
  indications: string;
  dosage_form: string;
  strength: string;
  route_of_administration: string;
  mechanism_of_action: string;
  side_effects: string;
  contraindications: string;
  interactions_text: string;
  warnings_and_precautions: string;
  pregnancy_category: string;
  storage_conditions: string;
  manufacturer: string;
  approval_date: string;
  availability: string;
  ndc: string;
  price: string;
};

export type Prescription = {
  id: string;
  patient_id: string;
  drug_id: number;
  tray: "morning" | "lunch" | "dinner" | "review";
  quantity: number;
  instructions: string;
  prescriber: string;
};

export type ActivePrescription = {
  prescription_id: string;
  stage: "idle" | "scanning" | "identified" | "picking" | "placed" | "done" | "error";
  vision_confidence: number;
  match: boolean;
  updated_at: string;
};

export type ActivePrescriptionDetail = {
  active: ActivePrescription;
  prescription: Prescription;
  patient: Patient;
  medicine: Medicine;
};

export type Interaction = {
  drug_1: string;
  drug_2: string;
  description: string;
  source: "common" | "exhaustive";
};

export type RobotStateEvent = {
  stage: string;
  detail?: string;
  progress?: number;
  drug_id?: number;
  drug_name?: string;
  tray?: string;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};
