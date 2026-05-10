from typing import Dict, Any, Tuple, List

class DataValidator:
    def __init__(self):
        self.required_fields = {
            "prescription_number", "patient_name", "drug_name", "day_supply",
            "total_amount", "drug_type", "brand_indicator", "daw", "origin",
            "prescriber_name", "status", "dispensing_date", "refill_auth",
            "order_date", "dob", "sex", "lot_number", "patient_type",
            "drug_class", "npi", "license", "340b_indicator", "quantity"
        }

    def validate_prescription_fields(self, fields: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        for rf in self.required_fields:
            if rf not in fields or not fields[rf]:
                errors.append(f"Missing required field: {rf}")
        return len(errors) == 0, errors

    def validate_composite_key(self, prescription_number: str, dispensing_date: str) -> bool:
        return bool(prescription_number and dispensing_date)
