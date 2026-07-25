from rest_framework.permissions import BasePermission


class HasHospitalRole(BasePermission):
    allowed_roles = set()

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in self.allowed_roles)


class CanManagePatients(HasHospitalRole):
    allowed_roles = {"ADMIN", "DOCTOR", "NURSE", "RECEPTIONIST"}


class CanManageClinicalRecords(HasHospitalRole):
    allowed_roles = {"ADMIN", "DOCTOR", "NURSE"}


class CanManageBilling(HasHospitalRole):
    allowed_roles = {"ADMIN", "RECEPTIONIST"}


class CanManagePharmacy(HasHospitalRole):
    allowed_roles = {"ADMIN", "PHARMACIST"}
