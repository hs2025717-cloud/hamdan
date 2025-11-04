import flet as ft
import json
import os
from datetime import datetime, timedelta

# إعدادات النافذة
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600

# بيانات الغرف الافتراضية
DEFAULT_ROOMS = {
    "1112": ["بدون اسم", 0, 0, 0],
    "13": ["بدون اسم", 0, 0, 0],
    "2122": ["بدون اسم", 0, 0, 0],
    "23": ["بدون اسم", 0, 0, 0],
    "31": ["بدون اسم", 0, 0, 0],
    "32": ["بدون اسم", 0, 0, 0],
    "33": ["بدون اسم", 0, 0, 0],
    "41": ["بدون اسم", 0, 0, 0],
    "42": ["بدون اسم", 0, 0, 0],
    "43": ["بدون اسم", 0, 0, 0],
}

# كلمة المرور
PASSWORD = "H033s"

class RoomManager:
    def __init__(self):
        self.data_file = "rooms_data.json"
        self.rooms = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return DEFAULT_ROOMS.copy()
        return DEFAULT_ROOMS.copy()
    
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.rooms, f, ensure_ascii=False)
            return True
        except:
            return False
    
    def calculate_bill(self, bill_amount):
        try:
            bill_amount = float(bill_amount)
            
            # حساب إجمالي عدد الطلاب
            total_students = sum(room_data[1] + room_data[2] for room_data in self.rooms.values())
            
            # حساب إجمالي الطلاب الذين يمتلكون لابتوب
            total_with_laptop = sum(room_data[1] for room_data in self.rooms.values())
            
            if total_students == 0:
                return None, None, 'لا يوجد طلاب لإجراء الحساب'
            
            # نظام المتوسط المرجح
            # 50% من الفاتورة توزع بالتساوي على جميع الطلاب
            student_share = (bill_amount * 0.5) / total_students if total_students > 0 else 0
            
            # 50% من الفاتورة توزع على الطلاب الذين يمتلكون أجهزة فقط
            laptop_share = (bill_amount * 0.5) / total_with_laptop if total_with_laptop > 0 else 0
            
            return student_share, laptop_share, None
        except ValueError:
            return None, None, 'قيمة الفاتورة يجب أن تكون رقمية'
        except ZeroDivisionError:
            return None, None, 'لا يمكن القسمة على صفر في الحساب'
    
    def apply_bill_to_rooms(self, student_share, laptop_share):
        # تحديث المبالغ في الغرف بناءً على نظام المتوسط المرجح
        for room_num in self.rooms:
            room_data = self.rooms[room_num]
            total_students_in_room = room_data[1] + room_data[2]
            
            # حساب حصة الغرفة من الجزء الموزع على جميع الطلاب
            room_share_all = total_students_in_room * student_share
            
            # حساب حصة الغرفة من الجزء الموزع على أصحاب الأجهزة
            room_share_laptop = room_data[1] * laptop_share
            
            # إضافة المبلغ الإجمالي للغرفة
            total_room_share = room_share_all + room_share_laptop
            room_data[3] += total_room_share
        
        self.save_data()
        return True
    
    def update_room(self, room_num, name=None, has_laptop=None, no_laptop=None):
        if room_num not in self.rooms:
            return False, 'رقم الغرفة غير موجود'
        
        try:
            if name is not None:
                self.rooms[room_num][0] = name
            if has_laptop is not None:
                self.rooms[room_num][1] = int(has_laptop)
            if no_laptop is not None:
                self.rooms[room_num][2] = int(no_laptop)
            
            self.save_data()
            return True, 'تم التحديث بنجاح'
        except ValueError:
            return False, 'قيم الطلاب يجب أن تكون أرقاماً'
    
    def reset_room_bill(self, room_num):
        if room_num in self.rooms:
            self.rooms[room_num][3] = 0
            self.save_data()
            return True, 'تم تصفير المبلغ للغرفة'
        else:
            return False, 'رقم الغرفة غير موجود'
    
    def pay_room_bill(self, room_num, amount):
        if room_num not in self.rooms:
            return False, 'رقم الغرفة غير موجود'
        
        try:
            amount = float(amount)
            if amount <= 0:
                return False, 'المبلغ يجب أن يكون أكبر من الصفر'
            
            current_bill = self.rooms[room_num][3]
            if amount > current_bill:
                return False, 'المبلغ المسدد أكبر من المبلغ المتراكم'
            
            self.rooms[room_num][3] -= amount
            self.save_data()
            return True, f'تم سداد {amount:.2f} من المبلغ المتراكم'
        except ValueError:
            return False, 'قيمة المبلغ يجب أن تكون رقمية'

class AppScreenManager:
    def __init__(self, page):
        self.page = page
        self.room_manager = RoomManager()
        self.current_screen = None
        
        # إعدادات النافذة
        self.page.title = "نظام إدارة الغرف"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window.width = WINDOW_WIDTH
        self.page.window.height = WINDOW_HEIGHT
        self.page.window.resizable = False
        self.page.padding = 0
        
    def show_screen(self, screen_name, *args):
        self.page.clean()
        
        if screen_name == "login":
            self.show_login_screen()
        elif screen_name == "main":
            self.show_main_screen()
        elif screen_name == "bill":
            self.show_bill_screen()
        elif screen_name == "rooms":
            self.show_rooms_screen()
        elif screen_name == "edit":
            self.show_edit_screen()
        elif screen_name == "payment":
            self.show_payment_screen()
    
    def show_login_screen(self):
        self.current_screen = "login"
        
        # حاوية رئيسية
        main_container = ft.Container(
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            padding=40,
            bgcolor="white"
        )
        
        # عمود المحتوى
        content_column = ft.Column([
            # العنوان
            ft.Container(
                content=ft.Text(
                    "نظام إدارة الغرف",
                    size=28,
                    color="black",
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                height=120,
                alignment=ft.alignment.center
            ),
            
            # إدخال كلمة المرور
            ft.Column([
                ft.Text(
                    "كلمة المرور:",
                    size=20,
                    color="black",
                    text_align=ft.TextAlign.RIGHT
                ),
                ft.Container(height=15),
                ft.TextField(
                    password=True,
                    can_reveal_password=True,
                    border_color="gray",
                    bgcolor="white",
                    color="black",
                    text_size=20,
                    height=50
                )
            ]),
            
            ft.Container(height=30),
            
            # زر الدخول
            ft.ElevatedButton(
                "دخول",
                on_click=self.check_password,
                style=ft.ButtonStyle(
                    color="white",
                    bgcolor="green"
                ),
                height=50
            )
        ], spacing=30)
        
        main_container.content = content_column
        self.page.add(main_container)
        
        # حفظ المرجع لحقل كلمة المرور
        self.password_input = content_column.controls[1].controls[2]
    
    def check_password(self, e):
        password = self.password_input.value.strip()
        if password == PASSWORD:
            self.show_screen("main")
        else:
            self.show_alert("خطأ", "كلمة المرور غير صحيحة")
    
    def show_main_screen(self):
        self.current_screen = "main"
        
        main_container = ft.Container(
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            padding=20,
            bgcolor="white"
        )
        
        content_column = ft.Column([
            # العنوان
            ft.Container(
                content=ft.Text(
                    "نظام إدارة الغرف",
                    size=24,
                    color="black",
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                height=90,
                alignment=ft.alignment.center
            ),
            
            # الأزرار
            ft.Column([
                self.create_main_button("عرض الفاتورة", "bill", "gray"),
                self.create_main_button("عرض الغرف والطلاب", "rooms", "gray"),
                self.create_main_button("تعديل معلومات الغرف", "edit", "gray"),
                self.create_main_button("سداد الفاتورة", "payment", "gray"),
                self.create_main_button("خروج", "exit", "red", "white")
            ], spacing=20)
        ], spacing=20)
        
        main_container.content = content_column
        self.page.add(main_container)
    
    def create_main_button(self, text, screen, bgcolor, text_color="black"):
        return ft.Container(
            content=ft.ElevatedButton(
                text,
                on_click=lambda e: self.show_screen(screen) if screen != "exit" else self.page.window_close(),
                style=ft.ButtonStyle(
                    color=text_color,
                    bgcolor=bgcolor
                ),
                width=360,
                height=50
            )
        )
    
    def show_bill_screen(self):
        self.current_screen = "bill"
        
        main_container = ft.Container(
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            padding=10,
            bgcolor="white"
        )
        
        # حاوية النتائج القابلة للتمرير
        self.results_container = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            spacing=10
        )
        
        content_column = ft.Column([
            # العنوان
            ft.Container(
                content=ft.Text(
                    "حساب الفاتورة",
                    size=24,
                    color="black",
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                height=60,
                alignment=ft.alignment.center
            ),
            
            # إدخال الفاتورة
            ft.Row([
                ft.Text("قيمة الفاتورة:", size=18, color="black", width=150),
                ft.Container(width=10),
                ft.TextField(
                    width=200,
                    border_color="gray",
                    bgcolor="white",
                    color="black",
                    text_size=18
                )
            ]),
            
            ft.Container(height=10),
            
            # أزرار الحساب والتطبيق
            ft.Row([
                ft.ElevatedButton(
                    "حساب الفاتورة",
                    on_click=self.calculate_bill,
                    style=ft.ButtonStyle(bgcolor="gray")
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    "تطبيق على الغرف",
                    on_click=self.apply_bill,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="green"
                    )
                )
            ]),
            
            ft.Container(height=10),
            
            # منطقة النتائج
            ft.Container(
                content=ft.Column([
                    self.results_container
                ]),
                height=350,
                border=ft.border.all(1, "gray"),
                padding=50
            ),
            
            ft.Container(height=10),
            
            # زر العودة
            ft.ElevatedButton(
                "العودة للرئيسية",
                on_click=lambda e: self.show_screen("main"),
                style=ft.ButtonStyle(bgcolor="gray"),
                width=200
            )
        ], spacing=10)
        
        main_container.content = content_column
        self.page.add(main_container)
        
        # حفظ المرجع لحقل الفاتورة
        self.bill_input = content_column.controls[1].controls[2]
        self.calculation_result = None
        self.bill_amount = 0
    
    def calculate_bill(self, e):
        bill_amount = self.bill_input.value.strip()
        if not bill_amount:
            self.show_alert("خطأ", "يرجى إدخال قيمة الفاتورة")
            return
        
        student_share, laptop_share, error = self.room_manager.calculate_bill(bill_amount)
        
        if error:
            self.show_alert("خطأ", error)
            return
        
        self.calculation_result = (student_share, laptop_share)
        self.bill_amount = float(bill_amount)
        self.display_calculation_results(student_share, laptop_share)
    
    def display_calculation_results(self, student_share, laptop_share):
        self.results_container.controls.clear()
        
        # عرض الأسعار
        prices_card = self.create_card(
            f"نظام المتوسط المرجح\n\n"
            f"50% على جميع الطلاب: {student_share:.2f} للطالب\n"
            f"50% على أصحاب الأجهزة: {laptop_share:.2f} للطالب",
            "#f5f5f5"
        )
        self.results_container.controls.append(prices_card)
        
        # عرض تفاصيل الغرف
        for room_num, room_data in self.room_manager.rooms.items():
            total_students_in_room = room_data[1] + room_data[2]
            room_share_all = total_students_in_room * student_share
            room_share_laptop = room_data[1] * laptop_share
            total_cost = room_share_all + room_share_laptop
            
            room_info = f"""الغرفة: {room_num}
الطلاب الكلي: {total_students_in_room} → {room_share_all:.2f}
طلاب مع لابتوب: {room_data[1]} → {room_share_laptop:.2f}
المبلغ المضاف: {total_cost:.2f}"""
            
            room_card = self.create_room_card(
                room_info, 
                room_num, 
                room_data, 
                student_share, 
                laptop_share, 
                total_cost
            )
            self.results_container.controls.append(room_card)
        
        self.page.update()
    
    def create_card(self, content, bgcolor):
        return ft.Container(
            content=ft.Text(
                content,
                size=16,
                color="black",
                text_align=ft.TextAlign.CENTER
            ),
            padding=10,
            bgcolor=bgcolor,
            border_radius=5
        )
    
    def create_room_card(self, room_info, room_num, room_data, student_share, laptop_share, total_cost):
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    room_info,
                    size=14,
                    color="black",
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "عرض الفاتورة",
                    on_click=lambda e, rn=room_num, rd=room_data, ss=student_share, 
                                   ls=laptop_share, tc=total_cost: 
                    self.show_invoice(rn, rd, ss, ls, tc),
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#3366cc"
                    )
                )
            ]),
            padding=10,
            bgcolor="#e6e6e6",
            border_radius=5
        )
    
    def show_invoice(self, room_num, room_data, student_share, laptop_share, total_cost):
        # حساب التواريخ
        current_date = datetime.now()
        due_date = current_date + timedelta(days=3)
        
        # حساب التفاصيل المالية
        total_students_in_room = room_data[1] + room_data[2]
        students_without_laptop = room_data[2]
        students_with_laptop = room_data[1]
        
        cost_without_laptop = students_without_laptop * student_share
        cost_with_laptop = students_with_laptop * (student_share + laptop_share)
        
        previous_bill = room_data[3]  # المبلغ المتراكم السابق
        new_total_bill = previous_bill + total_cost  # المبلغ الإجمالي الجديد
        
        # إنشاء محتوى الفاتورة
        invoice_content = f"""
بيت الطالب

فاتورة الكهرباء
قيمة الفاتورة الكلية: {self.bill_amount:.2f}
المبلغ على جميع الطلاب: {student_share:.2f} للطالب
المبلغ الإضافي على حاملي اللابتوب: {laptop_share:.2f} للطالب

────────────────────

حصة الغرفة:
اسم المسؤول: {room_data[0]}
رقم الغرفة: {room_num}
عدد الطلاب الكلي: {total_students_in_room}
عدد الطلاب بدون لابتوب: {students_without_laptop}
عدد الطلاب مع لابتوب: {students_with_laptop}

طلاب بدون لابتوب:
- نصيب الفرد: {student_share:.2f}
- العدد: {students_without_laptop}
- الإجمالي: {cost_without_laptop:.2f}

طلاب مع لابتوب:
- نصيب الفرد: {student_share + laptop_share:.2f}
- العدد: {students_with_laptop}
- الإجمالي: {cost_with_laptop:.2f}

إجمالي هذه الفاتورة: {total_cost:.2f}
المبلغ المتبقي من فواتير سابقة: {previous_bill:.2f}
المبلغ الإجمالي على الغرفة: {new_total_bill:.2f}

────────────────────

ملاحظات:
• مهلة السداد: 3 أيام من تاريخ صدور الفاتورة
• آخر موعد للسداد: {due_date.strftime('%Y-%m-%d')}
• يمكنكم التسديد على الحساب البنكي:
  البنك: الكريمي
  رقم الحساب: 3170319515
  اسم الحساب: همدان فارس

تاريخ الإصدار: {current_date.strftime('%Y-%m-%d')}
"""
        
        # عرض الفاتورة في نافذة منبثقة
        self.show_invoice_dialog(invoice_content, room_num)
    
    def show_invoice_dialog(self, invoice_content, room_num):
        content_column = ft.Column([
            ft.Text(
                f"فاتورة الغرفة {room_num}",
                size=18,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=10),
            ft.Container(
                content=ft.Text(
                    invoice_content,
                    selectable=True,
                    size=14,
                    color="black"
                ),
                height=400,
                width=350,
                padding=10,
                border=ft.border.all(1, "gray")
            ),
            ft.Container(height=10),
            ft.Row([
                ft.ElevatedButton(
                    "تحميل الفاتورة",
                    on_click=lambda e: self.download_invoice_as_text(invoice_content, room_num),
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="green"
                    )
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    "إغلاق",
                    on_click=lambda e: self.close_dialog()
                )
            ])
        ])
        
        self.dialog = ft.AlertDialog(
            title=ft.Text(f"فاتورة الغرفة {room_num}"),
            content=content_column,
        )
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def download_invoice_as_text(self, invoice_content, room_num):
        try:
            filename = f"فاتورة_الغرفة_{room_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(invoice_content)
            
            self.show_alert("نجاح", f'تم حفظ الفاتورة في ملف: {filename}')
            self.close_dialog()
            
        except Exception as e:
            self.show_alert("خطأ", 'حدث خطأ أثناء حفظ الفاتورة')
    
    def close_dialog(self):
        if hasattr(self, 'dialog'):
            self.dialog.open = False
            self.page.update()
    
    def apply_bill(self, e):
        if not self.calculation_result:
            self.show_alert("خطأ", "يرجى حساب الفاتورة أولاً")
            return
        
        student_share, laptop_share = self.calculation_result
        success = self.room_manager.apply_bill_to_rooms(student_share, laptop_share)
        
        if success:
            self.show_alert("نجاح", "تم تطبيق الفاتورة على جميع الغرف بنجاح")
            self.calculation_result = None
    
    def show_rooms_screen(self):
        self.current_screen = "rooms"
        
        main_container = ft.Container(
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            padding=10,
            bgcolor="white"
        )
        
        # حاوية الغرف القابلة للتمرير
        self.rooms_container = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            spacing=10
        )
        
        content_column = ft.Column([
            # العنوان
            ft.Container(
                content=ft.Text(
                    "الغرف والطلاب",
                    size=24,
                    color="black",
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                height=60,
                alignment=ft.alignment.center
            ),
            
            # منطقة الغرف
            ft.Container(
                content=self.rooms_container,
                height=450,
                border=ft.border.all(1, "gray"),
                padding=10
            ),
            
            ft.Container(height=10),
            
            # زر العودة
            ft.ElevatedButton(
                "العودة للرئيسية",
                on_click=lambda e: self.show_screen("main"),
                style=ft.ButtonStyle(bgcolor="gray"),
                width=200
            )
        ], spacing=10)
        
        main_container.content = content_column
        self.page.add(main_container)
        
        self.update_rooms_display()
    
    def update_rooms_display(self):
        self.rooms_container.controls.clear()
        
        for room_num, room_data in self.room_manager.rooms.items():
            room_info = f"""رقم الغرفة: {room_num}
اسم المسؤول: {room_data[0]}
الطلاب مع لابتوب: {room_data[1]}
الطلاب بدون لابتوب: {room_data[2]}
إجمالي الطلاب: {room_data[1] + room_data[2]}
المبلغ المتراكم: {room_data[3]:.2f}"""
            
            room_card = ft.Container(
                content=ft.Column([
                    ft.Text(
                        room_info,
                        size=16,
                        color="black",
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "حذف المبلغ",
                        on_click=lambda e, rn=room_num: self.reset_bill(rn),
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="red"
                        )
                    )
                ]),
                padding=10,
                bgcolor="#e6e6e6",
                border_radius=5
            )
            self.rooms_container.controls.append(room_card)
        
        self.page.update()
    
    def reset_bill(self, room_num):
        success, message = self.room_manager.reset_room_bill(room_num)
        
        if success:
            self.update_rooms_display()
            self.show_alert("نجاح", message)
        else:
            self.show_alert("خطأ", message)
    
    def show_edit_screen(self):
        self.current_screen = "edit"
        
        main_container = ft.Container(
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            padding=20,
            bgcolor="white"
        )
        
        # حقول الإدخال
        self.room_input_edit = ft.TextField(
            label="رقم الغرفة",
            border_color="gray",
            bgcolor="white",
            color="black",
            text_size=18
        )
        
        self.name_input = ft.TextField(
            label="اسم المسؤول الجديد",
            border_color="gray",
            bgcolor="white",
            color="black",
            text_size=16
        )
        
        self.has_laptop_input = ft.TextField(
            label="عدد الطلاب مع لابتوب",
            border_color="gray",
            bgcolor="white",
            color="black",
            text_size=16,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.no_laptop_input = ft.TextField(
            label="عدد الطلاب بدون لابتوب",
            border_color="gray",
            bgcolor="white",
            color="black",
            text_size=16,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.info_label_edit = ft.Text("", color="black", text_align=ft.TextAlign.CENTER)
        
        content_column = ft.Column([
            # العنوان
            ft.Container(
                content=ft.Text(
                    "تعديل معلومات الغرف",
                    size=24,
                    color="black",
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                height=60,
                alignment=ft.alignment.center
            ),
            
            # إدخال رقم الغرفة
            self.room_input_edit,
            
            ft.Container(height=10),
            
            # زر البحث
            ft.ElevatedButton(
                "بحث عن الغرفة",
                on_click=self.search_room,
                style=ft.ButtonStyle(bgcolor="gray")
            ),
            
            ft.Container(height=10),
            
            # معلومات الغرفة
            self.info_label_edit,
            
            ft.Container(height=10),
            
            # حقول التعديل
            self.name_input,
            self.has_laptop_input,
            self.no_laptop_input,
            
            ft.Container(height=10),
            
            # زر التحديث
            ft.ElevatedButton(
                "تحديث المعلومات",
                on_click=self.update_room,
                style=ft.ButtonStyle(bgcolor="gray")
            ),
            
            ft.Container(height=10),
            
            # زر العودة
            ft.ElevatedButton(
                "العودة للرئيسية",
                on_click=lambda e: self.show_screen("main"),
                style=ft.ButtonStyle(bgcolor="gray"),
                width=200
            )
        ], spacing=10)
        
        main_container.content = content_column
        self.page.add(main_container)
        
        self.current_room = None
    
    def search_room(self, e):
        room_num = self.room_input_edit.value.strip()
        if not room_num:
            self.show_alert("خطأ", "يرجى إدخال رقم الغرفة")
            return
        
        if room_num not in self.room_manager.rooms:
            self.show_alert("خطأ", "رقم الغرفة غير موجود")
            return
        
        self.current_room = room_num
        room_data = self.room_manager.rooms[room_num]
        
        room_info = f"""الغرفة: {room_num}
المسؤول الحالي: {room_data[0]}
الطلاب مع لابتوب: {room_data[1]}
الطلاب بدون لابتوب: {room_data[2]}"""
        
        self.info_label_edit.value = room_info
        self.name_input.value = room_data[0]
        self.has_laptop_input.value = str(room_data[1])
        self.no_laptop_input.value = str(room_data[2])
        self.page.update()
    
    def update_room(self, e):
        if not self.current_room:
            self.show_alert("خطأ", "يرجى البحث عن غرفة أولاً")
            return
        
        name = self.name_input.value.strip()
        has_laptop = self.has_laptop_input.value.strip()
        no_laptop = self.no_laptop_input.value.strip()
        
        success, message = self.room_manager.update_room(
            self.current_room, 
            name if name else None,
            has_laptop if has_laptop else None,
            no_laptop if no_laptop else None
        )
        
        if success:
            self.show_alert("نجاح", message)
            self.search_room(e)  # تحديث المعلومات
        else:
            self.show_alert("خطأ", message)
    
    def show_payment_screen(self):
        self.current_screen = "payment"
        
        main_container = ft.Container(
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            padding=20,
            bgcolor="white"
        )
        
        # حقول الإدخال
        self.room_input_payment = ft.TextField(
            label="رقم الغرفة",
            border_color="gray",
            bgcolor="white",
            color="black",
            text_size=18
        )
        
        self.amount_input = ft.TextField(
            label="المبلغ المسدد",
            border_color="gray",
            bgcolor="white",
            color="black",
            text_size=18,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.info_label_payment = ft.Text("", color="black", text_align=ft.TextAlign.CENTER)
        
        content_column = ft.Column([
            # العنوان
            ft.Container(
                content=ft.Text(
                    "سداد الفاتورة",
                    size=24,
                    color="black",
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                height=60,
                alignment=ft.alignment.center
            ),
            
            # إدخال رقم الغرفة
            self.room_input_payment,
            
            ft.Container(height=10),
            
            # زر البحث
            ft.ElevatedButton(
                "بحث عن الغرفة",
                on_click=self.search_room_payment,
                style=ft.ButtonStyle(bgcolor="gray")
            ),
            
            ft.Container(height=10),
            
            # معلومات الغرفة
            self.info_label_payment,
            
            ft.Container(height=10),
            
            # إدخال المبلغ
            self.amount_input,
            
            ft.Container(height=10),
            
            # زر السداد
            ft.ElevatedButton(
                "تسديد المبلغ",
                on_click=self.pay_bill,
                style=ft.ButtonStyle(
                    color="white",
                    bgcolor="green"
                )
            ),
            
            ft.Container(height=10),
            
            # زر العودة
            ft.ElevatedButton(
                "العودة للرئيسية",
                on_click=lambda e: self.show_screen("main"),
                style=ft.ButtonStyle(bgcolor="gray"),
                width=200
            )
        ], spacing=10)
        
        main_container.content = content_column
        self.page.add(main_container)
        
        self.current_room_payment = None
    
    def search_room_payment(self, e):
        room_num = self.room_input_payment.value.strip()
        if not room_num:
            self.show_alert("خطأ", "يرجى إدخال رقم الغرفة")
            return
        
        if room_num not in self.room_manager.rooms:
            self.show_alert("خطأ", "رقم الغرفة غير موجود")
            return
        
        self.current_room_payment = room_num
        room_data = self.room_manager.rooms[room_num]
        
        room_info = f"""الغرفة: {room_num}
المسؤول: {room_data[0]}
المبلغ المتراكم: {room_data[3]:.2f}"""
        
        self.info_label_payment.value = room_info
        self.amount_input.value = ""
        self.page.update()
    
    def pay_bill(self, e):
        if not self.current_room_payment:
            self.show_alert("خطأ", "يرجى البحث عن غرفة أولاً")
            return
        
        amount = self.amount_input.value.strip()
        if not amount:
            self.show_alert("خطأ", "يرجى إدخال المبلغ المسدد")
            return
        
        success, message = self.room_manager.pay_room_bill(self.current_room_payment, amount)
        
        if success:
            self.show_alert("نجاح", message)
            self.search_room_payment(e)  # تحديث المعلومات
        else:
            self.show_alert("خطأ", message)
    
    def show_alert(self, title, message):
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("إغلاق", on_click=close_dialog)]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

def main(page: ft.Page):
    app_manager = AppScreenManager(page)
    app_manager.show_screen("login")

if __name__ == "__main__":
    ft.app(target=main)
