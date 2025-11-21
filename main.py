import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from database import db, create_document, get_documents
from schemas import User, Patient, Doctor, Appointment, Medicine, Prescription, LabTest, Invoice, Vital, Ward, InventoryItem, Notification, Record

app = FastAPI(title="Hulubedeje API", description="Hospital Management System API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hulubedeje Backend Running", "version": "0.1.0"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:20]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response

# ----------------------------- AUTH LIGHT ENDPOINTS -----------------------------

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str

@app.post("/auth/signup")
def signup(payload: SignupRequest):
    # check if email exists
    existing = get_documents("user", {"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(name=payload.name, email=payload.email, password=payload.password, role=payload.role)
    _id = create_document("user", user)
    return {"id": _id, "message": "Signup successful"}

@app.post("/auth/login")
def login(payload: LoginRequest):
    users = get_documents("user", {"email": payload.email, "password": payload.password})
    if not users:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = users[0]
    return {"message": "Login successful", "user": {"id": str(user.get("_id")), "name": user.get("name"), "role": user.get("role")}}

# ----------------------------- PATIENTS -----------------------------

@app.post("/patients")
def create_patient(patient: Patient):
    _id = create_document("patient", patient)
    return {"id": _id}

@app.get("/patients")
def list_patients(limit: int = 50):
    docs = get_documents("patient", {}, limit)
    return docs

# ----------------------------- DOCTORS -----------------------------

@app.post("/doctors")
def create_doctor(doctor: Doctor):
    _id = create_document("doctor", doctor)
    return {"id": _id}

@app.get("/doctors")
def list_doctors(limit: int = 50):
    docs = get_documents("doctor", {}, limit)
    return docs

# ----------------------------- APPOINTMENTS -----------------------------

@app.post("/appointments")
def create_appointment(appt: Appointment):
    _id = create_document("appointment", appt)
    return {"id": _id}

@app.get("/appointments")
def list_appointments(patient_id: Optional[str] = None, doctor_id: Optional[str] = None, limit: int = 50):
    filt = {}
    if patient_id:
        filt["patient_id"] = patient_id
    if doctor_id:
        filt["doctor_id"] = doctor_id
    docs = get_documents("appointment", filt, limit)
    return docs

# ----------------------------- PHARMACY -----------------------------

@app.post("/medicines")
def create_medicine(med: Medicine):
    _id = create_document("medicine", med)
    return {"id": _id}

@app.get("/medicines")
def list_medicines(q: Optional[str] = None, limit: int = 100):
    filt = {}
    if q:
        filt["name"] = {"$regex": q, "$options": "i"}
    docs = get_documents("medicine", filt, limit)
    return docs

@app.post("/prescriptions")
def create_prescription(p: Prescription):
    _id = create_document("prescription", p)
    return {"id": _id}

@app.get("/prescriptions")
def list_prescriptions(patient_id: Optional[str] = None, doctor_id: Optional[str] = None, limit: int = 50):
    filt = {}
    if patient_id:
        filt["patient_id"] = patient_id
    if doctor_id:
        filt["doctor_id"] = doctor_id
    docs = get_documents("prescription", filt, limit)
    return docs

# ----------------------------- LAB -----------------------------

@app.post("/lab/tests")
def request_lab(test: LabTest):
    _id = create_document("labtest", test)
    return {"id": _id}

@app.get("/lab/tests")
def list_lab_tests(patient_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    filt = {}
    if patient_id:
        filt["patient_id"] = patient_id
    if status:
        filt["status"] = status
    docs = get_documents("labtest", filt, limit)
    return docs

# ----------------------------- BILLING -----------------------------

@app.post("/billing/invoices")
def create_invoice(inv: Invoice):
    _id = create_document("invoice", inv)
    return {"id": _id}

@app.get("/billing/invoices")
def list_invoices(patient_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    filt = {}
    if patient_id:
        filt["patient_id"] = patient_id
    if status:
        filt["status"] = status
    docs = get_documents("invoice", filt, limit)
    return docs

# ----------------------------- NURSING -----------------------------

@app.post("/nursing/vitals")
def record_vital(v: Vital):
    _id = create_document("vital", v)
    return {"id": _id}

@app.get("/nursing/vitals")
def list_vitals(patient_id: Optional[str] = None, limit: int = 100):
    filt = {}
    if patient_id:
        filt["patient_id"] = patient_id
    docs = get_documents("vital", filt, limit)
    return docs

@app.post("/nursing/wards")
def create_ward(ward: Ward):
    _id = create_document("ward", ward)
    return {"id": _id}

@app.get("/nursing/wards")
def list_wards(limit: int = 100):
    docs = get_documents("ward", {}, limit)
    return docs

# ----------------------------- INVENTORY -----------------------------

@app.post("/inventory/items")
def create_inventory_item(item: InventoryItem):
    _id = create_document("inventoryitem", item)
    return {"id": _id}

@app.get("/inventory/items")
def list_inventory_items(q: Optional[str] = None, limit: int = 100):
    filt = {}
    if q:
        filt["name"] = {"$regex": q, "$options": "i"}
    docs = get_documents("inventoryitem", filt, limit)
    return docs

# ----------------------------- NOTIFICATIONS -----------------------------

@app.post("/notifications")
def create_notification(n: Notification):
    _id = create_document("notification", n)
    return {"id": _id}

@app.get("/notifications")
def list_notifications(user_id: Optional[str] = None, limit: int = 100):
    filt = {}
    if user_id:
        filt["user_id"] = user_id
    docs = get_documents("notification", filt, limit)
    return docs

# ----------------------------- EHR -----------------------------

@app.post("/records")
def create_record(r: Record):
    _id = create_document("record", r)
    return {"id": _id}

@app.get("/records")
def list_records(patient_id: Optional[str] = None, limit: int = 100):
    filt = {}
    if patient_id:
        filt["patient_id"] = patient_id
    docs = get_documents("record", filt, limit)
    return docs

# ----------------------------- SCHEMA INSPECTOR -----------------------------

@app.get("/schema")
def get_schema_collections():
    return {
        "collections": [
            "user", "patient", "doctor", "appointment", "invoice", "medicine",
            "prescription", "labtest", "vital", "ward", "inventoryitem", "notification", "record"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
