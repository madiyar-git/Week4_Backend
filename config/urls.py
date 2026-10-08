from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView, )
from rest_framework_simplejwt.views import (TokenRefreshView, TokenVerifyView, )

from accounts.views import LimiterTokenObtainPairView
from apps.core.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls), path("api/", include("tasks.urls")),
    path("api/token/", LimiterTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/health/", HealthCheckView.as_view(), name="health-check"), path("api/", include("accounts.urls")),
    ]

urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"), path(
        "api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger", ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
