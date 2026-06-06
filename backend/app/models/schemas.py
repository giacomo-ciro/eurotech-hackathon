from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class Patient(BaseModel):
    id: str
    name: str
    name_zh: Optional[str] = None
    age: int
    sex: str
    language: str
    languages: list[str]
    allergies: list[str]
    notes: str = ""


class Medicine(BaseModel):
    drug_id: int
    drug_name: str
    generic_name: str
    drug_class: str
    indications: str
    dosage_form: str
    strength: str
    route_of_administration: str
    mechanism_of_action: str
    side_effects: str
    contraindications: str
    interactions_text: str = Field(
        default="",
        description="Free-text interaction column from the source catalog.",
    )
    warnings_and_precautions: str
    pregnancy_category: str
    storage_conditions: str
    manufacturer: str
    approval_date: str
    availability: str
    ndc: str
    price: str


class Interaction(BaseModel):
    drug_1: str
    drug_2: str
    description: str
    source: Literal["common", "exhaustive"] = "common"


class Prescription(BaseModel):
    id: str
    patient_id: str
    drug_id: int
    tray: Literal["morning", "lunch", "dinner", "review"]
    quantity: int = 1
    instructions: str = ""
    prescriber: str = ""


class ActivePrescription(BaseModel):
    prescription_id: str
    stage: Literal["idle", "scanning", "identified", "picking", "placed", "done", "error"] = "idle"
    vision_confidence: float = 0.0
    match: bool = False
    updated_at: str = ""


class ActivePrescriptionDetail(BaseModel):
    active: ActivePrescription
    prescription: Prescription
    patient: Patient
    medicine: Medicine


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    drug_id: int
    messages: list[ChatMessage]


class RobotStateEvent(BaseModel):
    stage: str
    detail: str = ""
    progress: float = 0.0
