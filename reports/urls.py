from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('pdf/', views.generate_pdf, name='generate_pdf'),
    path('excel/', views.export_excel, name='export_excel'),
]
