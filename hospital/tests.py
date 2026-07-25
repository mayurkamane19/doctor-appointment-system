from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Ambulance, Bed, BloodDonor, EmergencyCase, Invoice, Patient, User
from .portal import PORTAL_MODELS


class AdmissionAccessTests(APITestCase):
    def setUp(self):
        self.doctor = User.objects.create_user(username="doctor", password="safe-password", role=User.Role.DOCTOR, is_staff=True)
        self.receptionist = User.objects.create_user(username="reception", password="safe-password", role=User.Role.RECEPTIONIST, is_staff=True)
        self.patient = Patient.objects.create(first_name="Asha", date_of_birth=date(1990, 1, 1), sex="Female", phone="9999999999", emergency_contact_name="Ravi", emergency_contact_phone="9999999998")
        self.bed = Bed.objects.create(ward="General", bed_number="G-01")

    def test_receptionist_cannot_admit_patient(self):
        self.client.force_authenticate(self.receptionist)
        response = self.client.post(reverse("admission-list"), {"patient": self.patient.id, "bed": self.bed.id, "attending_doctor": self.doctor.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admission_marks_bed_as_occupied(self):
        self.client.force_authenticate(self.doctor)
        response = self.client.post(reverse("admission-list"), {"patient": self.patient.id, "bed": self.bed.id, "attending_doctor": self.doctor.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.bed.refresh_from_db()
        self.assertTrue(self.bed.is_occupied)


class PortalViewsTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(username="staffadmin", password="password123", is_staff=True, role=User.Role.ADMIN)
        self.client.force_login(self.staff_user)
        self.patient = Patient.objects.create(first_name="Test", last_name="Patient", date_of_birth=date(1992, 4, 10), sex="Male", phone="9888888888", emergency_contact_name="Contact", emergency_contact_phone="9777777777")
        self.invoice = Invoice.objects.create(patient=self.patient, invoice_number="INV-TEST-001", subtotal=Decimal("1000.00"), gst_amount=Decimal("180.00"), paid_amount=Decimal("1180.00"))

    def test_all_portal_resource_lists_return_200(self):
        for resource in PORTAL_MODELS:
            url = reverse("portal-resource-list", kwargs={"resource": resource})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Portal resource '{resource}' returned {response.status_code}")

    def test_all_portal_resource_create_forms_return_200(self):
        for resource in PORTAL_MODELS:
            url = reverse("portal-resource-create", kwargs={"resource": resource})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Portal form '{resource}' returned {response.status_code}")

    def test_invoice_pdf_download_returns_200(self):
        url = reverse("download-invoice-pdf", kwargs={"invoice_id": self.invoice.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_excel_revenue_export_returns_200(self):
        url = reverse("export-revenue-excel")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/vnd.openxmlformats-officedocument", response["Content-Type"])

    def test_csv_patients_export_returns_200(self):
        url = reverse("export-patients-csv")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_swagger_ui_returns_200(self):
        url = reverse("swagger-ui")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
