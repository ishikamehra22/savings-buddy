from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, Income, SavingsGoal, Category
from .forms import ExpenseForm, IncomeForm, SavingsGoalForm, RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Sum
import json
from django.utils.safestring import mark_safe
import csv
from django.http import HttpResponse
from datetime import date
import calendar
from dateutil.relativedelta import relativedelta
from django.contrib import messages

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')   # logged in → dashboard
    return render(request, 'home.html')  # not logged in → landing page

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user

    # --- Total calculations ---
    total_income = Income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
    net_saving = total_income - total_expense

    # --- Category-wise expense summary ---
    categories = Category.objects.all()
    cat_labels = []
    cat_values = []
    for c in categories:
        amt = Expense.objects.filter(user=user, category=c).aggregate(Sum('amount'))['amount__sum'] or 0
        cat_labels.append(c.name)
        cat_values.append(float(amt))

    # --- Monthly trend (accurate calendar months) ---
    from dateutil.relativedelta import relativedelta
    labels = []
    monthly_expenses = []
    today = date.today().replace(day=1)
    for i in range(5, -1, -1):
        month_date = today - relativedelta(months=i)
        month = month_date.month
        year = month_date.year
        labels.append(f"{calendar.month_abbr[month]} {year}")
        monthly_total = Expense.objects.filter(
            user=user,
            date__year=year,
            date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_expenses.append(float(monthly_total))

    # --- Savings Goal progress ---
    goal = SavingsGoal.objects.filter(user=user).order_by('-deadline').first()
    progress = goal.progress_percent() if goal else 0

    # --- Prepare data for template ---
    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'net_saving': net_saving,
        'cat_labels': mark_safe(json.dumps(cat_labels)),
        'cat_values': mark_safe(json.dumps(cat_values)),
        'labels': mark_safe(json.dumps(labels)),
        'monthly_expenses': mark_safe(json.dumps(monthly_expenses)),
        'goal': goal,
        'progress': progress,
    }

    return render(request, 'dashboard.html', context)

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "✅ Expense added successfully!")
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'expense_form.html', {'form': form})


@login_required
def goal_create(request):
    goal = SavingsGoal.objects.filter(user=request.user).first()  # get existing goal if any

    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=goal)  # update if exists
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "🎯 Savings goal saved successfully!")
            return redirect('dashboard')
    else:
        form = SavingsGoalForm(instance=goal)

    return render(request, 'goal_form.html', {'form': form})

@login_required
def expense_update(request, pk):
    obj = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=obj)
    return render(request, 'expense_form.html', {'form': form})

@login_required
def expense_delete(request, pk):
    obj = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        obj.delete()
        return redirect('expense_list')
    return render(request, 'expense_confirm_delete.html', {'obj':obj})

@login_required
def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('dashboard')
    else:
        form = IncomeForm()
    return render(request, 'income_form.html', {'form': form})

@login_required
def export_expenses_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Amount', 'Note'])

    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    for e in expenses:
        writer.writerow([e.date, e.category, e.amount, e.note])

    return response

@login_required
def expense_list(request):
    qs = Expense.objects.filter(user=request.user).order_by('-date')

    # --- filters ---
    category = request.GET.get('category')
    if category and category != "all":
        qs = qs.filter(category__name__icontains=category)

    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    if start_date and end_date:
        qs = qs.filter(date__range=[start_date, end_date])

    query = request.GET.get('q')
    if query:
        qs = qs.filter(note__icontains=query)

    categories = Category.objects.all()
    return render(request, 'expense_list.html', {
        'expenses': qs,
        'categories': categories,
    })

@login_required
def income_list(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    return render(request, 'income_list.html', {'incomes': incomes})

@login_required
def income_edit(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'income_form.html', {'form': form, 'title': 'Edit Income'})

@login_required
def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        income.delete()
        return redirect('income_list')
    # render generic confirm template
    return render(request, 'confirm_delete.html', {'object': income, 'type': 'income'})

@login_required
def expense_delete_all(request):
    if request.method == 'POST':
        Expense.objects.filter(user=request.user).delete()
        messages.success(request, "🧹 All expenses deleted successfully!")
        return redirect('expense_list')
    return render(request, 'confirm_delete.html', {'type': 'all expenses'})


@login_required
def income_delete_all(request):
    if request.method == 'POST':
        Income.objects.filter(user=request.user).delete()
        messages.success(request, "🧹 All incomes deleted successfully!")
        return redirect('income_list')
    return render(request, 'confirm_delete.html', {'type': 'all incomes'})
