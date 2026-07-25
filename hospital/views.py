from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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
    EmergencyCase,
    Encounter,
    InsuranceClaim,
    Invoice,
    LabReport,
    LabTestOrder,
    Medicine,
    Notification,
    OperationSchedule,
    Patient,
    Payment,
    Prescription,
    PrescriptionItem,
    PurchaseOrder,
    Supplier,
    VitalSign,
)
from .permissions import CanManageBilling, CanManageClinicalRecords, CanManagePatients, CanManagePharmacy
from .serializers import (
    AdmissionSerializer,
    AmbulanceDispatchSerializer,
    AmbulanceSerializer,
    AppointmentSerializer,
    BedSerializer,
    BloodDonorSerializer,
    BloodRequestSerializer,
    BloodUnitSerializer,
    ConsentRecordSerializer,
    DepartmentSerializer,
    DischargeSummarySerializer,
    EmergencyCaseSerializer,
    EncounterSerializer,
    InsuranceClaimSerializer,
    InvoiceSerializer,
    LabReportSerializer,
    LabTestOrderSerializer,
    MedicineSerializer,
    NotificationSerializer,
    OperationScheduleSerializer,
    PatientSerializer,
    PaymentSerializer,
    PrescriptionItemSerializer,
    PrescriptionSerializer,
    PurchaseOrderSerializer,
    SupplierSerializer,
    VitalSignSerializer,
)


class RestrictedViewSet(ModelViewSet):
    permission_classes = [CanManagePatients]


class DepartmentViewSet(RestrictedViewSet):
    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer


class PatientViewSet(RestrictedViewSet):
    queryset = Patient.objects.all().order_by("-created_at")
    serializer_class = PatientSerializer


class AppointmentViewSet(RestrictedViewSet):
    queryset = Appointment.objects.select_related("patient", "doctor", "department").all().order_by("-scheduled_at")
    serializer_class = AppointmentSerializer


class BloodDonorViewSet(RestrictedViewSet):
    queryset = BloodDonor.objects.all().order_by("-created_at")
    serializer_class = BloodDonorSerializer


class AmbulanceViewSet(RestrictedViewSet):
    queryset = Ambulance.objects.all().order_by("vehicle_number")
    serializer_class = AmbulanceSerializer


class EmergencyCaseViewSet(RestrictedViewSet):
    queryset = EmergencyCase.objects.select_related("patient", "assigned_doctor").all().order_by("-arrival_time")
    serializer_class = EmergencyCaseSerializer


class AmbulanceDispatchViewSet(RestrictedViewSet):
    queryset = AmbulanceDispatch.objects.select_related("ambulance", "emergency_case").all().order_by("-dispatched_at")
    serializer_class = AmbulanceDispatchSerializer


class NotificationViewSet(RestrictedViewSet):
    queryset = Notification.objects.select_related("patient").all().order_by("-created_at")
    serializer_class = NotificationSerializer


class EncounterViewSet(ModelViewSet):
    queryset = Encounter.objects.select_related("patient", "doctor").all().order_by("-recorded_at")
    serializer_class = EncounterSerializer
    permission_classes = [CanManageClinicalRecords]


class VitalSignViewSet(ModelViewSet):
    queryset = VitalSign.objects.select_related("patient", "recorded_by").all().order_by("-recorded_at")
    serializer_class = VitalSignSerializer
    permission_classes = [CanManageClinicalRecords]


class PrescriptionViewSet(ModelViewSet):
    queryset = Prescription.objects.select_related("patient", "doctor", "encounter").all().order_by("-prescribed_at")
    serializer_class = PrescriptionSerializer
    permission_classes = [CanManageClinicalRecords]


class PrescriptionItemViewSet(ModelViewSet):
    queryset = PrescriptionItem.objects.select_related("prescription", "medicine").all().order_by("-pk")
    serializer_class = PrescriptionItemSerializer
    permission_classes = [CanManageClinicalRecords]


class ConsentRecordViewSet(ModelViewSet):
    queryset = ConsentRecord.objects.select_related("patient").all().order_by("-signed_at")
    serializer_class = ConsentRecordSerializer
    permission_classes = [CanManageClinicalRecords]


class BedViewSet(RestrictedViewSet):
    queryset = Bed.objects.all().order_by("ward", "bed_number")
    serializer_class = BedSerializer


class AdmissionViewSet(ModelViewSet):
    queryset = Admission.objects.select_related("patient", "bed", "attending_doctor").all().order_by("-admitted_at")
    serializer_class = AdmissionSerializer
    permission_classes = [CanManageClinicalRecords]

    @transaction.atomic
    def perform_create(self, serializer):
        bed = Bed.objects.select_for_update().get(pk=serializer.validated_data["bed"].pk)
        if bed.is_occupied:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"bed": "This bed is already occupied."})
        bed.is_occupied = True
        bed.save(update_fields=["is_occupied"])
        serializer.save()


class DischargeSummaryViewSet(ModelViewSet):
    queryset = DischargeSummary.objects.select_related("admission", "prepared_by").all().order_by("-created_at")
    serializer_class = DischargeSummarySerializer
    permission_classes = [CanManageClinicalRecords]


class OperationScheduleViewSet(ModelViewSet):
    queryset = OperationSchedule.objects.select_related("patient", "surgeon").all().order_by("-scheduled_at")
    serializer_class = OperationScheduleSerializer
    permission_classes = [CanManageClinicalRecords]


class LabReportViewSet(ModelViewSet):
    queryset = LabReport.objects.select_related("patient", "ordered_by").all().order_by("-reported_at")
    serializer_class = LabReportSerializer
    permission_classes = [CanManageClinicalRecords]


class LabTestOrderViewSet(ModelViewSet):
    queryset = LabTestOrder.objects.select_related("patient", "ordered_by").all().order_by("-ordered_at")
    serializer_class = LabTestOrderSerializer
    permission_classes = [CanManageClinicalRecords]


class InvoiceViewSet(ModelViewSet):
    queryset = Invoice.objects.select_related("patient").all().order_by("-issued_at")
    serializer_class = InvoiceSerializer
    permission_classes = [CanManageBilling]


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.select_related("invoice").all().order_by("-received_at")
    serializer_class = PaymentSerializer
    permission_classes = [CanManageBilling]


class InsuranceClaimViewSet(ModelViewSet):
    queryset = InsuranceClaim.objects.select_related("patient", "invoice").all().order_by("-pk")
    serializer_class = InsuranceClaimSerializer
    permission_classes = [CanManageBilling]


class MedicineViewSet(ModelViewSet):
    queryset = Medicine.objects.all().order_by("name", "expiry_date")
    serializer_class = MedicineSerializer
    permission_classes = [CanManagePharmacy]


class BloodUnitViewSet(ModelViewSet):
    queryset = BloodUnit.objects.select_related("donor").all().order_by("expiry_date")
    serializer_class = BloodUnitSerializer
    permission_classes = [CanManagePharmacy]


class BloodRequestViewSet(ModelViewSet):
    queryset = BloodRequest.objects.select_related("patient", "requested_by").all().order_by("-requested_at")
    serializer_class = BloodRequestSerializer
    permission_classes = [CanManagePharmacy]


class SupplierViewSet(ModelViewSet):
    queryset = Supplier.objects.all().order_by("name")
    serializer_class = SupplierSerializer
    permission_classes = [CanManagePharmacy]


class PurchaseOrderViewSet(ModelViewSet):
    queryset = PurchaseOrder.objects.select_related("supplier").all().order_by("-order_date")
    serializer_class = PurchaseOrderSerializer
    permission_classes = [CanManagePharmacy]


class ReportViewSet(RestrictedViewSet):
    queryset = Patient.objects.none()

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        today = timezone.localdate()
        return Response({
            "today_revenue": Invoice.objects.filter(issued_at__date=today).aggregate(total=Sum("paid_amount"))["total"] or 0,
            "appointments_today": Appointment.objects.filter(scheduled_at__date=today).count(),
            "bed_occupancy": {"occupied": Bed.objects.filter(is_occupied=True).count(), "total": Bed.objects.count()},
            "low_stock": list(Medicine.objects.filter(quantity_in_stock__lte=10).values("id", "name", "quantity_in_stock")),
            "doctor_patient_counts": list(Appointment.objects.values("doctor__username").annotate(patients=Count("patient", distinct=True)).order_by("-patients")),
        })
