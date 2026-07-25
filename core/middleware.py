class AuditMiddleware:
    """Records mutating API activity without storing sensitive request bodies."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.user.is_authenticated:
            from hospital.models import AuditLog
            AuditLog.objects.create(
                actor=request.user,
                action=request.method,
                path=request.path[:255],
                status_code=response.status_code,
                ip_address=self._client_ip(request),
            )
        return response

    @staticmethod
    def _client_ip(request):
        return request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")).split(",")[0].strip() or None
