from typing import Optional, List
from datetime import date
from sqlalchemy import text
from sqlalchemy.orm import Session

class PrescriptionRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def store_or_update(self, prescription_data: dict) -> bool:
        """
        Stores a prescription record or updates it if (prescription_number, dispensing_date) exists.
        Uses PostgreSQL ON CONFLICT clause via SQLAlchemy's execute.
        """
        query = text("""
            INSERT INTO prescriptions (
                prescription_number, dispensing_date, patient_name, drug_name, 
                day_supply, total_amount, drug_type, brand_indicator, daw, 
                origin, prescriber_name, status, refill_auth, order_date, 
                dob, sex, lot_number, patient_type, drug_class, npi, license, 
                indicator_340b, quantity, original_email_path
            ) VALUES (
                :prescription_number, :dispensing_date, :patient_name, :drug_name, 
                :day_supply, :total_amount, :drug_type, :brand_indicator, :daw, 
                :origin, :prescriber_name, :status, :refill_auth, :order_date, 
                :dob, :sex, :lot_number, :patient_type, :drug_class, :npi, :license, 
                :indicator_340b, :quantity, :original_email_path
            )
            ON CONFLICT (prescription_number, dispensing_date) DO UPDATE SET
                patient_name = EXCLUDED.patient_name,
                drug_name = EXCLUDED.drug_name,
                day_supply = EXCLUDED.day_supply,
                total_amount = EXCLUDED.total_amount,
                drug_type = EXCLUDED.drug_type,
                brand_indicator = EXCLUDED.brand_indicator,
                daw = EXCLUDED.daw,
                origin = EXCLUDED.origin,
                prescriber_name = EXCLUDED.prescriber_name,
                status = EXCLUDED.status,
                refill_auth = EXCLUDED.refill_auth,
                order_date = EXCLUDED.order_date,
                dob = EXCLUDED.dob,
                sex = EXCLUDED.sex,
                lot_number = EXCLUDED.lot_number,
                patient_type = EXCLUDED.patient_type,
                drug_class = EXCLUDED.drug_class,
                npi = EXCLUDED.npi,
                license = EXCLUDED.license,
                indicator_340b = EXCLUDED.indicator_340b,
                quantity = EXCLUDED.quantity,
                original_email_path = EXCLUDED.original_email_path,
                extracted_at = CURRENT_TIMESTAMP;
        """)
        try:
            self.session.execute(query, prescription_data)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            raise

    def find_by_composite_key(self, prescription_number: str, dispensing_date: date) -> Optional[dict]:
        query = text("""
            SELECT * FROM prescriptions 
            WHERE prescription_number = :prescription_number 
            AND dispensing_date = :dispensing_date
        """)
        result = self.session.execute(query, {
            "prescription_number": prescription_number,
            "dispensing_date": dispensing_date
        }).mappings().first()
        return dict(result) if result else None

    def bulk_upsert(self, prescriptions: List[dict]) -> tuple:
        inserted = 0
        for rx in prescriptions:
            if self.store_or_update(rx):
                inserted += 1
        return inserted, 0

