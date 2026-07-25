from datetime import date

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Ambulance, Bed, BloodDonor, EmergencyCase, Patient, User
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

    def test_emergency_case_creation_and_list(self):
        url = reverse("portal-resource-create", kwargs={"resource": "emergency-cases"})
        response = self.client.post(url, {
            "temporary_patient_name": "John Doe Triage",
            "triage_level": "RED",
            "chief_complaint": "Chest Pain",
            "status": "ARRIVED",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EmergencyCase.objects.filter(temporary_patient_name="John Doe Triage").exists())

    def test_ambulance_creation(self):
        url = reverse("portal-resource-create", kwargs={"resource": "ambulances"})
        response = self.client.post(url, {
            "vehicle_number": "AMB-101",
            "driver_name": "Rajesh Kumar",
            "driver_phone": "9876543210",
            "status": "AVAILABLE",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ambulance.objects.filter(vehicle_number="AMB-101").exists())

    def test_blood_donor_creation(self):
        url = reverse("portal-resource-create", kwargs={"resource": "blood-donors"})
        response = self.client.post(url, {
            "full_name": "Vikram Singh",
            "blood_group": "O+",
            "phone": "9123456789",
            "date_of_birth": "1995-05-15",
            "is_eligible": True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BloodDonor.objects.filter(phone="9123456789").exists())
