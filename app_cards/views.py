from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from app_months.models import FinancialMonth

from .forms import CardForm, CardInvoiceForm
from .models import Card, CardInvoice


# ── Card CRUD ─────────────────────────────────────────────────────────────────

class CardListView(LoginRequiredMixin, ListView):
    model = Card
    template_name = 'app_cards/card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardForm
    template_name = 'app_cards/card_form.html'
    success_url = reverse_lazy('card-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Cartão adicionado com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_title'] = 'Novo Cartão'
        return ctx


class CardUpdateView(LoginRequiredMixin, UpdateView):
    model = Card
    form_class = CardForm
    template_name = 'app_cards/card_form.html'
    success_url = reverse_lazy('card-list')

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Cartão atualizado com sucesso.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_title'] = 'Editar Cartão'
        return ctx


class CardDeleteView(LoginRequiredMixin, DeleteView):
    model = Card
    template_name = 'app_months/confirm_delete.html'
    success_url = reverse_lazy('card-list')

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Cartão removido.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cancel_url'] = reverse_lazy('card-list')
        ctx['item_label'] = f'Cartão: {self.object.name} ({self.object.brand})'
        return ctx


# ── CardInvoice CRUD ──────────────────────────────────────────────────────────

class CardInvoiceCreateView(LoginRequiredMixin, CreateView):
    model = CardInvoice
    form_class = CardInvoiceForm
    template_name = 'app_cards/invoice_form.html'

    def _get_financial_month(self):
        return get_object_or_404(
            FinancialMonth,
            user=self.request.user,
            year=self.kwargs['year'],
            month=self.kwargs['month'],
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.financial_month = self._get_financial_month()
        messages.success(self.request, 'Fatura registrada com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        fm = self._get_financial_month()
        return reverse('month-detail', kwargs={'year': fm.year, 'month': fm.month})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['financial_month'] = self._get_financial_month()
        return ctx


class CardInvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = CardInvoice
    form_class = CardInvoiceForm
    template_name = 'app_cards/invoice_form.html'

    def get_queryset(self):
        return CardInvoice.objects.filter(financial_month__user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Fatura atualizada com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        fm = self.object.financial_month
        return reverse('month-detail', kwargs={'year': fm.year, 'month': fm.month})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['financial_month'] = self.object.financial_month
        return ctx


class CardInvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = CardInvoice
    template_name = 'app_months/confirm_delete.html'

    def get_queryset(self):
        return CardInvoice.objects.filter(financial_month__user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Fatura removida.')
        return super().form_valid(form)

    def get_success_url(self):
        fm = self.object.financial_month
        return reverse('month-detail', kwargs={'year': fm.year, 'month': fm.month})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        fm = self.object.financial_month
        ctx['cancel_url'] = reverse('month-detail', kwargs={'year': fm.year, 'month': fm.month})
        ctx['item_label'] = f'Fatura: {self.object.card.name} — {fm}'
        return ctx
