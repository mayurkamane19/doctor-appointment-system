from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from hospital.models import Admission, Appointment, Bed, ConsentRecord, Department, Encounter, InsuranceClaim, Invoice, LabReport, LabTestOrder, Medicine, Notification, OperationSchedule, Patient, Payment, Prescription, PrescriptionItem, PurchaseOrder, Supplier, User, VitalSign


class Command(BaseCommand):
    help = "Creates non-clinical demo data for the CarePoint HMS portal."

    def handle(self, *args, **options):
        departments = {}
        for name, code in [("Cardiology", "CARD"), ("Orthopedics", "ORTHO"), ("General Medicine", "GEN"), ("Pediatrics", "PEDS"), ("Pathology", "PATH")]:
            departments[name], _ = Department.objects.get_or_create(code=code, defaults={"name": name})

        doctors = {}
        for username, first_name, last_name, department_name in [("dr_rahul", "Rahul", "Mehta", "Cardiology"), ("dr_priya", "Priya", "Nair", "Orthopedics"), ("dr_arjun", "Arjun", "Shah", "General Medicine")]:
            doctor, _ = User.objects.get_or_create(username=username, defaults={"first_name": first_name, "last_name": last_name, "email": f"{username}@carepoint.demo", "role": User.Role.DOCTOR})
            doctor.first_name, doctor.last_name, doctor.role = first_name, last_name, User.Role.DOCTOR
            doctor.set_password("DemoDoctor@123")
            doctor.save()
            doctors[department_name] = doctor

        patient_data = [
            ("Anita", "Sharma", date(1989, 5, 12), "Female", "9876500001", "A+", "Vikram Sharma", "9876501001"),
            ("Rajesh", "Kumar", date(1977, 8, 23), "Male", "9876500002", "B+", "Sunita Kumar", "9876501002"),
            ("Meera", "Patel", date(1994, 11, 2), "Female", "9876500003", "O+", "Nilesh Patel", "9876501003"),
            ("Arjun", "Singh", date(1982, 3, 18), "Male", "9876500004", "AB+", "Kavita Singh", "9876501004"),
            ("Kavya", "Iyer", date(2001, 7, 29), "Female", "9876500005", "A-", "Ramesh Iyer", "9876501005"),
        ]
        patients = []
        for first_name, last_name, birth_date, sex, phone, blood_group, contact_name, contact_phone in patient_data:
            patient, _ = Patient.objects.get_or_create(phone=phone, defaults={"first_name": first_name, "last_name": last_name, "date_of_birth": birth_date, "sex": sex, "email": f"{first_name.lower()}@demo.local", "address": "CarePoint Demo Address, Pune", "blood_group": blood_group, "emergency_contact_name": contact_name, "emergency_contact_phone": contact_phone})
            patients.append(patient)

        beds = []
        for ward, bed_number in [("General Ward", "GW-01"), ("General Ward", "GW-02"), ("General Ward", "GW-03"), ("Private Ward", "PW-01"), ("Private Ward", "PW-02"), ("ICU", "ICU-01"), ("ICU", "ICU-02")]:
            bed, _ = Bed.objects.get_or_create(bed_number=bed_number, defaults={"ward": ward})
            beds.append(bed)

        today = timezone.localdate()
        appointment_data = [(patients[0], doctors["Cardiology"], departments["Cardiology"], time(9, 30), "Chest discomfort follow-up"), (patients[1], doctors["Orthopedics"], departments["Orthopedics"], time(10, 15), "Knee pain consultation"), (patients[2], doctors["Cardiology"], departments["Cardiology"], time(11, 0), "Routine cardiac review"), (patients[3], doctors["General Medicine"], departments["General Medicine"], time(12, 30), "Fever and fatigue")]
        appointments = []
        for patient, doctor, department, slot_time, reason in appointment_data:
            scheduled_at = timezone.make_aware(datetime.combine(today, slot_time))
            appointment, _ = Appointment.objects.get_or_create(doctor=doctor, scheduled_at=scheduled_at, defaults={"patient": patient, "department": department, "reason": reason, "status": Appointment.Status.CONFIRMED})
            appointments.append(appointment)

        Encounter.objects.get_or_create(patient=patients[0], doctor=doctors["Cardiology"], appointment=appointments[0], defaults={"chief_complaint": "Intermittent chest discomfort", "diagnosis": "Observation required", "treatment_plan": "ECG and follow-up", "notes": "Demo clinical data only; not for patient care."})
        encounter = Encounter.objects.get(patient=patients[0], appointment=appointments[0])
        VitalSign.objects.get_or_create(patient=patients[0], recorded_by=doctors["Cardiology"], defaults={"temperature_celsius": Decimal("36.8"), "pulse_rate": 78, "systolic_bp": 118, "diastolic_bp": 76, "oxygen_saturation": 98, "weight_kg": Decimal("62.50"), "notes": "Stable; demo record."})
        prescription, _ = Prescription.objects.get_or_create(patient=patients[0], doctor=doctors["Cardiology"], encounter=encounter, defaults={"notes": "Take medicines after meals. Demo prescription only."})

        for patient, bed, doctor, diagnosis in [(patients[0], beds[0], doctors["Cardiology"], "Cardiac observation"), (patients[3], beds[1], doctors["General Medicine"], "Fever observation")]:
            admission, created = Admission.objects.get_or_create(patient=patient, bed=bed, discharged_at__isnull=True, defaults={"attending_doctor": doctor, "diagnosis": diagnosis})
            if created or not bed.is_occupied:
                bed.is_occupied = True
                bed.save(update_fields=["is_occupied"])

        medicine_data = [("Paracetamol 500 mg", "PCM-2401", date.today() + timedelta(days=450), 8, 20, "2.50"), ("Amoxicillin 250 mg", "AMX-2421", date.today() + timedelta(days=320), 6, 15, "12.00"), ("Insulin Injection", "INS-2410", date.today() + timedelta(days=180), 4, 10, "360.00"), ("Normal Saline 500 ml", "NS-2440", date.today() + timedelta(days=280), 42, 20, "45.00")]
        for name, batch_number, expiry_date, quantity, reorder_level, price in medicine_data:
            Medicine.objects.update_or_create(name=name, batch_number=batch_number, defaults={"expiry_date": expiry_date, "quantity_in_stock": quantity, "reorder_level": reorder_level, "unit_price": Decimal(price)})
        paracetamol = Medicine.objects.get(name="Paracetamol 500 mg", batch_number="PCM-2401")
        PrescriptionItem.objects.get_or_create(prescription=prescription, medicine=paracetamol, defaults={"dosage": "500 mg", "frequency": "Twice daily", "duration_days": 5, "instructions": "After food"})

        for number, patient, subtotal, gst, paid in [("CP-2026-0001", patients[0], "12500.00", "625.00", "13125.00"), ("CP-2026-0002", patients[1], "4500.00", "225.00", "2500.00"), ("CP-2026-0003", patients[2], "7800.00", "390.00", "8190.00")]:
            Invoice.objects.update_or_create(invoice_number=number, defaults={"patient": patient, "subtotal": Decimal(subtotal), "gst_amount": Decimal(gst), "paid_amount": Decimal(paid)})
        first_invoice = Invoice.objects.get(invoice_number="CP-2026-0001")
        Payment.objects.get_or_create(invoice=first_invoice, reference_number="UPI-DEMO-0001", defaults={"amount": Decimal("13125.00"), "method": Payment.Method.UPI})
        InsuranceClaim.objects.get_or_create(claim_number="CLAIM-DEMO-001", defaults={"patient": patients[1], "invoice": Invoice.objects.get(invoice_number="CP-2026-0002"), "insurer_name": "CareShield Insurance", "policy_number": "CS-2026-8842", "claim_amount": Decimal("2225.00"), "status": InsuranceClaim.Status.SUBMITTED})

        supplier, _ = Supplier.objects.get_or_create(name="MediSupply Distributors", defaults={"contact_person": "Neha Joshi", "phone": "9876511111", "email": "orders@medisupply.demo", "gstin": "27ABCDE1234F1Z5", "address": "Pune, Maharashtra"})
        PurchaseOrder.objects.get_or_create(order_number="PO-2026-0001", defaults={"supplier": supplier, "expected_delivery_date": today + timedelta(days=3), "total_amount": Decimal("24500.00"), "status": PurchaseOrder.Status.ORDERED, "notes": "Restock low pharmacy inventory."})

        document = SimpleUploadedFile("demo-blood-report.txt", b"Demo laboratory report. Not for clinical use.", content_type="text/plain")
        LabReport.objects.get_or_create(patient=patients[0], test_name="Complete Blood Count", defaults={"ordered_by": doctors["General Medicine"], "report_pdf": document})
        LabTestOrder.objects.get_or_create(patient=patients[0], test_name="Complete Blood Count", defaults={"ordered_by": doctors["General Medicine"], "priority": "ROUTINE", "status": LabTestOrder.Status.COMPLETED})
        ConsentRecord.objects.get_or_create(patient=patients[0], consent_type="General treatment consent", defaults={"signed_by": "Anita Sharma", "notes": "Demo consent record."})
        operation_datetime = timezone.make_aware(datetime.combine(today + timedelta(days=1), time(10, 0)))
        OperationSchedule.objects.get_or_create(patient=patients[1], surgeon=doctors["Orthopedics"], scheduled_at=operation_datetime, defaults={"operating_room": "OT-02", "procedure_name": "Arthroscopic knee procedure", "anaesthetist": "Dr. Sunil Rao", "status": OperationSchedule.Status.SCHEDULED, "pre_op_notes": "Demo OT schedule."})
        Notification.objects.get_or_create(recipient=patients[0].phone, subject="Appointment reminder", defaults={"patient": patients[0], "channel": Notification.Channel.SMS, "message": "Demo reminder: your appointment is scheduled today.", "status": Notification.Status.SENT, "sent_at": timezone.now()})

        self.stdout.write(self.style.SUCCESS("Demo data created. Login: admin / Hospital@12345"))
