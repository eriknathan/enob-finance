from django.urls import path

from .views import ExportExcelView

urlpatterns = [
    path('', ExportExcelView.as_view(), name='export-excel'),
]
