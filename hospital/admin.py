from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Admission, Ambulance, AmbulanceDispatch, Appointment, AuditLog, Bed, BloodDonor, BloodRequest, BloodUnit, ConsentRecord, Department, DischargeSummary, EmergencyCase, Encounter, InsuranceClaim, Invoice, LabReport, LabTestOrder, Medicine, Notification, OperationSchedule, Patient, Payment, Prescription, PrescriptionItem, PurchaseOrder, Supplier, User, VitalSign

admin.site.register(User, UserAdmin)
admin.site.register([Department, Patient, BloodDonor, BloodUnit, BloodRequest, Appointment, Encounter, VitalSign, Prescription, PrescriptionItem, ConsentRecord, Bed, Admission, EmergencyCase, Ambulance, AmbulanceDispatch, DischargeSummary, OperationSchedule, Invoice, Payment, InsuranceClaim, Medicine, Supplier, PurchaseOrder, LabReport, LabTestOrder, Notification, AuditLog])
