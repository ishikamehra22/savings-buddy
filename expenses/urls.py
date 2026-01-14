from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),      # root shows home
    path('dashboard/', views.dashboard, name='dashboard'),  # dashboard moved here
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_create, name='expense_add'),
    path('expenses/<int:pk>/edit/', views.expense_update, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('expenses/export/', views.export_expenses_csv, name='expense_export'),
    path('incomes/add/', views.income_create, name='income_add'),
    path('goals/add/', views.goal_create, name='goal_add'),
    path('register/', views.register, name='register'),
    path('incomes/', views.income_list, name='income_list'),
    path('income/edit/<int:pk>/', views.income_edit, name='income_edit'),
    path('income/delete/<int:pk>/', views.income_delete, name='income_delete'),
    path('income/', views.income_list, name='income_list'),
    path('expenses/delete_all/', views.expense_delete_all, name='expense_delete_all'),
    path('incomes/delete_all/', views.income_delete_all, name='income_delete_all'),
]
