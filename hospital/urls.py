from rest_framework.routers import DefaultRouter

from .views import (
    AdmissionViewSet,
    AmbulanceDispatchViewSet,
    AmbulanceViewSet,
    AppointmentViewSet,
    BedViewSet,
    BloodDonorViewSet,
    BloodRequestViewSet,
    BloodUnitViewSet,
    ConsentRecordViewSet,
    DepartmentViewSet,
    DischargeSummaryViewSet,
    DoctorLeaveViewSet,
    DoctorScheduleViewSet,
    EmergencyCaseViewSet,
    EncounterViewSet,
    InsuranceClaimViewSet,
    InvoiceViewSet,
    LabReportViewSet,
    LabTestOrderViewSet,
    MedicationAdministrationLogViewSet,
    MedicineViewSet,
    NotificationViewSet,
    NursingNoteViewSet,
    OpdTokenViewSet,
    OperationScheduleViewSet,
    PatientDocumentViewSet,
    PatientViewSet,
    PaymentGatewayTransactionViewSet,
    PaymentViewSet,
    PrescriptionItemViewSet,
    PrescriptionViewSet,
    PurchaseOrderViewSet,
    RadiologyReportViewSet,
    ReportViewSet,
    SupplierViewSet,
    SystemBackupLogViewSet,
    VitalSignViewSet,
)

router = DefaultRouter()
router.register("departments", DepartmentViewSet)
router.register("patients", PatientViewSet)
router.register("blood-donors", BloodDonorViewSet)
router.register("blood-units", BloodUnitViewSet)
router.register("blood-requests", BloodRequestViewSet)
router.register("appointments", AppointmentViewSet)
router.register("encounters", EncounterViewSet)
router.register("vitals", VitalSignViewSet)
router.register("prescriptions", PrescriptionViewSet)
router.register("prescription-items", PrescriptionItemViewSet)
router.register("consents", ConsentRecordViewSet)
router.register("beds", BedViewSet)
router.register("admissions", AdmissionViewSet)
router.register("emergency-cases", EmergencyCaseViewSet)
router.register("ambulances", AmbulanceViewSet)
router.register("ambulance-dispatches", AmbulanceDispatchViewSet)
router.register("discharges", DischargeSummaryViewSet)
router.register("operations", OperationScheduleViewSet)
router.register("invoices", InvoiceViewSet)
router.register("payments", PaymentViewSet)
router.register("insurance-claims", InsuranceClaimViewSet)
router.register("medicines", MedicineViewSet)
router.register("suppliers", SupplierViewSet)
router.register("purchase-orders", PurchaseOrderViewSet)
router.register("lab-reports", LabReportViewSet)
router.register("lab-orders", LabTestOrderViewSet)
router.register("notifications", NotificationViewSet)
router.register("doctor-schedules", DoctorScheduleViewSet)
router.register("doctor-leaves", DoctorLeaveViewSet)
router.register("opd-tokens", OpdTokenViewSet)
router.register("radiology-reports", RadiologyReportViewSet)
router.register("patient-documents", PatientDocumentViewSet)
router.register("nursing-notes", NursingNoteViewSet)
router.register("medication-logs", MedicationAdministrationLogViewSet)
router.register("payment-transactions", PaymentGatewayTransactionViewSet)
router.register("backup-logs", SystemBackupLogViewSet)
router.register("reports", ReportViewSet, basename="reports")

urlpatterns = router.urls

