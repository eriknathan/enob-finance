from datetime import date
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from app_core.constants import MONTH_NAMES as MONTH_NAMES_FULL, MONTH_NAMES_SHORT
from app_months.models import FinancialMonth


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
                    'expenses': fm.total_variable_expenses(),
                    'fixed': fm.total_fixed_expenses(),
                    'investments': fm.total_investments(),
                    'balance': fm.current_balance(),
                    'invoices': fm.total_card_invoices(),
                    'installment_sales': fm.total_installment_sales(),
                    'installment_payments': fm.total_installment_payments(),
                    'investment_goal': fm.investment_goal,
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
                    'fixed': None,
                    'investments': None,
                    'balance': None,
                    'invoices': None,
                    'installment_sales': None,
                    'installment_payments': None,
                    'investment_goal': None,
                    'url': reverse('month-detail', kwargs={'year': year, 'month': m}),
                    'is_current': year == today.year and m == today.month,
                    'exists': False,
                })

        existing = [r for r in annual_rows if r['exists']]
        
        # Calculate balance for the year
        # The balance of the year is the balance of the last recorded month in that year
        year_balance = existing[-1]['balance'] if existing else Decimal('0')
        
        # Determine previous year balance
        try:
            prev_year_last_month = FinancialMonth.objects.filter(user=user, year=year-1).order_by('-month').first()
            prev_year_balance = prev_year_last_month.current_balance() if prev_year_last_month else Decimal('0')
        except Exception:
            prev_year_balance = Decimal('0')

        annual_totals = {
            'entries': sum(r['entries'] or Decimal('0') for r in existing),
            'expenses': sum(r['expenses'] or Decimal('0') for r in existing),
            'fixed': sum(r['fixed'] or Decimal('0') for r in existing),
            'investments': sum(r['investments'] or Decimal('0') for r in existing),
            'invoices': sum(r['invoices'] or Decimal('0') for r in existing),
            'installment_sales': sum(r['installment_sales'] or Decimal('0') for r in existing),
            'installment_payments': sum(r['installment_payments'] or Decimal('0') for r in existing),
            'investment_goal': sum(r['investment_goal'] or Decimal('0') for r in existing),
            'balance': year_balance,
            'previous_balance': prev_year_balance,
        }

        import json
        chart_labels = [r['name'] for r in annual_rows]
        chart_entries = [float(r['entries'] or 0) for r in annual_rows]
        chart_expenses = [float(r['expenses'] or 0) for r in annual_rows]
        chart_fixed = [float(r['fixed'] or 0) for r in annual_rows]
        chart_investments = [float(r['investments'] or 0) for r in annual_rows]
        chart_balances = [float(r['balance'] or 0) for r in annual_rows]
        chart_invoices = [float(r['invoices'] or 0) for r in annual_rows]

        ctx.update({
            'current_month': current_month,
            'current_month_name': MONTH_NAMES_FULL[today.month],
            'today': today,
            'selected_year': year,
            'prev_year': year - 1,
            'next_year': year + 1,
            'annual_rows': annual_rows,
            'annual_totals': annual_totals,
            'chart_labels': json.dumps(chart_labels),
            'chart_entries': json.dumps(chart_entries),
            'chart_expenses': json.dumps(chart_expenses),
            'chart_fixed': json.dumps(chart_fixed),
            'chart_investments': json.dumps(chart_investments),
            'chart_balances': json.dumps(chart_balances),
            'chart_invoices': json.dumps(chart_invoices),
        })
        return ctx
