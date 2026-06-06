from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models.schemas import Patient
from ..services.data_store import get_store


router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("", response_model=list[Patient])
def list_patients() -> list[Patient]:
    return get_store().patients()


@router.get("/{patient_id}", response_model=Patient)
def get_patient(patient_id: str) -> Patient:
    patient = get_store().patient(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    return patient
