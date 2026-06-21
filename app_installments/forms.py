from datetime import date
from decimal import Decimal

from django import forms

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


class InstallmentPayForm(forms.ModelForm):
    class Meta:
        model = Installment
        fields = ('status', 'receipt_url')
        labels = {
            'status': 'Status',
            'receipt_url': 'Link do comprovante',
        }
        widgets = {
            'receipt_url': forms.URLInput(attrs={
                'placeholder': 'https://drive.google.com/…',
            }),
        }
