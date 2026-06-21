from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from app_months.models import FinancialMonth

from .forms import InstallmentPayForm, InstallmentPlanCreateForm
from .models import Installment, InstallmentPlan


class InstallmentPlanListView(LoginRequiredMixin, ListView):
    model = InstallmentPlan
    template_name = 'app_installments/plan_list.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return InstallmentPlan.objects.filter(user=self.request.user).prefetch_related('installments')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        plans = self.get_queryset()
        ctx['payments'] = plans.filter(kind=InstallmentPlan.KIND_PAYMENT)
        ctx['sales'] = plans.filter(kind=InstallmentPlan.KIND_SALE)
        return ctx


class InstallmentPlanDetailView(LoginRequiredMixin, DetailView):
    model = InstallmentPlan
    template_name = 'app_installments/plan_detail.html'
    context_object_name = 'plan'

    def get_queryset(self):
        return InstallmentPlan.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['installments'] = self.object.installments.select_related('financial_month').all()
        return ctx


class InstallmentPlanCreateView(LoginRequiredMixin, CreateView):
    model = InstallmentPlan
    form_class = InstallmentPlanCreateForm
    template_name = 'app_installments/plan_form.html'
    success_url = reverse_lazy('installment-list')

    def form_valid(self, form):
        plan = form.save(commit=False)
        plan.user = self.request.user
        plan.save()

        total_amount = form.cleaned_data['total_amount']
        count = form.cleaned_data['installment_count']
        start_month = int(form.cleaned_data['start_month'])
        start_year = form.cleaned_data['start_year']

        # Calculate per-installment amount (last parcel absorbs rounding remainder)
        per_installment = (total_amount / count).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        remainder = total_amount - (per_installment * (count - 1))

        year, month = start_year, start_month
        for i in range(1, count + 1):
            fm, _ = FinancialMonth.objects.get_or_create(
                user=self.request.user,
                year=year,
                month=month,
            )
            Installment.objects.create(
                plan=plan,
                financial_month=fm,
                number=i,
                amount=remainder if i == count else per_installment,
            )
            month += 1
            if month > 12:
                month = 1
                year += 1

        messages.success(self.request, f'Plano "{plan.name}" criado com {count} parcelas.')
        return HttpResponseRedirect(reverse('installment-detail', kwargs={'pk': plan.pk}))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_title'] = 'Novo Plano de Parcelamento'
        return ctx


class InstallmentPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = InstallmentPlan
    template_name = 'app_months/confirm_delete.html'
    success_url = reverse_lazy('installment-list')

    def get_queryset(self):
        return InstallmentPlan.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f'Plano "{self.object.name}" removido.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = reverse('installment-detail', kwargs={'pk': self.object.pk})
        ctx['item_label'] = f'Plano: {self.object.name} ({self.object.get_kind_display()})'
        return ctx


class InstallmentPayView(LoginRequiredMixin, UpdateView):
    model = Installment
    form_class = InstallmentPayForm
    template_name = 'app_installments/installment_pay.html'

    def get_queryset(self):
        return Installment.objects.filter(plan__user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Parcela atualizada com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('installment-detail', kwargs={'pk': self.object.plan.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['plan'] = self.object.plan
        return ctx
