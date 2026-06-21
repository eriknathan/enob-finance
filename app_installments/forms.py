from datetime import date
from decimal import Decimal

from django import forms
from django.db import transaction

from app_months.models import FinancialMonth

from .models import Installment, InstallmentPlan

MONTH_CHOICES = [
    (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
    (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
    (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
]


class InstallmentPlanCreateForm(forms.ModelForm):
    total_amount = forms.DecimalField(
        label='Valor total (R$)',
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={'placeholder': '0,00', 'step': '0.01'}),
    )
    installment_count = forms.IntegerField(
        label='Número de parcelas',
        min_value=1,
        max_value=360,
        widget=forms.NumberInput(attrs={'placeholder': 'Ex: 12'}),
    )
    start_month = forms.ChoiceField(
        label='Mês inicial',
        choices=MONTH_CHOICES,
    )
    start_year = forms.IntegerField(
        label='Ano inicial',
        min_value=2020,
        max_value=2099,
        initial=date.today().year,
        widget=forms.NumberInput(attrs={'placeholder': 'Ex: 2026'}),
    )

    class Meta:
        model = InstallmentPlan
        fields = ('name', 'kind')
        labels = {
            'name': 'Nome do plano',
            'kind': 'Tipo',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ex: Geladeira, Venda do notebook…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today()
        self.fields['start_month'].initial = today.month
        self.fields['start_year'].initial = today.year

        self.fields['start_year'].initial = today.year


class InstallmentPlanUpdateForm(forms.ModelForm):
    start_month = forms.ChoiceField(
        label='Mês inicial',
        choices=MONTH_CHOICES,
    )
    start_year = forms.IntegerField(
        label='Ano inicial',
        min_value=2020,
        max_value=2099,
        widget=forms.NumberInput(attrs={'placeholder': 'Ex: 2026'}),
    )

    class Meta:
        model = InstallmentPlan
        fields = ('name', 'kind')
        labels = {
            'name': 'Nome do plano',
            'kind': 'Tipo',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ex: Geladeira, Venda do notebook…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            first_installment = self.instance.installments.order_by('number').first()
            if first_installment:
                self.fields['start_month'].initial = first_installment.financial_month.month
                self.fields['start_year'].initial = first_installment.financial_month.year

    @transaction.atomic
    def save(self, commit=True):
        plan = super().save(commit=commit)
        
        first_installment = plan.installments.order_by('number').first()
        if first_installment:
            old_month = first_installment.financial_month.month
            old_year = first_installment.financial_month.year
            
            new_month = int(self.cleaned_data['start_month'])
            new_year = int(self.cleaned_data['start_year'])
            
            if old_month != new_month or old_year != new_year:
                y, m = new_year, new_month
                for inst in plan.installments.order_by('number'):
                    fm, _ = FinancialMonth.objects.get_or_create(
                        user=plan.user,
                        year=y,
                        month=m,
                    )
                    inst.financial_month = fm
                    inst.save(update_fields=['financial_month'])
                    
                    m += 1
                    if m > 12:
                        m = 1
                        y += 1
                        
        return plan


class InstallmentPayForm(forms.ModelForm):
    class Meta:
        model = Installment
        fields = ('amount', 'status', 'receipt_url')
        labels = {
            'amount': 'Valor da parcela (R$)',
            'status': 'Status',
            'receipt_url': 'Link do comprovante',
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'receipt_url': forms.URLInput(attrs={
                'placeholder': 'https://drive.google.com/…',
            }),
        }
