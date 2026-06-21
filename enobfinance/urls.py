from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_core.urls')),
    path('conta/', include('app_accounts.urls')),
    path('meses/', include('app_months.urls')),
    path('cartoes/', include('app_cards.urls')),
    path('investimentos/', include('app_investments.urls')),
    path('parcelamentos/', include('app_installments.urls')),
    path('dashboard/', include('app_dashboard.urls')),
    path('exportar/', include('app_exports.urls')),
]
