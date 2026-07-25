import io
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import Count, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import hospital_form
from .models import Admission, Ambulance, AmbulanceDispatch, Appointment, Bed, BloodDonor, BloodRequest, BloodUnit, ConsentRecord, Department, DischargeSummary, EmergencyCase, Encounter, InsuranceClaim, Invoice, LabReport, LabTestOrder, Medicine, Notification, OperationSchedule, Patient, Payment, Prescription, PrescriptionItem, PurchaseOrder, Supplier, VitalSign


def staff_required(view):
    return user_passes_test(lambda account: account.is_staff, login_url="/admin/login/")(view)


PORTAL_MODELS = {
    "patients": {"model": Patient, "title": "Patients", "singular": "Patient", "fields": ["first_name", "last_name", "date_of_birth", "sex", "phone", "email", "address", "blood_group", "emergency_contact_name", "emergency_contact_phone"], "columns": ["patient_code", "first_name", "last_name", "phone", "blood_group"]},
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
}


def _config(resource):
    if resource not in PORTAL_MODELS:
        raise Http404("Unknown hospital resource")
    return PORTAL_MODELS[resource]


def _display(value):
    if value is None or value == "":
        return "—"
    if isinstance(value, bool):
        return "Occupied" if value else "Available"
    return str(value)


@staff_required
def dashboard(request):
    today = timezone.localdate()
    occupied_beds = Bed.objects.filter(is_occupied=True).count()
    total_beds = Bed.objects.count()
    revenue = Invoice.objects.filter(issued_at__date=today).aggregate(total=Sum("paid_amount"))["total"] or Decimal("0")
    context = {
        "appointments_today": Appointment.objects.filter(scheduled_at__date=today).count(),
        "admitted_patients": Admission.objects.filter(discharged_at__isnull=True).count(),
        "occupied_beds": occupied_beds,
        "total_beds": total_beds,
        "occupancy": round((occupied_beds / total_beds * 100) if total_beds else 0),
        "today_revenue": revenue,
        "appointments": Appointment.objects.filter(scheduled_at__date=today).select_related("patient", "doctor", "department").order_by("scheduled_at")[:5],
        "low_stock": Medicine.objects.filter(quantity_in_stock__lte=10).order_by("quantity_in_stock")[:5],
        "pending_reports": LabReport.objects.filter(reported_at__date=today).count(),
    }
    return render(request, "portal/dashboard.html", context)


@staff_required
def resource_list(request, resource):
    config = _config(resource)
    objects = config["model"].objects.all().order_by("-pk")
    query = request.GET.get("q", "").strip()
    if query:
        searchable = []
        for field in config["fields"]:
            try:
                f = config["model"]._meta.get_field(field)
                if f.get_internal_type() in {"CharField", "TextField", "EmailField"}:
                    searchable.append(field)
            except Exception:
                pass
        if searchable:
            from django.db.models import Q
            filters = Q()
            for field in searchable:
                filters |= Q(**{f"{field}__icontains": query})
            objects = objects.filter(filters)
    rows = [{"object": item, "values": [_display(getattr(item, column)) for column in config["columns"]]} for item in objects]
    return render(request, "portal/resource_list.html", {"config": config, "resource": resource, "rows": rows, "query": query})


@staff_required
def resource_form(request, resource, object_id=None):
    config = _config(resource)
    object_instance = get_object_or_404(config["model"], pk=object_id) if object_id else None
    form_class = hospital_form(config["model"], config["fields"])
    form = form_class(request.POST or None, request.FILES or None, instance=object_instance)
    if form.is_valid():
        with transaction.atomic():
            if resource == "admissions" and not object_instance:
                selected_bed = Bed.objects.select_for_update().get(pk=form.cleaned_data["bed"].pk)
                if selected_bed.is_occupied:
                    form.add_error("bed", "This bed is already occupied.")
                    return render(request, "portal/resource_form.html", {"form": form, "config": config, "resource": resource, "object": object_instance})
                selected_bed.is_occupied = True
                selected_bed.save(update_fields=["is_occupied"])
            saved_object = form.save()
            if resource == "discharges":
                admission = saved_object.admission
                if admission.discharged_at is None:
                    admission.discharged_at = timezone.now()
                    admission.save(update_fields=["discharged_at"])
                    admission.bed.is_occupied = False
                    admission.bed.save(update_fields=["is_occupied"])
        messages.success(request, f"{config['singular']} saved successfully.")
        return redirect("portal-resource-list", resource=resource)
    return render(request, "portal/resource_form.html", {"form": form, "config": config, "resource": resource, "object": object_instance})


@staff_required
def resource_delete(request, resource, object_id):
    config = _config(resource)
    object_instance = get_object_or_404(config["model"], pk=object_id)
    if request.method == "POST":
        try:
            with transaction.atomic():
                if resource == "admissions" and object_instance.discharged_at is None:
                    object_instance.bed.is_occupied = False
                    object_instance.bed.save(update_fields=["is_occupied"])
                object_instance.delete()
            messages.success(request, f"{config['singular']} deleted.")
        except Exception:
            messages.error(request, f"Cannot delete this {config['singular'].lower()} as it is referenced by other records.")
        return redirect("portal-resource-list", resource=resource)
    return render(request, "portal/confirm_delete.html", {"config": config, "resource": resource, "object": object_instance})


@staff_required
def patient_qr(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    try:
        import qrcode

        qr_image = qrcode.make(f"CAREPOINT-PATIENT:{patient.patient_code}")
        output = io.BytesIO()
        qr_image.save(output, format="PNG")
        return HttpResponse(output.getvalue(), content_type="image/png")
    except Exception:
        code_str = str(patient.patient_code)[:8]
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
            <rect width="200" height="200" fill="#ffffff" stroke="#0ea5e9" stroke-width="4"/>
            <rect x="20" y="20" width="50" height="50" fill="#0f172a"/>
            <rect x="30" y="30" width="30" height="30" fill="#ffffff"/>
            <rect x="40" y="40" width="10" height="10" fill="#0f172a"/>
            <rect x="130" y="20" width="50" height="50" fill="#0f172a"/>
            <rect x="140" y="30" width="30" height="30" fill="#ffffff"/>
            <rect x="150" y="40" width="10" height="10" fill="#0f172a"/>
            <rect x="20" y="130" width="50" height="50" fill="#0f172a"/>
            <rect x="30" y="140" width="30" height="30" fill="#ffffff"/>
            <rect x="40" y="150" width="10" height="10" fill="#0f172a"/>
            <text x="100" y="105" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle" fill="#0ea5e9">{code_str}</text>
        </svg>'''
        return HttpResponse(svg, content_type="image/svg+xml")


@staff_required
def patient_card(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    return render(request, "portal/patient_card.html", {"patient": patient})


@staff_required
def reports(request):
    context = {
        "revenue": Invoice.objects.aggregate(total=Sum("paid_amount"))["total"] or Decimal("0"),
        "outstanding": (Invoice.objects.aggregate(total=Sum("subtotal") + Sum("gst_amount") - Sum("paid_amount"))["total"] or Decimal("0")),
        "bed_occupancy": {"occupied": Bed.objects.filter(is_occupied=True).count(), "total": Bed.objects.count()},
        "doctor_patients": Appointment.objects.values("doctor__username").annotate(total=Count("patient", distinct=True)).order_by("-total"),
        "low_stock": Medicine.objects.filter(quantity_in_stock__lte=10).order_by("quantity_in_stock"),
    }
    return render(request, "portal/reports.html", context)
