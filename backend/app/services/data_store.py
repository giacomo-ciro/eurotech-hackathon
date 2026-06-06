from __future__ import annotations

import csv
import json
from pathlib import Path
from threading import Lock
from typing import Iterator, Optional

from .. import config
from ..models.schemas import (
    ActivePrescription,
    Interaction,
    Medicine,
    Patient,
    Prescription,
)


_CSV_TO_MODEL = {
    "Drug ID": "drug_id",
    "Drug Name": "drug_name",
    "Generic Name": "generic_name",
    "Drug Class": "drug_class",
    "Indications": "indications",
    "Dosage Form": "dosage_form",
    "Strength": "strength",
    "Route of Administration": "route_of_administration",
    "Mechanism of Action": "mechanism_of_action",
    "Side Effects": "side_effects",
    "Contraindications": "contraindications",
    "Interactions": "interactions_text",
    "Warnings and Precautions": "warnings_and_precautions",
    "Pregnancy Category": "pregnancy_category",
    "Storage Conditions": "storage_conditions",
    "Manufacturer": "manufacturer",
    "Approval Date": "approval_date",
    "Availability": "availability",
    "NDC": "ndc",
    "Price": "price",
}


def _row_to_medicine(row: dict[str, str]) -> Optional[Medicine]:
    try:
        drug_id = int(row["Drug ID"])
    except (KeyError, ValueError):
        return None
    payload: dict[str, object] = {"drug_id": drug_id}
    for csv_col, model_field in _CSV_TO_MODEL.items():
        if model_field == "drug_id":
            continue
        payload[model_field] = (row.get(csv_col) or "").strip()
    return Medicine(**payload)


def _load_catalog(path: Path) -> tuple[dict[int, Medicine], dict[str, int]]:
    by_id: dict[int, Medicine] = {}
    name_index: dict[str, int] = {}
    if not path.exists():
        return by_id, name_index
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            medicine = _row_to_medicine(row)
            if medicine is None:
                continue
            by_id[medicine.drug_id] = medicine
            for raw in (medicine.drug_name, medicine.generic_name):
                key = raw.strip().lower()
                if key:
                    name_index.setdefault(key, medicine.drug_id)
    return by_id, name_index


def _load_common_interactions(path: Path) -> dict[str, list[Interaction]]:
    index: dict[str, list[Interaction]] = {}
    if not path.exists():
        return index
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            d1 = (row.get("Drug 1") or "").strip()
            d2 = (row.get("Drug 2") or "").strip()
            desc = (row.get("Interaction Description") or "").strip()
            if not d1 or not d2 or not desc:
                continue
            interaction = Interaction(drug_1=d1, drug_2=d2, description=desc, source="common")
            index.setdefault(d1.lower(), []).append(interaction)
            index.setdefault(d2.lower(), []).append(interaction)
    return index


def _stream_exhaustive(path: Path, needle: str, limit: int) -> list[Interaction]:
    if not path.exists() or not needle:
        return []
    needle_l = needle.lower()
    hits: list[Interaction] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            d1 = (row.get("Drug 1") or "").strip()
            d2 = (row.get("Drug 2") or "").strip()
            if d1.lower() == needle_l or d2.lower() == needle_l:
                desc = (row.get("Interaction Description") or "").strip()
                if desc:
                    hits.append(
                        Interaction(drug_1=d1, drug_2=d2, description=desc, source="exhaustive")
                    )
                    if len(hits) >= limit:
                        break
    return hits


class DataStore:
    def __init__(self) -> None:
        self._medicines: dict[int, Medicine] = {}
        self._name_index: dict[str, int] = {}
        self._common_interactions: dict[str, list[Interaction]] = {}
        self._patients: dict[str, Patient] = {}
        self._prescriptions: dict[str, Prescription] = {}
        self._active: Optional[ActivePrescription] = None
        self._active_mtime: float = 0.0
        self._lock = Lock()
        self._loaded = False

    def load(self) -> None:
        with self._lock:
            primary_by_id, primary_names = _load_catalog(config.PRIMARY_CATALOG_CSV)
            secondary_by_id, secondary_names = _load_catalog(config.SECONDARY_CATALOG_CSV)
            merged_by_id = {**secondary_by_id, **primary_by_id}
            merged_names = {**secondary_names, **primary_names}
            self._medicines = merged_by_id
            self._name_index = merged_names
            self._common_interactions = _load_common_interactions(
                config.COMMON_INTERACTIONS_CSV
            )
            self._patients = {p.id: p for p in self._load_patients()}
            self._prescriptions = {r.id: r for r in self._load_prescriptions()}
            self._refresh_active_locked(force=True)
            self._loaded = True

    def _load_patients(self) -> list[Patient]:
        if not config.PATIENTS_JSON.exists():
            return []
        data = json.loads(config.PATIENTS_JSON.read_text(encoding="utf-8"))
        return [Patient(**row) for row in data]

    def _load_prescriptions(self) -> list[Prescription]:
        if not config.PRESCRIPTIONS_JSON.exists():
            return []
        data = json.loads(config.PRESCRIPTIONS_JSON.read_text(encoding="utf-8"))
        return [Prescription(**row) for row in data]

    def _refresh_active_locked(self, *, force: bool = False) -> None:
        path = config.ACTIVE_JSON
        if not path.exists():
            self._active = None
            self._active_mtime = 0.0
            return
        mtime = path.stat().st_mtime
        if not force and mtime == self._active_mtime and self._active is not None:
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._active = ActivePrescription(**data)
            self._active_mtime = mtime
        except (json.JSONDecodeError, ValueError):
            return

    def patients(self) -> list[Patient]:
        return list(self._patients.values())

    def patient(self, patient_id: str) -> Optional[Patient]:
        return self._patients.get(patient_id)

    def medicine(self, drug_id: int) -> Optional[Medicine]:
        return self._medicines.get(drug_id)

    def medicine_by_name(self, name: str) -> Optional[Medicine]:
        drug_id = self._name_index.get(name.strip().lower())
        if drug_id is None:
            return None
        return self._medicines.get(drug_id)

    def medicines(self) -> Iterator[Medicine]:
        return iter(self._medicines.values())

    def prescription(self, prescription_id: str) -> Optional[Prescription]:
        return self._prescriptions.get(prescription_id)

    def active(self) -> Optional[ActivePrescription]:
        with self._lock:
            self._refresh_active_locked()
            return self._active

    def set_active_stage(
        self,
        stage: str,
        *,
        vision_confidence: Optional[float] = None,
        match: Optional[bool] = None,
        updated_at: Optional[str] = None,
    ) -> Optional[ActivePrescription]:
        with self._lock:
            self._refresh_active_locked()
            if self._active is None:
                return None
            updated = self._active.model_copy(
                update={
                    "stage": stage,
                    **(
                        {"vision_confidence": vision_confidence}
                        if vision_confidence is not None
                        else {}
                    ),
                    **({"match": match} if match is not None else {}),
                    **({"updated_at": updated_at} if updated_at else {}),
                }
            )
            self._active = updated
            try:
                config.ACTIVE_JSON.write_text(
                    json.dumps(updated.model_dump(), indent=2) + "\n",
                    encoding="utf-8",
                )
                self._active_mtime = config.ACTIVE_JSON.stat().st_mtime
            except OSError:
                pass
            return updated

    def interactions_for(self, drug_id: int, *, limit: int = 25) -> list[Interaction]:
        medicine = self.medicine(drug_id)
        if medicine is None:
            return []
        seen: set[tuple[str, str, str]] = set()
        results: list[Interaction] = []

        for name in (medicine.drug_name, medicine.generic_name):
            key = name.strip().lower()
            if not key:
                continue
            for interaction in self._common_interactions.get(key, []):
                marker = (interaction.drug_1, interaction.drug_2, interaction.description)
                if marker in seen:
                    continue
                seen.add(marker)
                results.append(interaction)
                if len(results) >= limit:
                    return results

        if not results:
            fallback = _stream_exhaustive(
                config.INTERACTIONS_TEXT_CSV, medicine.drug_name, limit
            )
            for interaction in fallback:
                marker = (interaction.drug_1, interaction.drug_2, interaction.description)
                if marker in seen:
                    continue
                seen.add(marker)
                results.append(interaction)
                if len(results) >= limit:
                    return results
        return results


_store = DataStore()


def get_store() -> DataStore:
    if not _store._loaded:
        _store.load()
    return _store
