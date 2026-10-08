from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('patients/new/', views.create_patient, name='create_patient'),
    path('appointments/new/', views.create_appointment, name='create_appointment'),
    
    # URL endpoints สำหรับการดึงข้อมูลแบบ Real-time
    path('api/stats/', views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/appointments-rows/', views.appointment_rows_api, name='appointment_rows_api'),
    path('api/appointments/<int:pk>/status/', views.update_appointment_status, name='update_appointment_status'),
]