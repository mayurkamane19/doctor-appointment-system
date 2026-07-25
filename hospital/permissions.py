from rest_framework.permissions import BasePermission
from rest_framework.viewsets import ModelViewSet


class HasHospitalRole(BasePermission):
    allowed_roles = set()

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == "ADMIN" or request.user.is_superuser:
            return True
        return request.user.role in self.allowed_roles


class CanManagePatients(HasHospitalRole):
    allowed_roles = {"ADMIN", "DOCTOR", "NURSE", "RECEPTIONIST"}


class CanManageClinicalRecords(HasHospitalRole):
    allowed_roles = {"ADMIN", "DOCTOR", "NURSE", "RADIOLOGIST", "LAB_TECHNICIAN"}


class CanManageBilling(HasHospitalRole):
    allowed_roles = {"ADMIN", "RECEPTIONIST", "ACCOUNTANT"}


class CanManagePharmacy(HasHospitalRole):
    allowed_roles = {"ADMIN", "PHARMACIST"}


class CanManageMasterData(HasHospitalRole):
    allowed_roles = {"ADMIN", "DOCTOR", "RECEPTIONIST", "ACCOUNTANT"}


class RestrictedViewSet(ModelViewSet):
    permission_classes = [CanManageMasterData]
