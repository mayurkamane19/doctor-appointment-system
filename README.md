# Hospital Management System API

Secure Django hospital portal for RBAC, patient registration, OPD appointments, EMR encounters, nursing vitals, e-prescriptions, consents, IPD admissions/discharges/bed management, operation theatre schedules, GST invoices/payments, insurance claims, pharmacy inventory/procurement, laboratory orders/reports, notification tracking, audit logs, and dashboard reporting.

## Start locally

1. Create a virtual environment and run `pip install -r requirements.txt`.
2. Copy `.env.example` to `.env`; use SQLite initially or configure PostgreSQL.
3. Run `python manage.py makemigrations hospital`, `python manage.py migrate`, then `python manage.py createsuperuser`.
4. Start with `python manage.py runserver` and obtain a JWT from `POST /api/auth/token/`.

## Demo portal

Run `python manage.py seed_demo_data`, then sign in at `http://127.0.0.1:8000/` with `admin` / `Hospital@12345`. The staff portal provides searchable create, update, and delete screens for every core module.

For containers, set unique secrets in `docker-compose.yml`, then run `docker compose up --build`. Nginx serves the API at port 80; terminate TLS at a managed load balancer or extend the Nginx configuration with your certificate.

## Production requirements still needed

- A React/Angular patient and staff portal connected to these APIs.
- SMS/WhatsApp/email provider, payment gateway, and GST invoice PDF template. The portal tracks these workflows; sending payments/messages needs provider credentials and implementation.
- Object storage with encrypted backups; antivirus scanning for uploaded reports.
- Consent tracking, retention/deletion rules, break-glass access, and local legal/privacy review (DPDP Act plus applicable state/clinical regulations).
- Monitoring, alerting, disaster-recovery drills, rate limiting, vulnerability scanning, and a managed TLS certificate behind Nginx/load balancer.
- Interoperability integrations: HL7/FHIR, LIS/RIS/PACS, insurance/TPA, biometric attendance, and barcode printer/scanner workflows.

## Important

This starter is not certified for clinical deployment. Have a security professional and local healthcare/legal compliance team assess it before handling real patient data.
