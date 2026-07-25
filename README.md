# 🏥 CarePoint HMS - Enterprise Hospital Management ERP System

**CarePoint HMS** is a commercial-grade, full-featured **Enterprise Hospital ERP Platform** built with **Django 5.1**, **Django REST Framework (DRF)**, **WhiteNoise**, **ReportLab PDF**, **openpyxl Excel**, and **drf-spectacular OpenAPI/Swagger**.

---

## 🌐 Live Demo & Deployment

- 🔗 **Live Production Site:** [https://doctor-appointment-system-z8k5.onrender.com](https://doctor-appointment-system-z8k5.onrender.com)
- 📖 **Interactive Swagger API Docs:** [https://doctor-appointment-system-z8k5.onrender.com/api/docs/](https://doctor-appointment-system-z8k5.onrender.com/api/docs/)
- 📂 **GitHub Repository:** [https://github.com/mayurkamane19/doctor-appointment-system](https://github.com/mayurkamane19/doctor-appointment-system)

---

## 🚀 Key Enterprise Modules

### 👤 1. Patient & OPD Management
- Patient Registration, Digital Patient Code UUID, Medical History, Allergies, Family History, Insurance Details.
- Patient Digital QR Code Identity Cards (`/portal/patients/<id>/card/`).
- OPD Queue Token System with token status tracking (`WAITING`, `IN_CONSULTATION`, `COMPLETED`, `CANCELLED`).
- Medical Document Vault for uploading patient records, prescriptions, and lab documents.

### 🗓️ 2. Doctor Scheduling & OPD Calendar
- Doctor Shift Scheduling & Time-Slot Management.
- Leave Request Approval Workflow (`REQUESTED`, `APPROVED`, `REJECTED`).
- Department Assignment and Consultation Volume Tracking.

### 🚨 3. Emergency Triage & Ambulance Fleet
- 4-Tier Emergency Triage (`CRITICAL_RESUSCITATION`, `EMERGENCY`, `URGENT`, `NON_URGENT`).
- Ambulance Fleet Management with Live Driver Contact and Pickup Dispatching.

### 🩻 4. Radiology & Imaging (PACS/RIS Ready)
- Modality Scheduling for **X-Ray, CT Scan, MRI, and Ultrasound**.
- Findings, Radiological Impressions, and Image/PDF Uploads.

### 🏥 5. IPD Admissions, Beds & Operation Theatre (OT)
- Ward & Bed Allocation Grid with Real-Time Occupancy Analytics.
- OT Surgery Scheduling with Surgeon, Operating Room, and Anaesthetist Assignment.
- One-Click Discharge Summary Generation.

### 🩺 6. Nursing & Inpatient Care
- Real-time Vitals Recording (BP, Pulse, Temperature, SpO2, Weight).
- Nursing Shift Notes and Medication Administration Logs with Dosage Timestamping.

### 🧪 7. Laboratory & Pharmacy ERP
- Lab Test Ordering & Sample Collection Tracking.
- Pharmacy Stock Management with Low Stock Reorder Alerts.
- Supplier Purchase Orders & Blood Bank Inventory (Donors, Units, Requests).

### 🧾 8. Finance, GST Billing & Payment Gateways
- Line-Item GST Invoices with Automated Tax Split.
- Razorpay & Stripe Payment Gateway Transaction Tracking.
- TPA Insurance Claims Management.

### 📑 9. PDF Reports & Excel Exports
- **Downloadable PDF Reports**: Invoices, E-Prescriptions, and Discharge Summaries generated via ReportLab.
- **Data Exports**: One-click Excel `.xlsx` revenue audit exports and `.csv` patient directory downloads.

### 📖 10. Interactive OpenAPI / Swagger API Docs
- Live Swagger UI at `/api/docs/` and ReDoc at `/api/redoc/`.
- Complete JWT Authentication (`POST /api/auth/token/`).

---

## 🛠️ Installation & Setup

### 1. Local Development
```bash
# Clone Repository
git clone https://github.com/mayurkamane19/doctor-appointment-system.git
cd doctor-appointment-system

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Access the portal at `http://127.0.0.1:8000/` and Swagger API docs at `http://127.0.0.1:8000/api/docs/`.

---

## 🌐 Production Deployment on Render

This project is pre-configured for 1-click zero-config deployment on **Render**:
- Uses **WhiteNoise** for high-performance static CSS/JS file serving.
- `build.sh` automatically collects static files and executes database migrations on deploy.
- Dual-support database engine: PostgreSQL on Render (`DATABASE_URL`), SQLite locally.

### Production Environment Variables:
- `DEBUG`: `False`
- `DJANGO_SECRET_KEY`: *(Generate a secure random string)*
- `ALLOWED_HOSTS`: `doctor-appointment-system-z8k5.onrender.com,.onrender.com`
- `CSRF_TRUSTED_ORIGINS`: `https://doctor-appointment-system-z8k5.onrender.com,https://*.onrender.com`

---

## 🔒 Security & RBAC
- Role-Based Access Control (`ADMIN`, `DOCTOR`, `NURSE`, `RECEPTIONIST`, `PHARMACIST`, `LAB_TECHNICIAN`, `ACCOUNTANT`, `RADIOLOGIST`, `PATIENT`).
- Audit Logging (`AuditLog`) tracking all mutating API requests.
- Secure CSRF protection & `SECURE_PROXY_SSL_HEADER` support for SSL proxy environments.
