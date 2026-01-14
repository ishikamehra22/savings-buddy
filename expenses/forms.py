from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Expense, Income, SavingsGoal

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date', 'note']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date': forms.TextInput(attrs={'class': 'form-control date-input', 'type':'date'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['source', 'amount', 'date']
        widgets = {
            'source': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date': forms.TextInput(attrs={'class': 'form-control date-input', 'type':'date'}),
        }

class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['title', 'target_amount', 'deadline', 'starting_balance']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'step':'0.01'}),
            'deadline': forms.TextInput(attrs={'class': 'form-control date-input', 'type':'date'}),
            'starting_balance': forms.NumberInput(attrs={'class': 'form-control', 'step':'0.01'}),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'form-control'}))
    class Meta:
        model = User
        fields = ("username","email","password1","password2")

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            if field not in ['email']:
                self.fields[field].widget.attrs.update({'class':'form-control'})
