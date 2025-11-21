"""
Hulubedeje (ሁሉ በደጄ) Hospital Management System Schemas

Each Pydantic model represents a MongoDB collection. The collection name is the lowercase of the class name.

Core collections:
- User: authentication + roles
- Patient: patient profile and demographics
- Doctor: doctor profile and availability
- Appointment: appointment bookings
- Invoice: billing
- Medicine: pharmacy inventory
- Prescription: doctor prescriptions
- LabTest: lab requests/results
- Vital: nursing vitals
- Ward: wards/beds
- InventoryItem: equipment and stock
- Notification: system notifications
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime

# AUTH / USER MANAGEMENT
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Hashed or plain for demo")
    role: Literal["admin", "doctor", "nurse", "patient", "pharmacist", "lab"] = Field(...)
    is_active: bool = Field(True)
    phone: Optional[str] = None
    language: Optional[Literal["en", "am"]] = "en"

# PATIENTS
class Patient(BaseModel):
    user_id: Optional[str] = Field(None, description="Linked user id if portal account exists")
    first_name: str
    last_name: str
    gender: Optional[Literal["male", "female", "other"]] = None
    dob: Optional[str] = Field(None, description="YYYY-MM-DD")
    national_id: Optional[str] = None
    emergency_contact: Optional[dict] = None
    address: Optional[str] = None
    city: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[List[str]] = []
    chronic_conditions: Optional[List[str]] = []

# DOCTORS
class Doctor(BaseModel):
    user_id: Optional[str] = None
    name: str
    specialty: str
    qualifications: Optional[List[str]] = []
    bio: Optional[str] = None
    consultation_fee: Optional[float] = 0.0
    availability: Optional[List[dict]] = Field(default_factory=list, description="[{day, start, end}]")

# APPOINTMENTS
class Appointment(BaseModel):
    patient_id: str
    doctor_id: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    status: Literal["pending", "confirmed", "completed", "cancelled"] = "pending"
    reason: Optional[str] = None
    notes: Optional[str] = None

# BILLING
class Invoice(BaseModel):
    patient_id: str
    amount: float
    status: Literal["unpaid", "paid", "partial", "void"] = "unpaid"
    items: List[dict] = Field(default_factory=list)
    insurance_provider: Optional[str] = None
    insurance_policy: Optional[str] = None

# PHARMACY
class Medicine(BaseModel):
    name: str
    sku: Optional[str] = None
    price: float
    stock: int
    expiry_date: Optional[str] = None
    manufacturer: Optional[str] = None

class Prescription(BaseModel):
    patient_id: str
    doctor_id: str
    items: List[dict] = Field(default_factory=list)  # [{medicine_id, name, dose, frequency, duration}]
    notes: Optional[str] = None

# LABORATORY
class LabTest(BaseModel):
    patient_id: str
    doctor_id: Optional[str] = None
    test_type: str
    status: Literal["requested", "in_progress", "completed", "rejected"] = "requested"
    result_url: Optional[str] = None  # points to PDF path
    result_values: Optional[dict] = None

# NURSING
class Vital(BaseModel):
    patient_id: str
    temperature_c: Optional[float] = None
    pulse_bpm: Optional[int] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    respiration_rate: Optional[int] = None
    spo2: Optional[int] = None
    recorded_by: Optional[str] = None  # nurse user id
    recorded_at: Optional[str] = None

class Ward(BaseModel):
    name: str
    bed_count: int
    occupied_beds: int = 0
    notes: Optional[str] = None

# INVENTORY
class InventoryItem(BaseModel):
    name: str
    category: Optional[str] = None
    quantity: int
    min_threshold: Optional[int] = 0
    unit: Optional[str] = None
    vendor: Optional[str] = None

# NOTIFICATIONS
class Notification(BaseModel):
    user_id: str
    title: str
    message: str
    type: Literal["info", "success", "warning", "error"] = "info"
    read: bool = False

# EHR
class Record(BaseModel):
    patient_id: str
    visit_date: str
    diagnosis: Optional[str] = None
    prescriptions: Optional[List[str]] = []
    labs: Optional[List[str]] = []
    documents: Optional[List[str]] = []
