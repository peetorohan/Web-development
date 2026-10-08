from datetime import timedelta

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Appointment, Patient

# ---------------------------------------------------------------
# หัวเรื่องของระบบ
# ---------------------------------------------------------------
admin.site.site_header = "🏥 Clinic Management System "
admin.site.site_title = "ระบบคลินิก"
admin.site.index_title = "แผงควบคุมระบบงานคลินิกและการนัดหมาย"

# สีป้ายสถานะ: key = ค่า status ในฐานข้อมูล -> (สีพื้น, สีตัวอักษร)
STATUS_COLORS = {
    "waiting":   ("#fff4d6", "#8a6100"),   # รอตรวจ
    "checking":  ("#dbeafe", "#1d4ed8"),   # กำลังตรวจ
    "done":      ("#d6f5dc", "#17803d"),   # เสร็จสิ้น
    "cancelled": ("#ececec", "#666666"),   # ยกเลิก
}
DEFAULT_COLOR = ("#ececec", "#666666")


def pill(text, bg, fg):
    return format_html(
        '<span style="background:{};color:{};padding:3px 12px;border-radius:999px;'
        'font-weight:500;white-space:nowrap;">{}</span>',
        bg, fg, text,
    )


# ---------------------------------------------------------------
# ตัวกรองช่วงเวลานัด (ใช้บ่อยในคลินิก)
# ---------------------------------------------------------------
class AppointmentWhenFilter(admin.SimpleListFilter):
    title = "ช่วงเวลานัด"
    parameter_name = "when"

    def lookups(self, request, model_admin):
        return [
            ("today", "วันนี้"),
            ("tomorrow", "พรุ่งนี้"),
            ("week", "7 วันข้างหน้า"),
            ("past", "ที่ผ่านมาแล้ว"),
        ]

    def queryset(self, request, queryset):
        today = timezone.localdate()
        value = self.value()
        if value == "today":
            return queryset.filter(appointment_date=today)
        if value == "tomorrow":
            return queryset.filter(appointment_date=today + timedelta(days=1))
        if value == "week":
            return queryset.filter(appointment_date__range=(today, today + timedelta(days=7)))
        if value == "past":
            return queryset.filter(appointment_date__lt=today)
        return queryset


# ---------------------------------------------------------------
# คนไข้
# ---------------------------------------------------------------
class AppointmentInline(admin.TabularInline):
    """แสดงประวัตินัดหมายในหน้าแก้ไขข้อมูลคนไข้"""
    model = Appointment
    extra = 0
    fields = ("appointment_date", "appointment_time", "doctor", "symptoms", "status")
    ordering = ("-appointment_date", "-appointment_time")
    verbose_name = "นัดหมาย"
    verbose_name_plural = "ประวัตินัดหมายของคนไข้"
    show_change_link = True


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("masked_id_card", "full_name", "phone", "blood_badge", "created_at")
    list_display_links = ("masked_id_card", "full_name")
    search_fields = ("first_name", "last_name", "id_card", "phone")
    list_filter = ("blood_group", "created_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25
    inlines = [AppointmentInline]

    @admin.display(description="ชื่อ-นามสกุล", ordering="first_name")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="เลขบัตรประชาชน", ordering="id_card")
    def masked_id_card(self, obj):
        # แสดงแค่ 4 หลักท้ายในหน้ารายการ เพื่อความเป็นส่วนตัว (PDPA)
        card = str(obj.id_card or "")
        return f"{'•' * max(len(card) - 4, 0)}{card[-4:]}" if card else "-"

    @admin.display(description="หมู่เลือด", ordering="blood_group")
    def blood_badge(self, obj):
        if not obj.blood_group:
            return "-"
        return pill(obj.blood_group, "#ffe0e3", "#b42336")


# ---------------------------------------------------------------
# นัดหมาย
# ---------------------------------------------------------------
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "appointment_date", "appointment_time", "symptoms_short", "status_badge")
    list_filter = (AppointmentWhenFilter, "status", "doctor", "appointment_date")
    search_fields = (
        "patient__first_name", "patient__last_name", "patient__id_card",
        "patient__phone", "symptoms",
    )
    date_hierarchy = "appointment_date"
    ordering = ("appointment_date", "appointment_time")
    autocomplete_fields = ("patient",)
    list_select_related = ("patient", "doctor")
    list_per_page = 25
    actions = ["mark_waiting", "mark_checking", "mark_done"]

    @admin.display(description="อาการเบื้องต้น")
    def symptoms_short(self, obj):
        text = obj.symptoms or ""
        return (text[:40] + "…") if len(text) > 40 else (text or "-")

    @admin.display(description="สถานะ", ordering="status")
    def status_badge(self, obj):
        bg, fg = STATUS_COLORS.get(obj.status, DEFAULT_COLOR)
        return pill(obj.get_status_display(), bg, fg)

    def _set_status(self, request, queryset, value, label):
        updated = queryset.update(status=value)
        self.message_user(request, f"เปลี่ยนสถานะเป็น \"{label}\" แล้ว {updated} รายการ")

    @admin.action(description="เปลี่ยนสถานะ → รอตรวจ")
    def mark_waiting(self, request, queryset):
        self._set_status(request, queryset, "waiting", "รอตรวจ")

    @admin.action(description="เปลี่ยนสถานะ → กำลังตรวจ")
    def mark_checking(self, request, queryset):
        self._set_status(request, queryset, "checking", "กำลังตรวจ")

    @admin.action(description="เปลี่ยนสถานะ → เสร็จสิ้น")
    def mark_done(self, request, queryset):
        self._set_status(request, queryset, "done", "เสร็จสิ้น")