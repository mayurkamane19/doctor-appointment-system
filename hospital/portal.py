import csv
import io
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count, ProtectedError, Q, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .forms import hospital_form
from .models import (
    Admission,
    Ambulance,
    AmbulanceDispatch,
    Appointment,
    Bed,
    BloodDonor,
    BloodRequest,
    BloodUnit,
    ConsentRecord,
    Department,
    DischargeSummary,
    DoctorLeave,
    DoctorSchedule,
    EmergencyCase,
    Encounter,
    InsuranceClaim,
    Invoice,
    LabReport,
    LabTestOrder,
    MedicationAdministrationLog,
    Medicine,
    Notification,
    NursingNote,
    OpdToken,
    OperationSchedule,
    Patient,
    PatientDocument,
    Payment,
    PaymentGatewayTransaction,
    Prescription,
    PrescriptionItem,
    PurchaseOrder,
    RadiologyReport,
    Supplier,
    SystemBackupLog,
    VitalSign,
)


def staff_required(view):
    return user_passes_test(lambda account: account.is_staff, login_url="/admin/login/")(view)


PORTAL_MODELS = {
    "patients": {"model": Patient, "title": "Patients", "singular": "Patient", "fields": ["first_name", "last_name", "date_of_birth", "sex", "phone", "email", "address", "blood_group", "emergency_contact_name", "emergency_contact_phone", "allergies", "family_history", "medical_history", "insurance_provider", "insurance_policy_number"], "columns": ["patient_code", "first_name", "last_name", "phone", "blood_group", "insurance_provider"]},
    "blood-donors": {"model": BloodDonor, "title": "Blood Donors", "singular": "Blood Donor", "fields": ["full_name", "blood_group", "phone", "date_of_birth", "address", "last_donation_date", "is_eligible"], "columns": ["full_name", "blood_group", "phone", "last_donation_date", "is_eligible"]},
    "blood-units": {"model": BloodUnit, "title": "Blood Inventory", "singular": "Blood Unit", "fields": ["unit_number", "donor", "blood_group", "component", "collection_date", "expiry_date", "status"], "columns": ["unit_number", "blood_group", "component", "expiry_date", "status"]},
    "blood-requests": {"model": BloodRequest, "title": "Blood Requests", "singular": "Blood Request", "fields": ["patient", "requested_by", "blood_group", "component", "units_required", "priority", "status", "notes"], "columns": ["patient", "blood_group", "component", "units_required", "priority", "status"]},
    "appointments": {"model": Appointment, "title": "Appointments", "singular": "Appointment", "fields": ["patient", "doctor", "department", "scheduled_at", "reason", "status"], "columns": ["patient", "doctor", "department", "scheduled_at", "status"]},
    "encounters": {"model": Encounter, "title": "Medical Records", "singular": "Medical Record", "fields": ["patient", "doctor", "appointment", "chief_complaint", "diagnosis", "treatment_plan", "notes"], "columns": ["patient", "doctor", "diagnosis", "recorded_at"]},
    "vitals": {"model": VitalSign, "title": "Nursing Vitals", "singular": "Vital Record", "fields": ["patient", "recorded_by", "temperature_celsius", "pulse_rate", "systolic_bp", "diastolic_bp", "oxygen_saturation", "weight_kg", "notes"], "columns": ["patient", "temperature_celsius", "pulse_rate", "oxygen_saturation", "recorded_at"]},
    "prescriptions": {"model": Prescription, "title": "E-Prescriptions", "singular": "Prescription", "fields": ["patient", "doctor", "encounter", "notes"], "columns": ["patient", "doctor", "encounter", "prescribed_at"]},
    "prescription-items": {"model": PrescriptionItem, "title": "Prescription Medicines", "singular": "Prescription Medicine", "fields": ["prescription", "medicine", "dosage", "frequency", "duration_days", "instructions"], "columns": ["prescription", "medicine", "dosage", "frequency", "duration_days"]},
    "consents": {"model": ConsentRecord, "title": "Patient Consents", "singular": "Consent Record", "fields": ["patient", "consent_type", "signed_by", "document", "notes"], "columns": ["patient", "consent_type", "signed_by", "signed_at"]},
    "beds": {"model": Bed, "title": "IPD Beds", "singular": "Bed", "fields": ["ward", "bed_number", "is_occupied"], "columns": ["ward", "bed_number", "is_occupied"]},
    "admissions": {"model": Admission, "title": "IPD Admissions", "singular": "Admission", "fields": ["patient", "bed", "attending_doctor", "diagnosis", "discharged_at"], "columns": ["patient", "bed", "attending_doctor", "admitted_at", "discharged_at"]},
    "emergency-cases": {"model": EmergencyCase, "title": "Emergency & Triage", "singular": "Emergency Case", "fields": ["patient", "temporary_patient_name", "triage_level", "chief_complaint", "assigned_doctor", "status", "notes"], "columns": ["patient", "temporary_patient_name", "triage_level", "assigned_doctor", "status"]},
    "ambulances": {"model": Ambulance, "title": "Ambulance Fleet", "singular": "Ambulance", "fields": ["vehicle_number", "driver_name", "driver_phone", "status", "last_known_location"], "columns": ["vehicle_number", "driver_name", "driver_phone", "status", "last_known_location"]},
    "ambulance-dispatches": {"model": AmbulanceDispatch, "title": "Ambulance Dispatches", "singular": "Ambulance Dispatch", "fields": ["ambulance", "emergency_case", "pickup_location", "contact_phone", "status", "arrived_at"], "columns": ["ambulance", "emergency_case", "contact_phone", "status", "dispatched_at"]},
    "discharges": {"model": DischargeSummary, "title": "Discharge Summaries", "singular": "Discharge Summary", "fields": ["admission", "prepared_by", "final_diagnosis", "treatment_summary", "discharge_instructions", "follow_up_date"], "columns": ["admission", "prepared_by", "follow_up_date", "created_at"]},
    "operations": {"model": OperationSchedule, "title": "Operation Theatre", "singular": "Operation Schedule", "fields": ["patient", "surgeon", "scheduled_at", "operating_room", "procedure_name", "anaesthetist", "status", "pre_op_notes"], "columns": ["patient", "surgeon", "scheduled_at", "operating_room", "status"]},
    "invoices": {"model": Invoice, "title": "Billing & GST", "singular": "Invoice", "fields": ["patient", "invoice_number", "subtotal", "gst_amount", "paid_amount"], "columns": ["invoice_number", "patient", "subtotal", "gst_amount", "paid_amount", "issued_at"]},
    "payments": {"model": Payment, "title": "Payment Receipts", "singular": "Payment", "fields": ["invoice", "amount", "method", "reference_number"], "columns": ["invoice", "amount", "method", "reference_number", "received_at"]},
    "insurance-claims": {"model": InsuranceClaim, "title": "Insurance & TPA Claims", "singular": "Insurance Claim", "fields": ["patient", "invoice", "insurer_name", "policy_number", "claim_number", "claim_amount", "status", "submitted_at"], "columns": ["claim_number", "patient", "insurer_name", "claim_amount", "status"]},
    "medicines": {"model": Medicine, "title": "Pharmacy Inventory", "singular": "Medicine", "fields": ["name", "batch_number", "expiry_date", "quantity_in_stock", "reorder_level", "unit_price"], "columns": ["name", "batch_number", "expiry_date", "quantity_in_stock", "reorder_level"]},
    "suppliers": {"model": Supplier, "title": "Pharmacy Suppliers", "singular": "Supplier", "fields": ["name", "contact_person", "phone", "email", "gstin", "address"], "columns": ["name", "contact_person", "phone", "gstin"]},
    "purchase-orders": {"model": PurchaseOrder, "title": "Pharmacy Purchase Orders", "singular": "Purchase Order", "fields": ["order_number", "supplier", "expected_delivery_date", "total_amount", "status", "notes"], "columns": ["order_number", "supplier", "order_date", "total_amount", "status"]},
    "lab-reports": {"model": LabReport, "title": "Laboratory Reports", "singular": "Lab Report", "fields": ["patient", "ordered_by", "test_name", "report_pdf"], "columns": ["patient", "test_name", "ordered_by", "reported_at"]},
    "lab-orders": {"model": LabTestOrder, "title": "Laboratory Test Orders", "singular": "Lab Test Order", "fields": ["patient", "ordered_by", "test_name", "priority", "status", "sample_collected_at"], "columns": ["patient", "test_name", "priority", "status", "ordered_at"]},
    "notifications": {"model": Notification, "title": "Notification Centre", "singular": "Notification", "fields": ["patient", "recipient", "channel", "subject", "message", "status", "sent_at"], "columns": ["recipient", "channel", "subject", "status", "created_at"]},
    "departments": {"model": Department, "title": "Departments", "singular": "Department", "fields": ["name", "code"], "columns": ["name", "code"]},
    "doctor-schedules": {"model": DoctorSchedule, "title": "Doctor Schedules", "singular": "Doctor Schedule", "fields": ["doctor", "day_of_week", "start_time", "end_time", "slot_duration_minutes", "max_patients", "is_active"], "columns": ["doctor", "day_of_week", "start_time", "end_time", "is_active"]},
    "doctor-leaves": {"model": DoctorLeave, "title": "Doctor Leave Requests", "singular": "Doctor Leave", "fields": ["doctor", "start_date", "end_date", "reason", "status"], "columns": ["doctor", "start_date", "end_date", "status"]},
    "opd-tokens": {"model": OpdToken, "title": "OPD Queue Tokens", "singular": "OPD Token", "fields": ["token_number", "patient", "doctor", "department", "date", "status"], "columns": ["token_number", "patient", "doctor", "department", "status"]},
    "radiology": {"model": RadiologyReport, "title": "Radiology & Imaging", "singular": "Radiology Report", "fields": ["patient", "ordered_by", "radiologist", "modality", "body_part", "findings", "impression", "image_file", "status"], "columns": ["patient", "modality", "body_part", "status", "created_at"]},
    "patient-documents": {"model": PatientDocument, "title": "Patient Document Vault", "singular": "Patient Document", "fields": ["patient", "title", "document_type", "file"], "columns": ["patient", "title", "document_type", "uploaded_at"]},
    "nursing-notes": {"model": NursingNote, "title": "Nursing Shift Notes", "singular": "Nursing Note", "fields": ["patient", "nurse", "note"], "columns": ["patient", "nurse", "recorded_at"]},
    "medication-logs": {"model": MedicationAdministrationLog, "title": "Medication Logs", "singular": "Medication Log", "fields": ["patient", "administered_by", "medicine", "dosage", "notes"], "columns": ["patient", "medicine", "dosage", "administered_by", "administered_at"]},
    "payment-transactions": {"model": PaymentGatewayTransaction, "title": "Payment Gateways", "singular": "Gateway Transaction", "fields": ["invoice", "gateway", "transaction_id", "order_id", "amount", "currency", "status"], "columns": ["transaction_id", "invoice", "gateway", "amount", "status"]},
    "backup-logs": {"model": SystemBackupLog, "title": "System Backup Logs", "singular": "Backup Log", "fields": ["file_name", "file_size_bytes", "status"], "columns": ["file_name", "file_size_bytes", "status", "created_at"]},
}


@staff_required
def dashboard(request):
    today = timezone.localdate()
    today_revenue = Invoice.objects.filter(issued_at__date=today).aggregate(total=Sum("paid_amount"))["total"] or Decimal("0.00")
    appointments_today = Appointment.objects.filter(scheduled_at__date=today).count()

    total_beds = Bed.objects.count()
    occupied_beds = Bed.objects.filter(is_occupied=True).count()
    occupancy_pct = int((occupied_beds / total_beds) * 100) if total_beds > 0 else 0

    todays_appointments = Appointment.objects.select_related("patient", "doctor", "department").filter(scheduled_at__date=today).order_by("scheduled_at")[:10]
    low_stock = Medicine.objects.filter(quantity_in_stock__lte=10)[:5]
    recent_emergency = EmergencyCase.objects.select_related("patient").filter(status__in=["TRIAGED", "IN_PROGRESS"]).order_by("-arrival_time")[:5]

    active_resources = [{"slug": slug, "title": data["title"]} for slug, data in PORTAL_MODELS.items()]

    context = {
        "today_revenue": today_revenue,
        "appointments_today": appointments_today,
        "occupied_beds": occupied_beds,
        "total_beds": total_beds,
        "occupancy_pct": occupancy_pct,
        "todays_appointments": todays_appointments,
        "low_stock": low_stock,
        "recent_emergency": recent_emergency,
        "active_resources": active_resources,
    }
    return render(request, "portal/dashboard.html", context)


@staff_required
def resource_list(request, resource):
    if resource not in PORTAL_MODELS:
        raise Http404("Resource module not found.")

    cfg = PORTAL_MODELS[resource]
    model_cls = cfg["model"]
    query = request.GET.get("q", "").strip()

    items = model_cls.objects.all()
    if query:
        search_filter = Q()
        for field in cfg["columns"]:
            if hasattr(model_cls, field):
                model_field = model_cls._meta.get_field(field)
                if model_field.is_relation:
                    search_filter |= Q(**{f"{field}__first_name__icontains": query}) | Q(**{f"{field}__name__icontains": query})
                else:
                    search_filter |= Q(**{f"{field}__icontains": query})
        items = items.filter(search_filter)

    items = items.order_by("-pk")[:100]

    processed_items = []
    for item in items:
        row = {"id": item.pk, "obj": item, "cells": []}
        for col in cfg["columns"]:
            val = getattr(item, col, "")
            if callable(val):
                val = val()
            row["cells"].append(val)
        processed_items.append(row)

    context = {
        "resource": resource,
        "cfg": cfg,
        "query": query,
        "items": processed_items,
        "active_resources": [{"slug": slug, "title": data["title"]} for slug, data in PORTAL_MODELS.items()],
    }
    return render(request, "portal/resource_list.html", context)


@staff_required
def resource_form(request, resource, object_id=None):
    if resource not in PORTAL_MODELS:
        raise Http404("Resource module not found.")

    cfg = PORTAL_MODELS[resource]
    model_cls = cfg["model"]
    instance = get_object_or_404(model_cls, pk=object_id) if object_id else None

    FormClass = hospital_form(model_cls, cfg["fields"])

    if request.method == "POST":
        form = FormClass(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            saved_obj = form.save()
            messages.success(request, f"Successfully saved {cfg['singular']} #{saved_obj.pk}.")
            return redirect("portal-resource-list", resource=resource)
        else:
            messages.error(request, "Please correct errors in the form below.")
    else:
        form = FormClass(instance=instance)

    context = {
        "resource": resource,
        "cfg": cfg,
        "instance": instance,
        "form": form,
        "active_resources": [{"slug": slug, "title": data["title"]} for slug, data in PORTAL_MODELS.items()],
    }
    return render(request, "portal/resource_form.html", context)


@staff_required
def resource_delete(request, resource, object_id):
    if resource not in PORTAL_MODELS:
        raise Http404("Resource module not found.")

    cfg = PORTAL_MODELS[resource]
    instance = get_object_or_404(cfg["model"], pk=object_id)

    if request.method == "POST":
        try:
            instance.delete()
            messages.success(request, f"Successfully deleted {cfg['singular']} #{object_id}.")
        except ProtectedError:
            messages.error(request, f"Cannot delete {cfg['singular']} #{object_id} because it is referenced by active clinical records.")
        return redirect("portal-resource-list", resource=resource)

    context = {
        "resource": resource,
        "cfg": cfg,
        "instance": instance,
        "active_resources": [{"slug": slug, "title": data["title"]} for slug, data in PORTAL_MODELS.items()],
    }
    return render(request, "portal/confirm_delete.html", context)


@staff_required
def patient_card(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    return render(request, "portal/patient_card.html", {"patient": patient})


@staff_required
def patient_qr(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    try:
        import qrcode

        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(patient.qr_value)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return HttpResponse(buffer.getvalue(), content_type="image/png")
    except Exception:
        svg_qr = f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="#f8fafc"/><text x="10" y="100" font-family="sans-serif" font-size="12" fill="#0f172a">{patient.patient_code}</text></svg>'
        return HttpResponse(svg_qr, content_type="image/svg+xml")


@staff_required
def reports(request):
    today = timezone.localdate()
    start_of_month = today.replace(day=1)

    revenue_by_day = list(Invoice.objects.filter(issued_at__date__gte=start_of_month).values("issued_at__date").annotate(daily_total=Sum("paid_amount")).order_by("issued_at__date"))
    doctor_volume = list(Appointment.objects.values("doctor__username").annotate(total_appointments=Count("id")).order_by("-total_appointments"))
    department_volume = list(Appointment.objects.values("department__name").annotate(total_appointments=Count("id")).order_by("-total_appointments"))

    context = {
        "revenue_by_day": revenue_by_day,
        "doctor_volume": doctor_volume,
        "department_volume": department_volume,
        "active_resources": [{"slug": slug, "title": data["title"]} for slug, data in PORTAL_MODELS.items()],
    }
    return render(request, "portal/reports.html", context)


@staff_required
def download_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, 750, "CarePoint Health Systems Ltd.")
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, "Official GST Medical Invoice")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 700, f"Invoice #: {invoice.invoice_number}")
    p.drawString(50, 680, f"Date: {invoice.issued_at.strftime('%d-%b-%Y')}")
    p.drawString(50, 660, f"Patient: {invoice.patient}")

    p.line(50, 640, 550, 640)

    p.drawString(50, 610, f"Subtotal: INR {invoice.subtotal:.2f}")
    p.drawString(50, 590, f"GST Amount (18%): INR {invoice.gst_amount:.2f}")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 560, f"Total Amount Paid: INR {(invoice.subtotal + invoice.gst_amount):.2f}")

    p.setFont("Helvetica-Oblique", 9)
    p.drawString(50, 500, "This is a computer-generated tax invoice and requires no physical signature.")
    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
    return response


@staff_required
def download_prescription_pdf(request, prescription_id):
    prescription = get_object_or_404(Prescription, pk=prescription_id)
    items = prescription.items.all()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, 750, "CarePoint Health Systems Ltd.")
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, "Digital E-Prescription Slip")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 700, f"Patient: {prescription.patient}")
    p.drawString(50, 680, f"Attending Doctor: Dr. {prescription.doctor.username}")
    p.drawString(50, 660, f"Date: {prescription.prescribed_at.strftime('%d-%b-%Y %H:%M')}")

    p.line(50, 640, 550, 640)

    y = 610
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Prescribed Medicines:")
    y -= 25

    p.setFont("Helvetica", 10)
    for item in items:
        p.drawString(60, y, f"- {item.medicine.name} | Dosage: {item.dosage} | Frequency: {item.frequency} | Duration: {item.duration_days} days")
        y -= 20

    if prescription.notes:
        y -= 15
        p.setFont("Helvetica-Bold", 11)
        p.drawString(50, y, "Doctor Notes:")
        y -= 20
        p.setFont("Helvetica", 10)
        p.drawString(60, y, prescription.notes)

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Prescription_{prescription.id}.pdf"'
    return response


@staff_required
def download_discharge_pdf(request, discharge_id):
    discharge = get_object_or_404(DischargeSummary, pk=discharge_id)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, 750, "CarePoint Health Systems Ltd.")
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, "Inpatient Discharge Summary")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 700, f"Patient: {discharge.admission.patient}")
    p.drawString(50, 680, f"Prepared By: Dr. {discharge.prepared_by.username}")
    p.drawString(50, 660, f"Follow-up Date: {discharge.follow_up_date.strftime('%d-%b-%Y') if discharge.follow_up_date else 'N/A'}")

    p.line(50, 640, 550, 640)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, 610, "Final Diagnosis:")
    p.setFont("Helvetica", 10)
    p.drawString(60, 590, discharge.final_diagnosis)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, 560, "Treatment Summary:")
    p.setFont("Helvetica", 10)
    p.drawString(60, 540, discharge.treatment_summary)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, 510, "Discharge Instructions:")
    p.setFont("Helvetica", 10)
    p.drawString(60, 490, discharge.discharge_instructions)

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Discharge_Summary_{discharge.id}.pdf"'
    return response


@staff_required
def export_revenue_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Revenue Audit"

    ws.append(["Invoice Number", "Patient Name", "Subtotal (INR)", "GST Amount (INR)", "Paid Amount (INR)", "Issued Date"])

    for inv in Invoice.objects.select_related("patient").all().order_by("-issued_at"):
        ws.append([
            inv.invoice_number,
            str(inv.patient),
            float(inv.subtotal),
            float(inv.gst_amount),
            float(inv.paid_amount),
            inv.issued_at.strftime("%Y-%m-%d %H:%M"),
        ])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="CarePoint_Revenue_Report.xlsx"'
    return response


@staff_required
def export_patients_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="CarePoint_Patients_Directory.csv"'

    writer = csv.writer(response)
    writer.writerow(["Patient Code", "First Name", "Last Name", "DOB", "Sex", "Phone", "Blood Group", "Insurance Provider"])

    for p in Patient.objects.all().order_by("first_name"):
        writer.writerow([str(p.patient_code), p.first_name, p.last_name, str(p.date_of_birth), p.sex, p.phone, p.blood_group, p.insurance_provider])

    return response


@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        if "update_profile" in request.POST:
            user.first_name = request.POST.get("first_name", user.first_name)
            user.last_name = request.POST.get("last_name", user.last_name)
            user.email = request.POST.get("email", user.email)
            user.phone = request.POST.get("phone", user.phone)
            user.save()
            messages.success(request, "Your profile details have been updated.")
        elif "change_password" in request.POST:
            old_pass = request.POST.get("old_password")
            new_pass = request.POST.get("new_password")
            if user.check_password(old_pass):
                user.set_password(new_pass)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been changed successfully.")
            else:
                messages.error(request, "Current password is invalid.")
        return redirect("profile-view")

    context = {
        "user": user,
        "active_resources": [{"slug": slug, "title": data["title"]} for slug, data in PORTAL_MODELS.items()],
    }
    return render(request, "portal/profile.html", context)


@staff_required
def analytics_view(request):
    today = timezone.localdate()
    start_of_month = today.replace(day=1)

    daily_revenue = list(Invoice.objects.filter(issued_at__date__gte=start_of_month).values("issued_at__date").annotate(total=Sum("paid_amount")).order_by("issued_at__date"))
    doctor_volume = list(Appointment.objects.values("doctor__username").annotate(total_appointments=Count("id")).order_by("-total_appointments"))

    context = {
        "daily_revenue": daily_revenue,
        "doctor_volume": doctor_volume,
        "active_resources": [{"slug": slug, "title": data["title"]} for slug, data in PORTAL_MODELS.items()],
    }
    return render(request, "portal/analytics.html", context)
