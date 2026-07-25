from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.shortcuts import render
from hospital import portal
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("", portal.dashboard, name="dashboard"),
    path("portal/patients/<int:patient_id>/qr/", portal.patient_qr, name="patient-qr"),
    path("portal/patients/<int:patient_id>/card/", portal.patient_card, name="patient-card"),
    path("portal/reports/", portal.reports, name="portal-reports"),
    path("portal/<str:resource>/", portal.resource_list, name="portal-resource-list"),
    path("portal/<str:resource>/new/", portal.resource_form, name="portal-resource-create"),
    path("portal/<str:resource>/<int:object_id>/edit/", portal.resource_form, name="portal-resource-edit"),
    path("portal/<str:resource>/<int:object_id>/delete/", portal.resource_delete, name="portal-resource-delete"),
    path("admin/", admin.site.urls),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("hospital.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
