import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        DOCTOR = "DOCTOR", "Doctor"
        NURSE = "NURSE", "Nurse"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
        PATIENT = "PATIENT", "Patient"
        PHARMACIST = "PHARMACIST", "Pharmacist"
        LAB_TECHNICIAN = "LAB_TECHNICIAN", "Lab technician"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"
        RADIOLOGIST = "RADIOLOGIST", "Radiologist"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    phone = models.CharField(max_length=20, blank=True)


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=12, unique=True)

    def __str__(self): return self.name


class Patient(models.Model):
    patient_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="patient_profile")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    emergency_contact_name = models.CharField(max_length=150)
    emergency_contact_phone = models.CharField(max_length=20)
    allergies = models.TextField(blank=True)
    family_history = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    insurance_provider = models.CharField(max_length=150, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def qr_value(self): return str(self.patient_code)

    def __str__(self): return f"{self.first_name} {self.last_name}".strip()


class BloodDonor(models.Model):
    full_name = models.CharField(max_length=150)
    blood_group = models.CharField(max_length=5, db_index=True)
    phone = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    address = models.TextField(blank=True)
    last_donation_date = models.DateField(null=True, blank=True)
    is_eligible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.full_name} ({self.blood_group})"


class BloodUnit(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        RESERVED = "RESERVED", "Reserved"
        ISSUED = "ISSUED", "Issued"
        EXPIRED = "EXPIRED", "Expired"
        DISCARDED = "DISCARDED", "Discarded"

    unit_number = models.CharField(max_length=50, unique=True)
    donor = models.ForeignKey(BloodDonor, on_delete=models.SET_NULL, null=True, blank=True)
    blood_group = models.CharField(max_length=5, db_index=True)
    component = models.CharField(max_length=50, default="Whole Blood")
    collection_date = models.DateField()
    expiry_date = models.DateField(db_index=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.AVAILABLE, db_index=True)

    def __str__(self): return f"{self.unit_number} · {self.blood_group}"


class BloodRequest(models.Model):
    class Priority(models.TextChoices):
        ROUTINE = "ROUTINE", "Routine"
        URGENT = "URGENT", "Urgent"
        EMERGENCY = "EMERGENCY", "Emergency"

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        RESERVED = "RESERVED", "Reserved"
        ISSUED = "ISSUED", "Issued"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    blood_group = models.CharField(max_length=5)
    component = models.CharField(max_length=50, default="Whole Blood")
    units_required = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    priority = models.CharField(max_length=12, choices=Priority.choices, default=Priority.ROUTINE)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.REQUESTED)
    notes = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)


class Appointment(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No show"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="appointments")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="appointments", limit_choices_to={"role": User.Role.DOCTOR})
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    scheduled_at = models.DateTimeField(db_index=True)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.REQUESTED, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: constraints = [models.UniqueConstraint(fields=["doctor", "scheduled_at"], name="one_doctor_one_slot")]


class Encounter(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="encounters")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="encounters")
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    chief_complaint = models.TextField()
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)


class VitalSign(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="vital_signs")
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="recorded_vitals")
    temperature_celsius = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    pulse_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    systolic_bp = models.PositiveSmallIntegerField(null=True, blank=True)
    diastolic_bp = models.PositiveSmallIntegerField(null=True, blank=True)
    oxygen_saturation = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="prescriptions")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="prescriptions")
    encounter = models.ForeignKey(Encounter, on_delete=models.SET_NULL, null=True, blank=True, related_name="prescriptions")
    notes = models.TextField(blank=True)
    prescribed_at = models.DateTimeField(auto_now_add=True, db_index=True)


class ConsentRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="consents")
    consent_type = models.CharField(max_length=120)
    signed_by = models.CharField(max_length=150)
    signed_at = models.DateTimeField(auto_now_add=True)
    document = models.FileField(upload_to="consents/", blank=True)
    notes = models.TextField(blank=True)


class Bed(models.Model):
    ward = models.CharField(max_length=100)
    bed_number = models.CharField(max_length=30, unique=True)
    is_occupied = models.BooleanField(default=False, db_index=True)


class Admission(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    bed = models.ForeignKey(Bed, on_delete=models.PROTECT)
    attending_doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    admitted_at = models.DateTimeField(auto_now_add=True)
    discharged_at = models.DateTimeField(null=True, blank=True)
    diagnosis = models.TextField(blank=True)


class Ambulance(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        DISPATCHED = "DISPATCHED", "Dispatched"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    vehicle_number = models.CharField(max_length=30, unique=True)
    driver_name = models.CharField(max_length=150)
    driver_phone = models.CharField(max_length=20)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.AVAILABLE, db_index=True)
    last_known_location = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return self.vehicle_number


class EmergencyCase(models.Model):
    class Triage(models.TextChoices):
        RED = "RED", "Red - immediate"
        YELLOW = "YELLOW", "Yellow - urgent"
        GREEN = "GREEN", "Green - non-urgent"
        BLACK = "BLACK", "Black - deceased"

    class Status(models.TextChoices):
        ARRIVED = "ARRIVED", "Arrived"
        TRIAGED = "TRIAGED", "Triaged"
        ADMITTED = "ADMITTED", "Admitted"
        DISCHARGED = "DISCHARGED", "Discharged"
        REFERRED = "REFERRED", "Referred"

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    temporary_patient_name = models.CharField(max_length=150, blank=True)
    arrival_time = models.DateTimeField(auto_now_add=True)
    triage_level = models.CharField(max_length=10, choices=Triage.choices, default=Triage.YELLOW, db_index=True)
    chief_complaint = models.TextField()
    assigned_doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="emergency_cases")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ARRIVED, db_index=True)
    notes = models.TextField(blank=True)

    def __str__(self): return self.temporary_patient_name or str(self.patient)


class AmbulanceDispatch(models.Model):
    class Status(models.TextChoices):
        DISPATCHED = "DISPATCHED", "Dispatched"
        PICKED_UP = "PICKED_UP", "Patient picked up"
        ARRIVED = "ARRIVED", "Arrived at hospital"
        CANCELLED = "CANCELLED", "Cancelled"

    ambulance = models.ForeignKey(Ambulance, on_delete=models.PROTECT, related_name="dispatches")
    emergency_case = models.ForeignKey(EmergencyCase, on_delete=models.SET_NULL, null=True, blank=True)
    pickup_location = models.TextField()
    contact_phone = models.CharField(max_length=20)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DISPATCHED)
    dispatched_at = models.DateTimeField(auto_now_add=True)
    arrived_at = models.DateTimeField(null=True, blank=True)


class DischargeSummary(models.Model):
    admission = models.OneToOneField(Admission, on_delete=models.PROTECT, related_name="discharge_summary")
    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    final_diagnosis = models.TextField()
    treatment_summary = models.TextField()
    discharge_instructions = models.TextField()
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OperationSchedule(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    surgeon = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="operations")
    scheduled_at = models.DateTimeField(db_index=True)
    operating_room = models.CharField(max_length=50)
    procedure_name = models.CharField(max_length=200)
    anaesthetist = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    pre_op_notes = models.TextField(blank=True)


class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="invoices")
    invoice_number = models.CharField(max_length=40, unique=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    issued_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"
        UPI = "UPI", "UPI"
        BANK = "BANK", "Bank transfer"
        INSURANCE = "INSURANCE", "Insurance"

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    method = models.CharField(max_length=12, choices=Method.choices)
    reference_number = models.CharField(max_length=100, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)


class InsuranceClaim(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SETTLED = "SETTLED", "Settled"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)
    insurer_name = models.CharField(max_length=150)
    policy_number = models.CharField(max_length=100)
    claim_number = models.CharField(max_length=100, unique=True)
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)


class Medicine(models.Model):
    name = models.CharField(max_length=200)
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField()
    quantity_in_stock = models.PositiveIntegerField(default=0, db_index=True)
    reorder_level = models.PositiveIntegerField(default=10)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta: constraints = [models.UniqueConstraint(fields=["name", "batch_number"], name="medicine_batch_unique")]


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration_days = models.PositiveSmallIntegerField()
    instructions = models.TextField(blank=True)


class Supplier(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)


class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ORDERED = "ORDERED", "Ordered"
        RECEIVED = "RECEIVED", "Received"
        CANCELLED = "CANCELLED", "Cancelled"

    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    order_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)


class LabReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="lab_reports")
    ordered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    test_name = models.CharField(max_length=200)
    report_pdf = models.FileField(upload_to="lab_reports/")
    reported_at = models.DateTimeField(auto_now_add=True)


class LabTestOrder(models.Model):
    class Status(models.TextChoices):
        ORDERED = "ORDERED", "Ordered"
        COLLECTED = "COLLECTED", "Sample collected"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    ordered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    test_name = models.CharField(max_length=200)
    priority = models.CharField(max_length=20, choices=[("ROUTINE", "Routine"), ("URGENT", "Urgent")], default="ROUTINE")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ORDERED)
    sample_collected_at = models.DateTimeField(null=True, blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    class Channel(models.TextChoices):
        SMS = "SMS", "SMS"
        EMAIL = "EMAIL", "Email"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        IN_APP = "IN_APP", "In-app"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    recipient = models.CharField(max_length=150)
    channel = models.CharField(max_length=12, choices=Channel.choices, default=Channel.IN_APP)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    status_code = models.PositiveSmallIntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


class DoctorSchedule(models.Model):
    class DayOfWeek(models.TextChoices):
        MONDAY = "MONDAY", "Monday"
        TUESDAY = "TUESDAY", "Tuesday"
        WEDNESDAY = "WEDNESDAY", "Wednesday"
        THURSDAY = "THURSDAY", "Thursday"
        FRIDAY = "FRIDAY", "Friday"
        SATURDAY = "SATURDAY", "Saturday"
        SUNDAY = "SUNDAY", "Sunday"

    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.CharField(max_length=12, choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.PositiveSmallIntegerField(default=15)
    max_patients = models.PositiveSmallIntegerField(default=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.doctor.username} - {self.day_of_week} ({self.start_time} - {self.end_time})"


class DoctorLeave(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leaves")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.APPROVED)

    def __str__(self):
        return f"Dr. {self.doctor.username} Leave ({self.start_date} to {self.end_date})"


class OpdToken(models.Model):
    class Status(models.TextChoices):
        WAITING = "WAITING", "Waiting"
        IN_CONSULTATION = "IN_CONSULTATION", "In consultation"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    token_number = models.PositiveIntegerField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="opd_tokens")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="opd_tokens")
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token #{self.token_number} - {self.patient} (Dr. {self.doctor.username})"


class RadiologyReport(models.Model):
    class Modality(models.TextChoices):
        XRAY = "XRAY", "X-Ray"
        CT = "CT", "CT Scan"
        MRI = "MRI", "MRI"
        ULTRASOUND = "ULTRASOUND", "Ultrasound"

    class Status(models.TextChoices):
        ORDERED = "ORDERED", "Ordered"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="radiology_reports")
    ordered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="radiology_orders")
    radiologist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="radiology_reports")
    modality = models.CharField(max_length=15, choices=Modality.choices, default=Modality.XRAY)
    body_part = models.CharField(max_length=100)
    findings = models.TextField()
    impression = models.TextField(blank=True)
    image_file = models.FileField(upload_to="radiology/", blank=True)
    report_pdf = models.FileField(upload_to="radiology_reports/", blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ORDERED)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.modality} - {self.patient} ({self.body_part})"


class PatientDocument(models.Model):
    class DocType(models.TextChoices):
        PRESCRIPTION = "PRESCRIPTION", "Prescription"
        LAB = "LAB", "Lab Report"
        RADIOLOGY = "RADIOLOGY", "Radiology Image"
        ID_PROOF = "ID_PROOF", "ID Proof"
        OTHER = "OTHER", "Other Document"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DocType.choices, default=DocType.OTHER)
    file = models.FileField(upload_to="patient_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.patient}"


class NursingNote(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="nursing_notes")
    nurse = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    note = models.TextField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.patient} by {self.nurse.username}"


class MedicationAdministrationLog(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medication_logs")
    administered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    dosage = models.CharField(max_length=100)
    administered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.medicine.name} to {self.patient}"


class PaymentGatewayTransaction(models.Model):
    class Gateway(models.TextChoices):
        RAZORPAY = "RAZORPAY", "Razorpay"
        STRIPE = "STRIPE", "Stripe"
        UPI = "UPI", "UPI"
        CASH = "CASH", "Cash"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="gateway_transactions")
    gateway = models.CharField(max_length=12, choices=Gateway.choices, default=Gateway.RAZORPAY)
    transaction_id = models.CharField(max_length=150, unique=True)
    order_id = models.CharField(max_length=150, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.gateway} - {self.transaction_id} ({self.status})"


class SystemBackupLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    file_name = models.CharField(max_length=255)
    file_size_bytes = models.PositiveIntegerField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SUCCESS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Backup {self.file_name} ({self.status})"

