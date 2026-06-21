from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import View

from .services import build_export


class ExportExcelView(LoginRequiredMixin, View):
    def get(self, request):
        buf = build_export(request.user)
        today = date.today().strftime('%Y-%m-%d')
        filename = f'enobfinance-{today}.xlsx'
        response = HttpResponse(
            buf.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
