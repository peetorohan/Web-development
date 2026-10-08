from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="ชื่อ")
    last_name = models.CharField(max_length=100, verbose_name="นามสกุล")
    id_card = models.CharField(max_length=13, unique=True, verbose_name="เลขบัตรประชาชน")
    phone = models.CharField(max_length=15, verbose_name="เบอร์โทรศัพท์")
    blood_group = models.CharField(max_length=5, blank=True, verbose_name="หมู่เลือด")
    allergies = models.TextField(blank=True, default="ไม่มี", verbose_name="ประวัติการแพ้ยา/อาหาร")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'รอตรวจ'),
        ('checking', 'กำลังตรวจ'),
        ('done', 'ตรวจเสร็จสิ้น'),
        ('cancelled', 'ยกเลิก'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments', verbose_name="คนไข้")
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="แพทย์ผู้ตรวจ")
    appointment_date = models.DateField(verbose_name="วันที่นัด")
    appointment_time = models.TimeField(verbose_name="เวลานัด")
    symptoms = models.TextField(blank=True, verbose_name="อาการเบื้องต้น")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting', verbose_name="สถานะ")

    def __str__(self):
        return f"{self.patient} - {self.appointment_date} ({self.get_status_display()})"