from datetime import date
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from app_months.models import FinancialMonth

MONTH_NAMES_SHORT = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez',
}

MONTH_NAMES_FULL = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'app_dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = date.today()
        user = self.request.user

        try:
            year = int(self.request.GET.get('ano', today.year))
        except (ValueError, TypeError):
            year = today.year

        current_month, _ = FinancialMonth.objects.get_or_create(
            user=user, year=today.year, month=today.month,
        )

        months_qs = FinancialMonth.objects.filter(user=user, year=year)
        months_by_number = {fm.month: fm for fm in months_qs}

        annual_rows = []
        for m in range(1, 13):
            fm = months_by_number.get(m)
            if fm:
                annual_rows.append({
                    'month': m,
                    'name': MONTH_NAMES_SHORT[m],
                    'entries': fm.total_entries(),
                    'expenses': fm.total_expenses(),
                    'investments': fm.total_investments(),
                    'balance': fm.current_balance(),
                    'url': reverse('month-detail', kwargs={'year': year, 'month': m}),
                    'is_current': year == today.year and m == today.month,
                    'exists': True,
                })
            else:
                annual_rows.append({
                    'month': m,
                    'name': MONTH_NAMES_SHORT[m],
                    'entries': None,
                    'expenses': None,
                    'investments': None,
                    'balance': None,
                    'url': reverse('month-detail', kwargs={'year': year, 'month': m}),
                    'is_current': year == today.year and m == today.month,
                    'exists': False,
                })

        existing = [r for r in annual_rows if r['exists']]
        annual_totals = {
            'entries': sum(r['entries'] or Decimal('0') for r in existing),
            'expenses': sum(r['expenses'] or Decimal('0') for r in existing),
            'investments': sum(r['investments'] or Decimal('0') for r in existing),
        }

        ctx.update({
            'current_month': current_month,
            'current_month_name': MONTH_NAMES_FULL[today.month],
            'today': today,
            'selected_year': year,
            'prev_year': year - 1,
            'next_year': year + 1,
            'annual_rows': annual_rows,
            'annual_totals': annual_totals,
        })
        return ctx
