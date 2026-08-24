class CRSHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.path.startswith("/api/docs"):
            response["Content-Security-Policy"] = (
                "default-src 'self';"
                "script-src 'self';"
                "style-src 'self' 'unsafe-inline';"
                "img-src 'self' data:;"
            )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response
