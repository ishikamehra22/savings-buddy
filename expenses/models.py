from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True)
    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    def __str__(self):
        return f"{self.user.username} +{self.amount} on {self.date}"

class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField(null=True, blank=True)
    starting_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def progress_percent(self):
        # get total income & expense (you can restrict to deadline if wanted)
        total_income = Income.objects.filter(user=self.user).aggregate(sum=Sum('amount'))['sum'] or Decimal('0')
        total_expense = Expense.objects.filter(user=self.user).aggregate(sum=Sum('amount'))['sum'] or Decimal('0')

        current_saving = (total_income - total_expense) + (self.starting_balance or Decimal('0'))

        try:
            target = Decimal(self.target_amount or Decimal('0'))
        except Exception:
            target = Decimal('0')

        if target <= Decimal('0'):
            return 0.0
        percent = (current_saving / target) * 100
        # clamp between 0 and 100
        if percent < 0:
            percent = Decimal('0')
        if percent > 100:
            percent = Decimal('100')
        return float(percent)