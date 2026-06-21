from django import forms

from .models import Entry, FixedExpense, VariableExpense


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ('description', 'amount')
        labels = {
            'description': 'Descrição',
            'amount': 'Valor (R$)',
        }
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Ex: Salário, Freelance…'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0,00', 'step': '0.01', 'min': '0.01'}),
        }


class VariableExpenseForm(forms.ModelForm):
    class Meta:
        model = VariableExpense
        fields = ('description', 'amount')
        labels = {
            'description': 'Descrição',
            'amount': 'Valor (R$)',
        }
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Ex: Mercado, Combustível…'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0,00', 'step': '0.01', 'min': '0.01'}),
        }


class FixedExpenseForm(forms.ModelForm):
    class Meta:
        model = FixedExpense
        fields = ('description', 'amount', 'status')
        labels = {
            'description': 'Descrição',
            'amount': 'Valor (R$)',
            'status': 'Status',
        }
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Ex: Aluguel, Internet…'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0,00', 'step': '0.01', 'min': '0.01'}),
        }
