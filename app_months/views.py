from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, RedirectView, UpdateView
from django.views.generic.detail import DetailView

from .forms import (
    EntryForm,
    FinancialMonthConfigForm,
    FixedExpenseForm,
    InvestmentGoalForm,
    VariableExpenseForm,
)
from .models import Entry, FinancialMonth, FixedExpense, VariableExpense


# ── Helpers ───────────────────────────────────────────────────────────────────

MONTH_NAMES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}


def _month_detail_url(year, month):
    return reverse('month-detail', kwargs={'year': year, 'month': month})


def _carousel_months(current_year, current_month):
    """Returns list of (year, month, name) for the carousel: Jan to Dec of the selected year."""
    months = []
    for m in range(1, 13):
        months.append({
            'year': current_year,
            'month': m,
            'name': MONTH_NAMES[m],
            'active': m == current_month,
        })
    return months


class _MonthEntryMixin(LoginRequiredMixin):
    """Shared helper for entry-type CUD views that need the parent FinancialMonth."""

    def _get_financial_month(self):
        return get_object_or_404(
            FinancialMonth,
            user=self.request.user,
            year=self.kwargs['year'],
            month=self.kwargs['month'],
        )

    def get_success_url(self):
        return _month_detail_url(self.kwargs['year'], self.kwargs['month'])


class _OwnedMixin(LoginRequiredMixin):
    """Restricts queryset to items owned by the current user."""

    _owner_field = 'financial_month__user'

    def get_queryset(self):
        return super().get_queryset().filter(**{self._owner_field: self.request.user})

    def get_success_url(self):
        fm = self.object.financial_month
        return _month_detail_url(fm.year, fm.month)


# ── Month views ───────────────────────────────────────────────────────────────

class MonthCurrentView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        today = date.today()
        return _month_detail_url(today.year, today.month)


class MonthDetailView(LoginRequiredMixin, DetailView):
    model = FinancialMonth
    template_name = 'app_months/month_detail.html'
    context_object_name = 'financial_month'

    def get_object(self):
        # Auto-create the month on first access
        obj, _ = FinancialMonth.objects.get_or_create(
            user=self.request.user,
            year=self.kwargs['year'],
            month=self.kwargs['month'],
        )
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        fm = self.object
        year, month = fm.year, fm.month

        # Previous / next month navigation
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        installments_qs = fm.installments.select_related('plan').all()
        ctx.update({
            'month_name': MONTH_NAMES[month],
            'carousel_months': _carousel_months(year, month),
            'prev_url': _month_detail_url(prev_year, prev_month),
            'next_url': _month_detail_url(next_year, next_month),
            'entries': fm.entries.all(),
            'variable_expenses': fm.variable_expenses.all(),
            'fixed_expenses': fm.fixed_expenses.all(),
            'card_invoices': fm.card_invoices.select_related('card').all(),
            'investments': fm.investments.all(),
        })
        return ctx


# ── Entry CRUD ────────────────────────────────────────────────────────────────

class EntryCreateView(_MonthEntryMixin, CreateView):
    model = Entry
    form_class = EntryForm
    template_name = 'app_months/entry_form.html'

    def form_valid(self, form):
        form.instance.financial_month = self._get_financial_month()
        messages.success(self.request, 'Entrada adicionada com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['financial_month'] = self._get_financial_month()
        ctx['form_title'] = 'Nova Entrada'
        return ctx


class EntryUpdateView(_OwnedMixin, UpdateView):
    model = Entry
    form_class = EntryForm
    template_name = 'app_months/entry_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Entrada atualizada com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['financial_month'] = self.object.financial_month
        ctx['form_title'] = 'Editar Entrada'
        return ctx


class EntryDeleteView(_OwnedMixin, DeleteView):
    model = Entry
    template_name = 'app_months/confirm_delete.html'

    def form_valid(self, form):
        messages.success(self.request, 'Entrada removida.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = self.get_success_url()
        ctx['item_label'] = f'Entrada: {self.object.description}'
        return ctx


# ── VariableExpense CRUD ──────────────────────────────────────────────────────

class VariableExpenseCreateView(_MonthEntryMixin, CreateView):
    model = VariableExpense
    form_class = VariableExpenseForm
    template_name = 'app_months/expense_form.html'

    def form_valid(self, form):
        form.instance.financial_month = self._get_financial_month()
        messages.success(self.request, 'Gasto variável adicionado com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['financial_month'] = self._get_financial_month()
        ctx['form_title'] = 'Novo Gasto Variável'
        return ctx


class VariableExpenseUpdateView(_OwnedMixin, UpdateView):
    model = VariableExpense
    form_class = VariableExpenseForm
    template_name = 'app_months/expense_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Gasto variável atualizado com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['financial_month'] = self.object.financial_month
        ctx['form_title'] = 'Editar Gasto Variável'
        return ctx


class VariableExpenseDeleteView(_OwnedMixin, DeleteView):
    model = VariableExpense
    template_name = 'app_months/confirm_delete.html'

    def form_valid(self, form):
        messages.success(self.request, 'Gasto variável removido.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = self.get_success_url()
        ctx['item_label'] = f'Gasto variável: {self.object.description}'
        return ctx


# ── FixedExpense CRUD ─────────────────────────────────────────────────────────

class FixedExpenseCreateView(_MonthEntryMixin, CreateView):
    model = FixedExpense
    form_class = FixedExpenseForm
    template_name = 'app_months/expense_form.html'

    def form_valid(self, form):
        form.instance.financial_month = self._get_financial_month()
        messages.success(self.request, 'Despesa fixa adicionada com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['financial_month'] = self._get_financial_month()
        ctx['form_title'] = 'Nova Despesa Fixa'
        return ctx


class FixedExpenseUpdateView(_OwnedMixin, UpdateView):
    model = FixedExpense
    form_class = FixedExpenseForm
    template_name = 'app_months/expense_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Despesa fixa atualizada com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['financial_month'] = self.object.financial_month
        ctx['form_title'] = 'Editar Despesa Fixa'
        return ctx


class FixedExpenseDeleteView(_OwnedMixin, DeleteView):
    model = FixedExpense
    template_name = 'app_months/confirm_delete.html'

    def form_valid(self, form):
        messages.success(self.request, 'Despesa fixa removida.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = self.get_success_url()
        ctx['item_label'] = f'Despesa fixa: {self.object.description}'
        return ctx


class FixedExpenseToggleStatusView(_OwnedMixin, RedirectView):
    def post(self, request, *args, **kwargs):
        expense = get_object_or_404(FixedExpense, pk=self.kwargs['pk'], financial_month__user=request.user)
        expense.status = FixedExpense.STATUS_UNPAID if expense.status == FixedExpense.STATUS_PAID else FixedExpense.STATUS_PAID
        expense.save()
        messages.success(request, f'Status de "{expense.description}" atualizado.')
        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        expense = get_object_or_404(FixedExpense, pk=self.kwargs['pk'], financial_month__user=self.request.user)
        return _month_detail_url(expense.financial_month.year, expense.financial_month.month)


class FinancialMonthConfigUpdateView(LoginRequiredMixin, UpdateView):
    model = FinancialMonth
    form_class = FinancialMonthConfigForm
    template_name = 'app_months/month_config_form.html'

    def get_object(self, queryset=None):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(
            FinancialMonth,
            user=self.request.user,
            year=self.kwargs['year'],
            month=self.kwargs['month']
        )

    def get_success_url(self):
        return reverse('month-detail', kwargs={
            'year': self.object.year,
            'month': self.object.month,
        })
    
    def form_valid(self, form):
        messages.success(self.request, 'Período do mês atualizado com sucesso.')
        return super().form_valid(form)

class InvestmentGoalUpdateView(LoginRequiredMixin, UpdateView):
    model = FinancialMonth
    form_class = InvestmentGoalForm
    template_name = 'app_months/investment_goal_form.html'

    def get_object(self, queryset=None):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(
            FinancialMonth,
            user=self.request.user,
            year=self.kwargs['year'],
            month=self.kwargs['month']
        )

    def get_success_url(self):
        return reverse('month-detail', kwargs={
            'year': self.object.year,
            'month': self.object.month,
        })
    
    def form_valid(self, form):
        messages.success(self.request, 'Meta de investimento atualizada.')
        return super().form_valid(form)


