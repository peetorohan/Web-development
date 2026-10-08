from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Appointment, Patient


def is_valid_thai_id(value: str) -> bool:
    """ตรวจเลขบัตรประชาชนไทย 13 หลักด้วยหลักตรวจสอบ (checksum)"""
    if len(value) != 13 or not value.isdigit():
        return False
    total = sum(int(d) * (13 - i) for i, d in enumerate(value[:12]))
    return (11 - total % 11) % 10 == int(value[12])


# ---------------------------------------------------------------
# ฟอร์มลงทะเบียนผู้ป่วย
# ---------------------------------------------------------------
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["first_name", "last_name", "id_card", "phone", "blood_group", "allergies"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "เช่น สมชาย", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "เช่น ใจดี", "autocomplete": "family-name"}),
            "id_card": forms.TextInput(attrs={"placeholder": "1234567890123", "inputmode": "numeric", "maxlength": 17}),
            "phone": forms.TextInput(attrs={"placeholder": "0812345678", "inputmode": "tel", "maxlength": 15}),
            "allergies": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "เช่น แพ้เพนิซิลลิน ผื่นขึ้น / แพ้อาหารทะเล (ถ้าไม่มีให้เว้นว่าง)",
            }),
        }

    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip()

    def clean_id_card(self):
        value = self.cleaned_data["id_card"].replace("-", "").replace(" ", "")
        if not is_valid_thai_id(value):
            raise forms.ValidationError("เลขบัตรประชาชนไม่ถูกต้อง กรุณาตรวจสอบเลข 13 หลักอีกครั้ง")
        # กันการลงทะเบียนซ้ำ (ยกเว้นกำลังแก้ไขข้อมูลของคนไข้คนเดิม)
        duplicate = Patient.objects.filter(id_card=value).exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise forms.ValidationError("เลขบัตรประชาชนนี้ลงทะเบียนในระบบแล้ว")
        return value

    def clean_phone(self):
        value = self.cleaned_data["phone"].replace("-", "").replace(" ", "")
        if not value.isdigit() or not (9 <= len(value) <= 10):
            raise forms.ValidationError("เบอร์โทรศัพท์ต้องเป็นตัวเลข 9-10 หลัก")
        return value


# ---------------------------------------------------------------
# ฟอร์มนัดหมายแพทย์
# ---------------------------------------------------------------
class DoctorChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, user):
        return user.get_full_name() or user.username


class AppointmentForm(forms.ModelForm):
    # แสดงเฉพาะผู้ใช้ที่ยังใช้งานอยู่ เรียงตามชื่อ
    doctor = DoctorChoiceField(
        queryset=get_user_model().objects.filter(is_active=True).order_by("first_name", "username"),
        empty_label="— เลือกแพทย์ —",
        label="แพทย์ผู้รับการตรวจ",
    )

    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "appointment_date", "appointment_time", "symptoms", "status"]
        widgets = {
            "appointment_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "appointment_time": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "symptoms": forms.Textarea(attrs={"rows": 3, "placeholder": "เช่น ไข้ ปวดหัว ไอ มา 2 วัน"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].empty_label = "— เลือกผู้ป่วย —"
        # ช่องวันที่: ห้ามเลือกวันที่ผ่านมาแล้ว (ฝั่งเบราว์เซอร์)
        self.fields["appointment_date"].widget.attrs["min"] = timezone.localdate().isoformat()

    def clean_appointment_date(self):
        date = self.cleaned_data["appointment_date"]
        # ตรวจเฉพาะตอนสร้างใหม่ เพื่อให้แก้ไขนัดเก่าได้
        if self.instance.pk is None and date < timezone.localdate():
            raise forms.ValidationError("ไม่สามารถนัดหมายย้อนหลังได้ กรุณาเลือกวันนี้หรือวันถัดไป")
        return date

    def clean(self):
        cleaned = super().clean()
        doctor = cleaned.get("doctor")
        date = cleaned.get("appointment_date")
        time = cleaned.get("appointment_time")

        # แพทย์คนเดียวห้ามมีสองนัดในวัน-เวลาเดียวกัน (ไม่นับนัดที่ยกเลิก)
        if doctor and date and time:
            clash = (
                Appointment.objects
                .filter(doctor=doctor, appointment_date=date, appointment_time=time)
                .exclude(status="cancelled")
                .exclude(pk=self.instance.pk)
            )
            if clash.exists():
                raise forms.ValidationError("แพทย์ท่านนี้มีนัดหมายในวัน-เวลาดังกล่าวแล้ว กรุณาเลือกเวลาอื่น")
        return cleaned