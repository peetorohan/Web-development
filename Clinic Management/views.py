import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AppointmentForm, PatientForm
from .models import Appointment, Patient


# 1. หน้าแดชบอร์ดหลัก (ต้องล็อกอินก่อนใช้งาน)
@login_required
def dashboard(request):
    today = timezone.localdate()
    appointments = (
        Appointment.objects
        .select_related("patient", "doctor")
        .order_by("appointment_date", "appointment_time")
    )
    return render(request, "clinic/dashboard.html", {
        "total_patients": Patient.objects.count(),
        "appointments": appointments,
        "today_count": appointments.filter(appointment_date=today).exclude(status="cancelled").count(),
        "today": today,
    })


# 2. ฟังก์ชันลงทะเบียนคนไข้ใหม่
@login_required
def create_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"ลงทะเบียนคนไข้ {patient} เรียบร้อยแล้ว")
            return redirect("dashboard")
    else:
        form = PatientForm()
    return render(request, "clinic/patient_form.html", {"form": form})


# 3. ฟังก์ชันสร้างนัดหมาย
@login_required
def create_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(request, f"สร้างนัดหมายของ {appointment.patient} เรียบร้อยแล้ว")
            return redirect("dashboard")
    else:
        form = AppointmentForm()
    return render(request, "clinic/appointment_form.html", {"form": form})


# 4. API ส่งตัวเลขสถิติแบบเรียลไทม์
@login_required
def dashboard_stats_api(request):
    today = timezone.localdate()
    appointments = Appointment.objects.all()
    return JsonResponse({
        "total_patients": Patient.objects.count(),
        "total_appointments": appointments.count(),
        "today_count": appointments.filter(appointment_date=today).exclude(status="cancelled").count(),
    })


# 5. API ส่งแถวตารางคิวแบบเรียลไทม์
@login_required
def appointment_rows_api(request):
    appointments = (
        Appointment.objects
        .select_related("patient", "doctor")
        .order_by("appointment_date", "appointment_time")
    )
    return render(request, "clinic/_appointment_rows.html", {
        "appointments": appointments
    })


# 6. API อัปเดตสถานะคิว (เริ่มตรวจ / เสร็จสิ้น)
@login_required
@require_POST
def update_appointment_status(request, pk):
    try:
        data = json.loads(request.body)
        new_status = data.get("status")
        appointment = Appointment.objects.get(pk=pk)
        if new_status in ["waiting", "checking", "done", "cancelled"]:
            appointment.status = new_status
            appointment.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "สถานะไม่ถูกต้อง"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)