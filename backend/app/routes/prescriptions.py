from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException

from ..models.schemas import ActivePrescriptionDetail
from ..services.data_store import get_store
from ..services.robot_proxy import get_robot_proxy


log = logging.getLogger("dispensr.prescriptions")
router = APIRouter(prefix="/api/prescriptions", tags=["prescriptions"])


@router.get("/active", response_model=ActivePrescriptionDetail)
def get_active() -> ActivePrescriptionDetail:
    store = get_store()
    active = store.active()
    if active is None:
        raise HTTPException(status_code=404, detail="No active prescription set")
    prescription = store.prescription(active.prescription_id)
    if prescription is None:
        raise HTTPException(
            status_code=500,
            detail=f"active.json references unknown prescription {active.prescription_id}",
        )
    patient = store.patient(prescription.patient_id)
    medicine = store.medicine(prescription.drug_id)
    if patient is None or medicine is None:
        raise HTTPException(
            status_code=500,
            detail="Active prescription references missing patient or medicine",
        )
    return ActivePrescriptionDetail(
        active=active,
        prescription=prescription,
        patient=patient,
        medicine=medicine,
    )


@router.post("/{prescription_id}/dispense")
async def dispense(prescription_id: str) -> dict[str, object]:
    store = get_store()
    prescription = store.prescription(prescription_id)
    if prescription is None:
        raise HTTPException(status_code=404, detail=f"Prescription {prescription_id} not found")
    medicine = store.medicine(prescription.drug_id)
    if medicine is None:
        raise HTTPException(status_code=500, detail="Prescription drug missing from catalog")

    store.set_active_stage(
        "scanning",
        updated_at=datetime.now(timezone.utc).isoformat(),
    )

    payload = {
        "prescription_id": prescription.id,
        "drug_id": prescription.drug_id,
        "drug_name": medicine.drug_name,
        "tray": prescription.tray,
    }

    try:
        result = await get_robot_proxy().trigger_dispense(payload)
    except httpx.HTTPError as exc:
        store.set_active_stage(
            "error",
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        log.warning("robot-bridge dispense failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=f"robot-bridge unreachable: {exc}",
        ) from exc

    return {"ok": True, "bridge": result}
