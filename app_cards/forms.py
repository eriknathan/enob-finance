from django import forms

from .models import Card, CardInvoice


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ('name', 'brand', 'closing_day', 'due_day')
        labels = {
            'name': 'Nome do cartão',
            'brand': 'Bandeira',
            'closing_day': 'Dia de fechamento',
            'due_day': 'Dia de vencimento',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ex: Nubank, Inter Platinum…'}),
            'closing_day': forms.NumberInput(attrs={'min': 1, 'max': 31, 'placeholder': '1-31'}),
            'due_day': forms.NumberInput(attrs={'min': 1, 'max': 31, 'placeholder': '1-31'}),
        }


class CardInvoiceForm(forms.ModelForm):
    class Meta:
        model = CardInvoice
        fields = ('card', 'amount')
        labels = {
            'card': 'Cartão',
            'amount': 'Valor da fatura (R$)',
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'placeholder': '0,00', 'step': '0.01', 'min': '0.01'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['card'].queryset = Card.objects.filter(user=user)
        self.fields['card'].empty_label = 'Selecione um cartão'


class InvoiceCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Arquivo CSV')

    def clean_csv_file(self):
        f = self.cleaned_data['csv_file']
        if not f.name.endswith('.csv'):
            raise forms.ValidationError('O arquivo deve ser um .csv.')
        return f
