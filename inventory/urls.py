from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Laptop CRUD
    path('', views.laptop_list, name='laptop_list'),
    path('create/', views.laptop_create, name='laptop_create'),
    path('<int:pk>/', views.laptop_detail, name='laptop_detail'),
    path('<int:pk>/edit/', views.laptop_edit, name='laptop_edit'),
    path('<int:pk>/delete/', views.laptop_delete, name='laptop_delete'),
    path('<int:pk>/status/', views.laptop_change_status, name='laptop_change_status'),
    
    # WSM Assessment
    path('assessment/', views.assessment_list, name='assessment_list'),
    path('assessment/input/', views.assessment_input, name='assessment_input'),
    path('assessment/<int:pk>/', views.assessment_detail, name='assessment_detail'),
    
    # Grading Results
    path('grading/', views.grading_results, name='grading_results'),
    
    # Audit Log
    path('audit-log/', views.audit_log, name='audit_log'),
    
    # Settings
    path('settings/', views.settings_view, name='settings'),
    path('settings/criteria/', views.criteria_list, name='criteria_list'),
    path('settings/criteria/create/', views.criteria_create, name='criteria_create'),
    path('settings/criteria/<int:pk>/edit/', views.criteria_edit, name='criteria_edit'),
]
