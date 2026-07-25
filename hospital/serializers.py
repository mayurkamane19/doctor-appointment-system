from rest_framework import serializers

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


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class PatientSerializer(serializers.ModelSerializer):
    qr_value = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ("patient_code", "created_at")


class BloodDonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodDonor
        fields = "__all__"
        read_only_fields = ("created_at",)


class BloodUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodUnit
        fields = "__all__"


class BloodRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = "__all__"
        read_only_fields = ("requested_at",)


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ("created_at",)


class EncounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encounter
        fields = "__all__"
        read_only_fields = ("recorded_at",)


class VitalSignSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSign
        fields = "__all__"
        read_only_fields = ("recorded_at",)


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = "__all__"
        read_only_fields = ("prescribed_at",)


class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = "__all__"


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = "__all__"
        read_only_fields = ("signed_at",)


class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bed
        fields = "__all__"


class AdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admission
        fields = "__all__"
        read_only_fields = ("admitted_at",)


class AmbulanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambulance
        fields = "__all__"
        read_only_fields = ("updated_at",)


class EmergencyCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyCase
        fields = "__all__"
        read_only_fields = ("arrival_time",)


class AmbulanceDispatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmbulanceDispatch
        fields = "__all__"
        read_only_fields = ("dispatched_at",)


class DischargeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DischargeSummary
        fields = "__all__"
        read_only_fields = ("created_at",)


class OperationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationSchedule
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ("issued_at",)

    def get_total(self, invoice):
        return invoice.subtotal + invoice.gst_amount


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("received_at",)


class InsuranceClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceClaim
        fields = "__all__"


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = "__all__"


class PrescriptionItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = "__all__"
        read_only_fields = ("order_date",)


class LabReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = "__all__"
        read_only_fields = ("reported_at",)


class LabTestOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTestOrder
        fields = "__all__"
        read_only_fields = ("ordered_at",)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("created_at",)


class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = "__all__"


class DoctorLeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorLeave
        fields = "__all__"


class OpdTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpdToken
        fields = "__all__"
        read_only_fields = ("created_at",)


class RadiologyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadiologyReport
        fields = "__all__"
        read_only_fields = ("created_at",)


class PatientDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDocument
        fields = "__all__"
        read_only_fields = ("uploaded_at",)


class NursingNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NursingNote
        fields = "__all__"
        read_only_fields = ("recorded_at",)


class MedicationAdministrationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationAdministrationLog
        fields = "__all__"
        read_only_fields = ("administered_at",)


class PaymentGatewayTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewayTransaction
        fields = "__all__"
        read_only_fields = ("created_at",)


class SystemBackupLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemBackupLog
        fields = "__all__"
        read_only_fields = ("created_at",)

