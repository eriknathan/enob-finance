import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, DetailView, View

from app_months.models import FinancialMonth

from .forms import CardForm, CardInvoiceForm, InvoiceCSVUploadForm
from .models import Card, CardInvoice, InvoiceItem


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


class CardDetailView(LoginRequiredMixin, DetailView):
    model = Card
    template_name = 'app_cards/card_detail.html'
    context_object_name = 'card'

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        invoices = self.object.invoices.select_related('financial_month').order_by('-financial_month__year', '-financial_month__month')
        ctx['invoices'] = invoices
        
        # Prepare chart data for invoices history (last 12 invoices)
        chart_invoices = list(invoices[:12])
        chart_invoices.reverse()
        
        import json
        ctx['chart_labels'] = json.dumps([f"{inv.financial_month.month:02d}/{inv.financial_month.year}" for inv in chart_invoices])
        ctx['chart_amounts'] = json.dumps([float(inv.amount) for inv in chart_invoices])
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

class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = CardInvoice
    template_name = 'app_cards/invoice_detail.html'
    context_object_name = 'invoice'

    def get_queryset(self):
        return CardInvoice.objects.filter(financial_month__user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['items'] = self.object.items.all()
        ctx['upload_form'] = InvoiceCSVUploadForm()
        return ctx


class InvoiceCSVUploadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        invoice = get_object_or_404(CardInvoice, pk=pk, financial_month__user=request.user)
        form = InvoiceCSVUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.error(request, 'Arquivo inválido. Envie um arquivo .csv.')
            return redirect('invoice-detail', pk=pk)

        decoded = request.FILES['csv_file'].read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))

        items = []
        for row in reader:
            title = row.get('title', '').strip()
            date_str = row.get('date', '').strip()
            amount_str = row.get('amount', '').strip()

            if not title or not date_str or not amount_str:
                continue
            try:
                normalized = amount_str.replace(' ', '').replace('.', '').replace(',', '.')
                amount = Decimal(normalized)
            except InvalidOperation:
                continue
            if amount <= 0:
                continue
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                continue

            items.append(InvoiceItem(invoice=invoice, date=date, description=title, amount=amount))

        invoice.items.all().delete()
        InvoiceItem.objects.bulk_create(items)
        messages.success(request, f'{len(items)} itens importados com sucesso.')
        return redirect('invoice-detail', pk=pk)


class CardInvoiceToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        invoice = get_object_or_404(CardInvoice, pk=pk, financial_month__user=request.user)
        if invoice.status == 'unpaid' or invoice.status == 'PENDING':
            invoice.status = 'paid'
        else:
            invoice.status = 'unpaid'
        invoice.save()
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('month-detail', year=invoice.financial_month.year, month=invoice.financial_month.month)
