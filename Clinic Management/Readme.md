# 🏥 Clinic Management System (ระบบจัดการคลินิกและการนัดหมายแพทย์)

เว็บแอปพลิเคชันสำหรับการบริหารจัดการคนไข้ คิวนัดหมายแพทย์ และแดชบอร์ดติดตามข้อมูลแบบเรียลไทม์ พัฒนาด้วย **Django Web Framework (Python)** ร่วมกับ Vanilla JavaScript (AJAX Polling)

---

## 📌 คุณสมบัติเด่นของระบบ (Features)

1. **ระบบยืนยันตัวตนและการเข้าถึง (Authentication & Security)**
   - หน้า Login สไตล์โมเดิร์นแบบ Glassmorphism พร้อมระบบตรวจสอบสิทธิ์ผ่าน Django Auth[cite: 8, 10]
   - การป้องกัน CSRF Token ในทุกฟอร์มและ Endpoint[cite: 9, 11]
   - ระบบควบคุมสิทธิ์เข้าถึงเฉพาะผู้ที่ล็อกอิน (`@login_required`)

2. **ระบบทะเบียนประวัติคนไข้ (Patient Management)**
   - บันทึกชื่อ-นามสกุล, เลขบัตรประชาชน 13 หลัก, เบอร์โทรศัพท์, กรุ๊ปเลือด และประวัติการแพ้ยา/อาหาร[cite: 13, 14]
   - ระบบตรวจสอบความถูกต้องของเลขบัตรประชาชนไทย 13 หลักด้วยอัลกอริทึม Checksum อัตโนมัติ[cite: 14]
   - ป้องกันการลงทะเบียนเลขบัตรประชาชนซ้ำในระบบ[cite: 14]
   - การปกป้องข้อมูลส่วนบุคคล (PDPA) ด้วยการ Mask เลขบัตรประชาชนในหน้าตารางข้อมูล[cite: 16]

3. **ระบบนัดหมายแพทย์ (Appointment Scheduling)**
   - ฟอร์มสร้างนัดหมายระบุแพทย์ผู้ตรวจ, วันที่ และเวลานัดหมาย[cite: 13, 14]
   - ระบบป้องกันการนัดหมายย้อนหลัง[cite: 14]
   - ระบบป้องกันคิวซ้ำซ้อน (Clash Detection): แพทย์คนเดียวกันไม่สามารถรับนัดซ้ำในวันและเวลาเดียวกันได้[cite: 14]
   - ระบบสถานะคิว 4 ระดับ: `รอตรวจ (waiting)`, `กำลังตรวจ (checking)`, `ตรวจเสร็จสิ้น (done)`, และ `ยกเลิก (cancelled)`[cite: 13, 16]

4. **แผงควบคุมเรียลไทม์ (Live Clinic Dashboard)**
   - การ์ดสรุปตัวเลขสถิติ 3 ช่อง: คนไข้ทั้งหมด, คิวนัดหมายทั้งหมด และคิวนัดหมายวันนี้
   - ตารางแสดงคิวนัดหมายประจำวันพร้อมปุ่มกดเปลี่ยนสถานะ (เริ่มตรวจ / เสร็จสิ้น)
   - อัปเดตข้อมูลอัตโนมัติแบบเรียลไทม์ผ่าน AJAX Polling ทุกๆ 3 วินาที โดยไม่ต้องรีโหลดหน้าเว็บ[cite: 2, 11]

5. **ระบบจัดการหลังบ้าน (Django Admin Customization)**
   - ปรับแต่งหน้าตา Dashboard ของแอดมินด้วย Badge สีบอกสถานะและหมู่เลือด[cite: 16]
   - ตัวกรองอัจฉริยะ (Custom List Filter): กรองนัดหมายวันนี้, พรุ่งนี้, 7 วันข้างหน้า หรือนัดหมายในอดีต[cite: 16]
   - ดูประวัตินัดหมายย้อนหลังของคนไข้ได้โดยตรงผ่าน TabularInline[cite: 16]

---

## 🛠 เทคโนโลยีที่ใช้งาน (Tech Stack)

- **Backend:** Python 3.13+, Django 6.1[cite: 2, 7, 10]
- **Database:** SQLite3 (Default Development)[cite: 9]
- **Frontend:** HTML5, CSS3 (Modern Glassmorphism & Responsive Design), Vanilla JavaScript (Fetch API)[cite: 2, 10]
- **Fonts & Icons:** Google Fonts (Prompt), Custom SVG Vector Icons[cite: 10]

---

## 📁 โครงสร้างโปรเจกต์ (Project Directory Structure)

```text
clinic_management/
│
├── clinic/                          # แอปพลิเคชันหลักของระบบคลินิก[cite: 9, 15]
│   ├── templates/                   # เทมเพลตภายในแอป[cite: 2, 9]
│   │   └── clinic/
│   │       ├── dashboard.html       # หน้าแดชบอร์ดหลัก[cite: 2]
│   │       ├── _appointment_rows.html # Partial HTML ตารางคิวแบบเรียลไทม์[cite: 2]
│   │       ├── patient_form.html    # ฟอร์มลงทะเบียนคนไข้[cite: 2]
│   │       └── appointment_form.html# ฟอร์มนัดหมายแพทย์[cite: 2]
│   ├── admin.py                     # ปรับแต่งระบบจัดการแอดมิน[cite: 16]
│   ├── apps.py                      # การตั้งค่าแอปพลิเคชัน[cite: 15]
│   ├── forms.py                     # ฟอร์มและการ Validate ข้อมูล[cite: 14]
│   ├── models.py                    # ตาราง Patient และ Appointment[cite: 13]
│   ├── urls.py                      # กำหนด Endpoint ภายในแอป clinic[cite: 2, 8]
│   └── views.py                     # Controllers และ Real-time APIs
│
├── clinic_management/               # โฟลเดอร์ตั้งค่าระบบของโปรเจกต์
│   ├── asgi.py                      # ASGI Entry point[cite: 10]
│   ├── settings.py                  # การตั้งค่าระบบทั้งหมด[cite: 9]
│   ├── urls.py                      # รูท URL หลัก (รวม Login & Admin)
│   └── wsgi.py                      # WSGI Entry point[cite: 7]
│
├── static/                          # ไฟล์ Static Assets
│   └── images/
│       ├── logo.png                 # โลโก้คลินิก
│       └── clinic-bg.jpg            # ภาพพื้นหลังคลินิก
│       └── logo.png
├── templates/                       # เทมเพลตระดับโปรเจกต์ (Override Admin)[cite: 9]
│   └── admin/
│       └── login.html               # หน้าเข้าสู่ระบบแบบ Glassmorphism[cite: 2, 9]
│
├── db.sqlite3                       # ฐานข้อมูล SQLite[cite: 9]
├── manage.py                        # สคริปต์คำสั่งจัดการ Django[cite: 2]
└── README.md
# 🏥 Clinic Management System รันเซิร์ฟเวอร์สำหรับทดสอบ
python manage.py runserver