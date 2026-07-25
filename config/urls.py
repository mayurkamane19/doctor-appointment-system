from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from hospital import portal
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("", portal.dashboard, name="dashboard"),
    path("portal/profile/", portal.profile_view, name="profile-view"),
    path("portal/analytics/", portal.analytics_view, name="portal-analytics"),
    path("portal/patients/<int:patient_id>/qr/", portal.patient_qr, name="patient-qr"),
    path("portal/patients/<int:patient_id>/card/", portal.patient_card, name="patient-card"),
    path("portal/invoices/<int:invoice_id>/pdf/", portal.download_invoice_pdf, name="download-invoice-pdf"),
    path("portal/prescriptions/<int:prescription_id>/pdf/", portal.download_prescription_pdf, name="download-prescription-pdf"),
    path("portal/discharges/<int:discharge_id>/pdf/", portal.download_discharge_pdf, name="download-discharge-pdf"),
    path("portal/export/revenue/excel/", portal.export_revenue_excel, name="export-revenue-excel"),
    path("portal/export/patients/csv/", portal.export_patients_csv, name="export-patients-csv"),
    path("portal/reports/", portal.reports, name="portal-reports"),
    path("portal/<str:resource>/", portal.resource_list, name="portal-resource-list"),
    path("portal/<str:resource>/new/", portal.resource_form, name="portal-resource-create"),
    path("portal/<str:resource>/<int:object_id>/edit/", portal.resource_form, name="portal-resource-edit"),
    path("portal/<str:resource>/<int:object_id>/delete/", portal.resource_delete, name="portal-resource-delete"),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("hospital.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
