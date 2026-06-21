from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, RedirectView, TemplateView, UpdateView

from app_months.models import FinancialMonth

from app_core.constants import MONTH_NAMES

from .forms import InvestmentForm, InvestmentGoalForm
from .models import Investment


def _month_detail_url(year, month):
    return reverse('month-detail', kwargs={'year': year, 'month': month})


# ── Annual view ───────────────────────────────────────────────────────────────

class InvestmentCurrentView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('investment-annual-year', kwargs={'year': date.today().year})


class InvestmentAnnualView(LoginRequiredMixin, TemplateView):
    template_name = 'app_investments/annual.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        year = self.kwargs['year']

        months_qs = FinancialMonth.objects.filter(user=self.request.user, year=year)
        months_by_month = {fm.month: fm for fm in months_qs.prefetch_related('investments')}

        rows = []
        total_goal = Decimal('0')
        total_invested = Decimal('0')

        for m in range(1, 13):
            fm = months_by_month.get(m)
            goal = fm.investment_goal if fm else Decimal('0')
            invested = fm.total_investments() if fm else Decimal('0')
            diff = invested - goal
            pct = round((invested / goal * 100), 1) if goal > 0 else None

            rows.append({
                'month': m,
                'month_name': MONTH_NAMES[m],
                'goal': goal,
                'invested': invested,
                'diff': diff,
                'pct': pct,
                'fm': fm,
            })
            total_goal += goal
            total_invested += invested

        total_pct = round((total_invested / total_goal * 100), 1) if total_goal > 0 else None

        import json
        chart_labels = [r['month_name'][:3] for r in rows]
        chart_invested = [float(r['invested'] or 0) for r in rows]
        chart_goals = [float(r['goal'] or 0) for r in rows]

        ctx.update({
            'year': year,
            'rows': rows,
            'total_goal': total_goal,
            'total_invested': total_invested,
            'total_diff': total_invested - total_goal,
            'total_pct': total_pct,
            'prev_year': year - 1,
            'next_year': year + 1,
            'chart_labels': json.dumps(chart_labels),
            'chart_invested': json.dumps(chart_invested),
            'chart_goals': json.dumps(chart_goals),
        })
        return ctx


# ── Investment CRUD ───────────────────────────────────────────────────────────

class InvestmentCreateView(LoginRequiredMixin, CreateView):
    model = Investment
    form_class = InvestmentForm
    template_name = 'app_investments/investment_form.html'

    def _get_financial_month(self):
        return get_object_or_404(
            FinancialMonth,
            user=self.request.user,
            year=self.kwargs['year'],
            month=self.kwargs['month'],
        )

    def form_valid(self, form):
        form.instance.financial_month = self._get_financial_month()
        messages.success(self.request, 'Investimento registrado com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        return _month_detail_url(self.kwargs['year'], self.kwargs['month'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['financial_month'] = self._get_financial_month()
        ctx['form_title'] = 'Novo Investimento'
        return ctx


class InvestmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Investment
    form_class = InvestmentForm
    template_name = 'app_investments/investment_form.html'

    def get_queryset(self):
        return Investment.objects.filter(financial_month__user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Investimento atualizado com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        fm = self.object.financial_month
        return _month_detail_url(fm.year, fm.month)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['financial_month'] = self.object.financial_month
        ctx['form_title'] = 'Editar Investimento'
        return ctx


class InvestmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Investment
    template_name = 'app_months/confirm_delete.html'

    def get_queryset(self):
        return Investment.objects.filter(financial_month__user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Investimento removido.')
        return super().form_valid(form)

    def get_success_url(self):
        fm = self.object.financial_month
        return _month_detail_url(fm.year, fm.month)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        fm = self.object.financial_month
        ctx['cancel_url'] = _month_detail_url(fm.year, fm.month)
        ctx['item_label'] = f'Investimento: {self.object.place} — R$ {self.object.amount}'
        return ctx


# ── Investment Goal (FinancialMonth.investment_goal) ─────────────────────────

class InvestmentGoalUpdateView(LoginRequiredMixin, UpdateView):
    model = FinancialMonth
    form_class = InvestmentGoalForm
    template_name = 'app_investments/goal_form.html'

    def get_object(self):
        return get_object_or_404(
            FinancialMonth,
            user=self.request.user,
            year=self.kwargs['year'],
            month=self.kwargs['month'],
        )

    def form_valid(self, form):
        messages.success(self.request, 'Meta de investimento atualizada.')
        return super().form_valid(form)

    def get_success_url(self):
        return _month_detail_url(self.kwargs['year'], self.kwargs['month'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['financial_month'] = self.object
        return ctx

# ── Simulator ────────────────────────────────────────────────────────────────

class InvestmentSimulatorView(LoginRequiredMixin, TemplateView):
    template_name = 'app_investments/simulator.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Valores padrão
        ctx['default_cdi'] = 10.40
        return ctx
