import sys
import sqlite3
import os
from datetime import datetime, timedelta
from random import choice, randint
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont


# ================= VERİ TABANI =================
class DB:
    def __init__(self):
        # Eski veritabanını sil
        if os.path.exists("travel_pro.db"):
            os.remove("travel_pro.db")
        
        self.conn = sqlite3.connect("travel_pro.db")
        self.cur = self.conn.cursor()
        self.init_db()
        self.ornek_verileri_yukle()

    def init_db(self):
        # Seyahatler tablosu
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            country TEXT,
            start_date TEXT,
            end_date TEXT,
            budget REAL,
            status TEXT
        )
        """)

        # Oteller tablosu
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER,
            name TEXT,
            price REAL,
            check_in TEXT,
            check_out TEXT
        )
        """)

        # Planlar tablosu
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER,
            day TEXT,
            activity TEXT,
            location TEXT,
            time TEXT
        )
        """)

        # Harcamalar tablosu
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER,
            category TEXT,
            amount REAL,
            date TEXT,
            description TEXT
        )
        """)

        self.conn.commit()

    def ornek_verileri_yukle(self):
        # 20 şehir ve ülke verisi
        destinations = [
            ("İstanbul", "Türkiye", 15000, "Planlandı"),
            ("Paris", "Fransa", 25000, "Devam Ediyor"),
            ("Londra", "İngiltere", 30000, "Tamamlandı"),
            ("Roma", "İtalya", 20000, "Planlandı"),
            ("Barselona", "İspanya", 18000, "Devam Ediyor"),
            ("Amsterdam", "Hollanda", 22000, "Tamamlandı"),
            ("Berlin", "Almanya", 16000, "Planlandı"),
            ("Viyana", "Avusturya", 19000, "İptal Edildi"),
            ("Prag", "Çekya", 14000, "Planlandı"),
            ("Budapeşte", "Macaristan", 12000, "Devam Ediyor"),
            ("Dubai", "BAE", 35000, "Planlandı"),
            ("Tokyo", "Japonya", 45000, "Planlandı"),
            ("New York", "ABD", 40000, "Tamamlandı"),
            ("Bangkok", "Tayland", 15000, "Devam Ediyor"),
            ("Singapur", "Singapur", 28000, "Planlandı"),
            ("Sydney", "Avustralya", 38000, "Planlandı"),
            ("Kapadokya", "Türkiye", 10000, "Tamamlandı"),
            ("Antalya", "Türkiye", 8000, "Devam Ediyor"),
            ("Selanik", "Yunanistan", 7000, "Planlandı"),
            ("Kahire", "Mısır", 12000, "Planlandı")
        ]
        
        # Otel isimleri
        hotel_names = [
            "Hilton", "Marriott", "Sheraton", "Ritz Carlton", "Four Seasons",
            "Radisson Blu", "Holiday Inn", "Best Western", "Swissotel", "InterContinental"
        ]
        
        # Aktivite seçenekleri
        activities = [
            ("Şehir Turu", "Şehir Merkezi"),
            ("Müze Ziyareti", "Tarihi Bölge"),
            ("Yemek Turu", "Restoranlar Bölgesi"),
            ("Alışveriş", "Alışveriş Merkezi"),
            ("Doğa Yürüyüşü", "Park Alanı"),
            ("Plaj Keyfi", "Sahil"),
            ("Gece Hayatı", "Eğlence Merkezi"),
            ("Tarihi Gezi", "Tarihi Mekanlar")
        ]
        
        # Harcama kategorileri
        expense_categories = ["Konaklama", "Yemek", "Ulaşım", "Aktivite", "Alışveriş", "Diğer"]
        
        # 20 seyahat oluştur
        for city, country, base_budget, status in destinations:
            # Rastgele tarihler
            start_offset = randint(-30, 60)
            start_date = datetime.now() + timedelta(days=start_offset)
            duration = randint(3, 14)
            end_date = start_date + timedelta(days=duration)
            
            # Bütçe varyasyonu
            budget = base_budget + randint(-3000, 5000)
            budget = max(5000, budget)
            
            # Seyahati ekle
            self.cur.execute("""
            INSERT INTO trips(city, country, start_date, end_date, budget, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (city, country, start_date.strftime("%Y-%m-%d"),
                  end_date.strftime("%Y-%m-%d"), budget, status))
            trip_id = self.cur.lastrowid
            
            # 1-2 otel ekle
            num_hotels = randint(1, 2)
            for _ in range(num_hotels):
                hotel_name = choice(hotel_names) + " " + city
                hotel_price = randint(500, 4000) * duration
                check_in = start_date + timedelta(days=randint(0, max(0, duration-2)))
                check_out = check_in + timedelta(days=randint(1, min(3, duration)))
                self.cur.execute("""
                INSERT INTO hotels(trip_id, name, price, check_in, check_out)
                VALUES (?, ?, ?, ?, ?)
                """, (trip_id, hotel_name, hotel_price,
                      check_in.strftime("%Y-%m-%d"), check_out.strftime("%Y-%m-%d")))
            
            # 3-6 aktivite ekle
            num_activities = randint(3, 6)
            for day_num in range(1, min(duration + 1, num_activities + 1)):
                activity, location = choice(activities)
                time_slot = choice(["09:00", "11:00", "14:00", "16:00", "19:00", "21:00"])
                self.cur.execute("""
                INSERT INTO plans(trip_id, day, activity, location, time)
                VALUES (?, ?, ?, ?, ?)
                """, (trip_id, f"{day_num}. Gün", activity, location, time_slot))
            
            # 5-10 harcama ekle
            num_expenses = randint(5, 10)
            for _ in range(num_expenses):
                category = choice(expense_categories)
                amount = randint(50, 1500)
                expense_date = start_date + timedelta(days=randint(0, duration-1))
                self.cur.execute("""
                INSERT INTO expenses(trip_id, category, amount, date, description)
                VALUES (?, ?, ?, ?, ?)
                """, (trip_id, category, amount, expense_date.strftime("%Y-%m-%d"),
                      f"{category} harcaması"))
        
        self.conn.commit()
        print(f"{len(destinations)} adet örnek seyahat başarıyla yüklendi!")

    # ---------- SEYAHAT İŞLEMLERİ ----------
    def add_trip(self, city, country, start, end, budget, status="Planlandı"):
        self.cur.execute("""
        INSERT INTO trips(city, country, start_date, end_date, budget, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (city, country, start, end, budget, status))
        self.conn.commit()
        return self.cur.lastrowid

    def get_trips(self):
        return self.cur.execute("SELECT * FROM trips ORDER BY start_date DESC").fetchall()

    def get_trip_by_id(self, tid):
        return self.cur.execute("SELECT * FROM trips WHERE id=?", (tid,)).fetchone()

    def update_trip(self, tid, city, country, start, end, budget, status):
        self.cur.execute("""
        UPDATE trips SET city=?, country=?, start_date=?, end_date=?, budget=?, status=?
        WHERE id=?
        """, (city, country, start, end, budget, status, tid))
        self.conn.commit()

    def delete_trip(self, tid):
        self.cur.execute("DELETE FROM trips WHERE id=?", (tid,))
        self.conn.commit()

    # ---------- OTEL İŞLEMLERİ ----------
    def add_hotel(self, trip_id, name, price, check_in, check_out):
        self.cur.execute("""
        INSERT INTO hotels(trip_id, name, price, check_in, check_out)
        VALUES (?, ?, ?, ?, ?)
        """, (trip_id, name, price, check_in, check_out))
        self.conn.commit()

    def get_hotels_by_trip(self, trip_id):
        return self.cur.execute("SELECT * FROM hotels WHERE trip_id=?", (trip_id,)).fetchall()

    def delete_hotel(self, hid):
        self.cur.execute("DELETE FROM hotels WHERE id=?", (hid,))
        self.conn.commit()

    # ---------- PLAN İŞLEMLERİ ----------
    def add_plan(self, trip_id, day, activity, location, time=""):
        self.cur.execute("""
        INSERT INTO plans(trip_id, day, activity, location, time)
        VALUES (?, ?, ?, ?, ?)
        """, (trip_id, day, activity, location, time))
        self.conn.commit()

    def get_plans_by_trip(self, trip_id):
        return self.cur.execute("SELECT * FROM plans WHERE trip_id=? ORDER BY day, time", (trip_id,)).fetchall()

    def delete_plan(self, pid):
        self.cur.execute("DELETE FROM plans WHERE id=?", (pid,))
        self.conn.commit()

    # ---------- HARCAMA İŞLEMLERİ ----------
    def add_expense(self, trip_id, category, amount, date, description=""):
        self.cur.execute("""
        INSERT INTO expenses(trip_id, category, amount, date, description)
        VALUES (?, ?, ?, ?, ?)
        """, (trip_id, category, amount, date, description))
        self.conn.commit()

    def get_expenses_by_trip(self, trip_id):
        return self.cur.execute("SELECT * FROM expenses WHERE trip_id=? ORDER BY date DESC", (trip_id,)).fetchall()

    def delete_expense(self, eid):
        self.cur.execute("DELETE FROM expenses WHERE id=?", (eid,))
        self.conn.commit()

    def get_trip_expense_total(self, trip_id):
        result = self.cur.execute("SELECT SUM(amount) FROM expenses WHERE trip_id=?", (trip_id,)).fetchone()[0]
        return result or 0

    def get_hotel_total_by_trip(self, trip_id):
        result = self.cur.execute("SELECT SUM(price) FROM hotels WHERE trip_id=?", (trip_id,)).fetchone()[0]
        return result or 0

    # ---------- İSTATİSTİKLER ----------
    def total_budget(self):
        result = self.cur.execute("SELECT SUM(budget) FROM trips").fetchone()[0]
        return result or 0

    def total_expenses(self):
        result = self.cur.execute("SELECT SUM(amount) FROM expenses").fetchone()[0]
        return result or 0

    def total_hotel_cost(self):
        result = self.cur.execute("SELECT SUM(price) FROM hotels").fetchone()[0]
        return result or 0

    def get_trip_count_by_status(self):
        return {
            'planned': self.cur.execute("SELECT COUNT(*) FROM trips WHERE status='Planlandı'").fetchone()[0],
            'ongoing': self.cur.execute("SELECT COUNT(*) FROM trips WHERE status='Devam Ediyor'").fetchone()[0],
            'completed': self.cur.execute("SELECT COUNT(*) FROM trips WHERE status='Tamamlandı'").fetchone()[0],
            'cancelled': self.cur.execute("SELECT COUNT(*) FROM trips WHERE status='İptal Edildi'").fetchone()[0]
        }

    def get_upcoming_trips(self, limit=5):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.cur.execute("""
        SELECT * FROM trips WHERE start_date >= ? AND status != 'Tamamlandı'
        ORDER BY start_date LIMIT ?
        """, (today, limit)).fetchall()


# ================= SEYAHAT DETAY DİYALOĞU =================
class TripDetailDialog(QDialog):
    def __init__(self, db, trip_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.trip_id = trip_id
        self.trip = db.get_trip_by_id(trip_id)
        self.setWindowTitle(f"Seyahat Detayları - {self.trip[1]}")
        self.setGeometry(300, 200, 900, 700)
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        tabs = QTabWidget()

        self.create_info_tab(tabs)
        self.create_hotels_tab(tabs)
        self.create_plan_tab(tabs)
        self.create_expenses_tab(tabs)
        self.create_summary_tab(tabs)

        layout.addWidget(tabs)

        btn_close = QPushButton("Kapat")
        btn_close.clicked.connect(self.accept)
        btn_close.setFixedWidth(100)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def create_info_tab(self, tabs):
        widget = QWidget()
        layout = QFormLayout()

        city_edit = QLineEdit(self.trip[1])
        country_edit = QLineEdit(self.trip[2])
        start_edit = QDateEdit()
        start_edit.setDate(QDate.fromString(self.trip[3], "yyyy-MM-dd"))
        start_edit.setCalendarPopup(True)
        end_edit = QDateEdit()
        end_edit.setDate(QDate.fromString(self.trip[4], "yyyy-MM-dd"))
        end_edit.setCalendarPopup(True)
        budget_edit = QDoubleSpinBox()
        budget_edit.setRange(0, 1000000)
        budget_edit.setValue(self.trip[5])

        status_combo = QComboBox()
        status_combo.addItems(["Planlandı", "Devam Ediyor", "Tamamlandı", "İptal Edildi"])
        status_combo.setCurrentText(self.trip[6])

        layout.addRow("Şehir:", city_edit)
        layout.addRow("Ülke:", country_edit)
        layout.addRow("Başlangıç Tarihi:", start_edit)
        layout.addRow("Bitiş Tarihi:", end_edit)
        layout.addRow("Bütçe (TL):", budget_edit)
        layout.addRow("Durum:", status_combo)

        btn_save = QPushButton("Değişiklikleri Kaydet")
        btn_save.clicked.connect(lambda: self.save_trip_info(
            city_edit.text(), country_edit.text(),
            start_edit.date().toString("yyyy-MM-dd"),
            end_edit.date().toString("yyyy-MM-dd"),
            budget_edit.value(), status_combo.currentText()
        ))
        layout.addRow(btn_save)

        widget.setLayout(layout)
        tabs.addTab(widget, "Seyahat Bilgileri")

    def save_trip_info(self, city, country, start, end, budget, status):
        self.db.update_trip(self.trip_id, city, country, start, end, budget, status)
        QMessageBox.information(self, "Başarılı", "Seyahat bilgileri güncellendi!")
        self.trip = self.db.get_trip_by_id(self.trip_id)

    def create_hotels_tab(self, tabs):
        widget = QWidget()
        layout = QVBoxLayout()

        self.hotel_table = QTableWidget()
        self.hotel_table.setColumnCount(5)
        self.hotel_table.setHorizontalHeaderLabels(["ID", "Otel Adı", "Fiyat (TL)", "Giriş", "Çıkış"])
        self.hotel_table.hideColumn(0)
        self.load_hotels()

        form_widget = QWidget()
        form_layout = QHBoxLayout()

        hotel_name = QLineEdit()
        hotel_name.setPlaceholderText("Otel Adı")
        hotel_price = QDoubleSpinBox()
        hotel_price.setRange(0, 100000)
        hotel_price.setPrefix("₺")
        check_in = QDateEdit()
        check_in.setDate(QDate.currentDate())
        check_in.setCalendarPopup(True)
        check_out = QDateEdit()
        check_out.setDate(QDate.currentDate().addDays(1))
        check_out.setCalendarPopup(True)

        btn_add = QPushButton("Otel Ekle")
        btn_add.clicked.connect(lambda: self.add_hotel(
            hotel_name.text(), hotel_price.value(),
            check_in.date().toString("yyyy-MM-dd"),
            check_out.date().toString("yyyy-MM-dd")
        ))

        form_layout.addWidget(QLabel("Ad:"))
        form_layout.addWidget(hotel_name)
        form_layout.addWidget(QLabel("Fiyat:"))
        form_layout.addWidget(hotel_price)
        form_layout.addWidget(QLabel("Giriş:"))
        form_layout.addWidget(check_in)
        form_layout.addWidget(QLabel("Çıkış:"))
        form_layout.addWidget(check_out)
        form_layout.addWidget(btn_add)

        form_widget.setLayout(form_layout)

        btn_delete = QPushButton("Seçili Oteli Sil")
        btn_delete.clicked.connect(self.delete_hotel)

        layout.addWidget(self.hotel_table)
        layout.addWidget(form_widget)
        layout.addWidget(btn_delete)

        widget.setLayout(layout)
        tabs.addTab(widget, "Oteller")

    def load_hotels(self):
        hotels = self.db.get_hotels_by_trip(self.trip_id)
        self.hotel_table.setRowCount(0)
        for hotel in hotels:
            row = self.hotel_table.rowCount()
            self.hotel_table.insertRow(row)
            self.hotel_table.setItem(row, 0, QTableWidgetItem(str(hotel[0])))
            self.hotel_table.setItem(row, 1, QTableWidgetItem(hotel[2]))
            self.hotel_table.setItem(row, 2, QTableWidgetItem(f"₺{hotel[3]:.2f}"))
            self.hotel_table.setItem(row, 3, QTableWidgetItem(hotel[4]))
            self.hotel_table.setItem(row, 4, QTableWidgetItem(hotel[5]))

    def add_hotel(self, name, price, check_in, check_out):
        if not name:
            QMessageBox.warning(self, "Uyarı", "Lütfen otel adını girin!")
            return
        self.db.add_hotel(self.trip_id, name, price, check_in, check_out)
        self.load_hotels()
        QMessageBox.information(self, "Başarılı", "Otel eklendi!")

    def delete_hotel(self):
        row = self.hotel_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir otel seçin!")
            return
        hid = int(self.hotel_table.item(row, 0).text())
        reply = QMessageBox.question(self, "Onay", "Bu oteli silmek istediğinizden emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_hotel(hid)
            self.load_hotels()

    def create_plan_tab(self, tabs):
        widget = QWidget()
        layout = QVBoxLayout()

        self.plan_table = QTableWidget()
        self.plan_table.setColumnCount(5)
        self.plan_table.setHorizontalHeaderLabels(["ID", "Gün", "Saat", "Aktivite", "Konum"])
        self.plan_table.hideColumn(0)
        self.load_plans()

        form_widget = QWidget()
        form_layout = QHBoxLayout()

        plan_day = QLineEdit()
        plan_day.setPlaceholderText("1. Gün")
        plan_time = QLineEdit()
        plan_time.setPlaceholderText("09:00")
        plan_activity = QLineEdit()
        plan_activity.setPlaceholderText("Aktivite")
        plan_location = QLineEdit()
        plan_location.setPlaceholderText("Konum")

        btn_add = QPushButton("Plan Ekle")
        btn_add.clicked.connect(lambda: self.add_plan(
            plan_day.text(), plan_time.text(),
            plan_activity.text(), plan_location.text()
        ))

        form_layout.addWidget(QLabel("Gün:"))
        form_layout.addWidget(plan_day)
        form_layout.addWidget(QLabel("Saat:"))
        form_layout.addWidget(plan_time)
        form_layout.addWidget(QLabel("Aktivite:"))
        form_layout.addWidget(plan_activity)
        form_layout.addWidget(QLabel("Konum:"))
        form_layout.addWidget(plan_location)
        form_layout.addWidget(btn_add)

        form_widget.setLayout(form_layout)

        btn_delete = QPushButton("Seçili Planı Sil")
        btn_delete.clicked.connect(self.delete_plan)

        layout.addWidget(self.plan_table)
        layout.addWidget(form_widget)
        layout.addWidget(btn_delete)

        widget.setLayout(layout)
        tabs.addTab(widget, "Günlük Plan")

    def load_plans(self):
        plans = self.db.get_plans_by_trip(self.trip_id)
        self.plan_table.setRowCount(0)
        for plan in plans:
            row = self.plan_table.rowCount()
            self.plan_table.insertRow(row)
            self.plan_table.setItem(row, 0, QTableWidgetItem(str(plan[0])))
            self.plan_table.setItem(row, 1, QTableWidgetItem(plan[2]))
            self.plan_table.setItem(row, 2, QTableWidgetItem(plan[5] if plan[5] else ""))
            self.plan_table.setItem(row, 3, QTableWidgetItem(plan[3]))
            self.plan_table.setItem(row, 4, QTableWidgetItem(plan[4]))

    def add_plan(self, day, time, activity, location):
        if not activity:
            QMessageBox.warning(self, "Uyarı", "Lütfen aktivite girin!")
            return
        self.db.add_plan(self.trip_id, day, activity, location, time)
        self.load_plans()
        QMessageBox.information(self, "Başarılı", "Plan eklendi!")

    def delete_plan(self):
        row = self.plan_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir plan seçin!")
            return
        pid = int(self.plan_table.item(row, 0).text())
        reply = QMessageBox.question(self, "Onay", "Bu planı silmek istediğinizden emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_plan(pid)
            self.load_plans()

    def create_expenses_tab(self, tabs):
        widget = QWidget()
        layout = QVBoxLayout()

        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(5)
        self.expense_table.setHorizontalHeaderLabels(["ID", "Kategori", "Tutar (TL)", "Tarih", "Açıklama"])
        self.expense_table.hideColumn(0)
        self.load_expenses()

        form_widget = QWidget()
        form_layout = QHBoxLayout()

        expense_category = QComboBox()
        expense_category.addItems(["Konaklama", "Yemek", "Ulaşım", "Aktivite", "Alışveriş", "Diğer"])

        expense_amount = QDoubleSpinBox()
        expense_amount.setRange(0, 100000)
        expense_amount.setPrefix("₺")

        expense_date = QDateEdit()
        expense_date.setDate(QDate.currentDate())
        expense_date.setCalendarPopup(True)

        expense_desc = QLineEdit()
        expense_desc.setPlaceholderText("Açıklama (isteğe bağlı)")

        btn_add = QPushButton("Harcama Ekle")
        btn_add.clicked.connect(lambda: self.add_expense(
            expense_category.currentText(), expense_amount.value(),
            expense_date.date().toString("yyyy-MM-dd"), expense_desc.text()
        ))

        form_layout.addWidget(QLabel("Kategori:"))
        form_layout.addWidget(expense_category)
        form_layout.addWidget(QLabel("Tutar:"))
        form_layout.addWidget(expense_amount)
        form_layout.addWidget(QLabel("Tarih:"))
        form_layout.addWidget(expense_date)
        form_layout.addWidget(QLabel("Açıklama:"))
        form_layout.addWidget(expense_desc)
        form_layout.addWidget(btn_add)

        form_widget.setLayout(form_layout)

        btn_delete = QPushButton("Seçili Harcamayı Sil")
        btn_delete.clicked.connect(self.delete_expense)

        layout.addWidget(self.expense_table)
        layout.addWidget(form_widget)
        layout.addWidget(btn_delete)

        widget.setLayout(layout)
        tabs.addTab(widget, "Harcamalar")

    def load_expenses(self):
        expenses = self.db.get_expenses_by_trip(self.trip_id)
        self.expense_table.setRowCount(0)
        for expense in expenses:
            row = self.expense_table.rowCount()
            self.expense_table.insertRow(row)
            self.expense_table.setItem(row, 0, QTableWidgetItem(str(expense[0])))
            self.expense_table.setItem(row, 1, QTableWidgetItem(expense[2]))
            self.expense_table.setItem(row, 2, QTableWidgetItem(f"₺{expense[3]:.2f}"))
            self.expense_table.setItem(row, 3, QTableWidgetItem(expense[4]))
            self.expense_table.setItem(row, 4, QTableWidgetItem(expense[5] if expense[5] else ""))

    def add_expense(self, category, amount, date, description):
        self.db.add_expense(self.trip_id, category, amount, date, description)
        self.load_expenses()
        QMessageBox.information(self, "Başarılı", "Harcama eklendi!")

    def delete_expense(self):
        row = self.expense_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir harcama seçin!")
            return
        eid = int(self.expense_table.item(row, 0).text())
        reply = QMessageBox.question(self, "Onay", "Bu harcamayı silmek istediğinizden emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_expense(eid)
            self.load_expenses()

    def create_summary_tab(self, tabs):
        widget = QWidget()
        layout = QVBoxLayout()

        budget = self.trip[5]
        hotel_total = self.db.get_hotel_total_by_trip(self.trip_id)
        expense_total = self.db.get_trip_expense_total(self.trip_id)
        total_spent = hotel_total + expense_total
        remaining = budget - total_spent

        status_text = ""
        if self.trip[6] == "Planlandı":
            status_text = "📋 Planlandı"
        elif self.trip[6] == "Devam Ediyor":
            status_text = "✈️ Devam Ediyor"
        elif self.trip[6] == "Tamamlandı":
            status_text = "✅ Tamamlandı"
        else:
            status_text = "❌ İptal Edildi"

        summary_text = f"""
        <h2>Seyahat Özeti: {self.trip[1]}, {self.trip[2]}</h2>
        <hr>
        <table width="100%" cellpadding="10">
        <tr><td>📅 Tarihler:</td><td><b>{self.trip[3]} → {self.trip[4]}</b></td></tr>
        <tr><td>💰 Toplam Bütçe:</td><td><b>₺{budget:,.2f}</b></td></tr>
        <tr><td>🏨 Otel Harcamaları:</td><td>₺{hotel_total:,.2f}</td></tr>
        <tr><td>🍽️ Diğer Harcamalar:</td><td>₺{expense_total:,.2f}</td></tr>
        <tr><td>💸 Toplam Harcama:</td><td>₺{total_spent:,.2f}</td></tr>
        <tr><td>✅ Kalan Bütçe:</td><td><b style="color: {'green' if remaining >= 0 else 'red'}">₺{remaining:,.2f}</b></td></tr>
        <tr><td>📊 Durum:</td><td><b>{status_text}</b></td></tr>
        </table>
        """

        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet("font-size: 14px; padding: 20px;")

        layout.addWidget(summary_label)
        layout.addStretch()

        widget.setLayout(layout)
        tabs.addTab(widget, "Özet")


# ================= ANA UYGULAMA =================
class TravelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DB()
        self.setWindowTitle("Travel OS Pro - Profesyonel Seyahat Planlayıcı")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f4f6;
            }
            QPushButton {
                font-weight: bold;
            }
            QTableWidget {
                alternate-background-color: #f9fafb;
            }
            QHeaderView::section {
                background-color: #1f2937;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        self.ui()

    def ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        root.setLayout(layout)

        # Yan Menü
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            color: white;
            border: none;
        """)

        s = QVBoxLayout()
        s.setSpacing(5)

        title = QLabel("✈ TRAVEL OS")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
            border-bottom: 2px solid #3b82f6;
            margin-bottom: 20px;
        """)
        title.setAlignment(Qt.AlignCenter)
        s.addWidget(title)

        nav_buttons = [
            ("📊 Dashboard", self.go_dashboard),
            ("✈ Seyahatlerim", self.go_trips),
            ("➕ Yeni Seyahat", self.go_add),
            ("💰 Bütçe Genel Bakış", self.go_budget),
            ("📈 İstatistikler", self.go_stats)
        ]

        for text, callback in nav_buttons:
            btn = QPushButton(f"  {text}")
            btn.setStyleSheet("""
                QPushButton {
                    padding: 15px;
                    text-align: left;
                    border: none;
                    color: white;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: #334155;
                    border-left: 4px solid #3b82f6;
                }
            """)
            btn.clicked.connect(callback)
            s.addWidget(btn)

        s.addStretch()

        version = QLabel("Versiyon 2.0 | Profesyonel")
        version.setStyleSheet("padding: 15px; color: #94a3b8; font-size: 11px;")
        version.setAlignment(Qt.AlignCenter)
        s.addWidget(version)

        sidebar.setLayout(s)

        # Yığın
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("""
            QStackedWidget {
                background-color: #f8fafc;
            }
        """)

        self.page_dashboard()
        self.page_trips()
        self.page_add()
        self.page_budget()
        self.page_stats()

        self.stack.addWidget(self.dash_page)
        self.stack.addWidget(self.trips_page)
        self.stack.addWidget(self.add_page)
        self.stack.addWidget(self.budget_page)
        self.stack.addWidget(self.stats_page)

        layout.addWidget(sidebar)
        layout.addWidget(self.stack)

    def page_dashboard(self):
        self.dash_page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Dashboard")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)

        # Kartlar
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        self.total_trips_card = self.create_stats_card("Toplam Seyahat", "0", "#3b82f6")
        self.total_budget_card = self.create_stats_card("Toplam Bütçe", "0 TL", "#10b981")
        self.total_spent_card = self.create_stats_card("Toplam Harcama", "0 TL", "#ef4444")
        self.remaining_card = self.create_stats_card("Kalan Bütçe", "0 TL", "#f59e0b")

        cards_layout.addWidget(self.total_trips_card)
        cards_layout.addWidget(self.total_budget_card)
        cards_layout.addWidget(self.total_spent_card)
        cards_layout.addWidget(self.remaining_card)
        layout.addLayout(cards_layout)

        # Yaklaşan Seyahatler
        upcoming_label = QLabel("📅 Yaklaşan Seyahatler")
        upcoming_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(upcoming_label)

        self.upcoming_table = QTableWidget()
        self.upcoming_table.setColumnCount(5)
        self.upcoming_table.setHorizontalHeaderLabels(["ID", "Şehir", "Ülke", "Başlangıç", "Bütçe"])
        self.upcoming_table.hideColumn(0)
        self.upcoming_table.setAlternatingRowColors(True)
        self.upcoming_table.horizontalHeader().setStretchLastSection(True)
        self.upcoming_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        header_table = self.upcoming_table.horizontalHeader()
        header_table.setSectionResizeMode(1, QHeaderView.Stretch)
        header_table.setSectionResizeMode(2, QHeaderView.Stretch)

        layout.addWidget(self.upcoming_table, 1)

        self.dash_page.setLayout(layout)
        self.update_dashboard()

    def create_stats_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }}
        """)
        card.setMinimumHeight(120)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 14px;")

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold;")
        self.value_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def update_dashboard(self):
        trips = self.db.get_trips()
        total_budget = self.db.total_budget()
        total_spent = self.db.total_expenses() + self.db.total_hotel_cost()
        remaining = total_budget - total_spent

        # Kartları güncelle
        for child in self.total_trips_card.findChildren(QLabel):
            if child.text() != "Toplam Seyahat":
                child.setText(str(len(trips)))
                break

        for child in self.total_budget_card.findChildren(QLabel):
            if child.text() != "Toplam Bütçe":
                child.setText(f"₺{total_budget:,.0f}")
                break

        for child in self.total_spent_card.findChildren(QLabel):
            if child.text() != "Toplam Harcama":
                child.setText(f"₺{total_spent:,.0f}")
                break

        for child in self.remaining_card.findChildren(QLabel):
            if child.text() != "Kalan Bütçe":
                child.setText(f"₺{remaining:,.0f}")
                break

        upcoming = self.db.get_upcoming_trips()
        self.upcoming_table.setRowCount(0)
        for trip in upcoming:
            row = self.upcoming_table.rowCount()
            self.upcoming_table.insertRow(row)
            self.upcoming_table.setItem(row, 0, QTableWidgetItem(str(trip[0])))
            self.upcoming_table.setItem(row, 1, QTableWidgetItem(trip[1]))
            self.upcoming_table.setItem(row, 2, QTableWidgetItem(trip[2]))
            self.upcoming_table.setItem(row, 3, QTableWidgetItem(trip[3]))
            self.upcoming_table.setItem(row, 4, QTableWidgetItem(f"₺{trip[5]:,.0f}"))

    def page_trips(self):
        self.trips_page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Seyahatlerim")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Şehir veya ülkeye göre ara...")
        self.search_input.setStyleSheet("padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1;")
        self.search_input.textChanged.connect(self.search_trips)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.trip_table = QTableWidget()
        self.trip_table.setColumnCount(7)
        self.trip_table.setHorizontalHeaderLabels(["ID", "Şehir", "Ülke", "Başlangıç", "Bitiş", "Bütçe", "Durum"])
        self.trip_table.hideColumn(0)
        self.trip_table.setAlternatingRowColors(True)
        self.trip_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.trip_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.trip_table.doubleClicked.connect(self.view_trip_details)

        header_table = self.trip_table.horizontalHeader()
        header_table.setSectionResizeMode(1, QHeaderView.Stretch)
        header_table.setSectionResizeMode(2, QHeaderView.Stretch)

        buttons_layout = QHBoxLayout()

        btn_view = QPushButton("📋 Detayları Görüntüle")
        btn_view.clicked.connect(self.view_trip_details)
        btn_view.setStyleSheet("background-color: #3b82f6; color: white; padding: 10px; border-radius: 6px;")

        btn_delete = QPushButton("🗑 Seyahati Sil")
        btn_delete.clicked.connect(self.delete_trip)
        btn_delete.setStyleSheet("background-color: #ef4444; color: white; padding: 10px; border-radius: 6px;")

        btn_refresh = QPushButton("🔄 Yenile")
        btn_refresh.clicked.connect(self.load_trips)
        btn_refresh.setStyleSheet("background-color: #10b981; color: white; padding: 10px; border-radius: 6px;")

        buttons_layout.addWidget(btn_view)
        buttons_layout.addWidget(btn_delete)
        buttons_layout.addWidget(btn_refresh)
        buttons_layout.addStretch()

        layout.addWidget(self.trip_table)
        layout.addLayout(buttons_layout)

        self.trips_page.setLayout(layout)
        self.load_trips()

    def load_trips(self):
        trips = self.db.get_trips()
        self.all_trips = trips
        self.search_trips()

    def search_trips(self):
        search_text = self.search_input.text().lower()
        filtered = [t for t in self.all_trips if search_text in t[1].lower() or search_text in t[2].lower()]

        self.trip_table.setRowCount(0)
        for trip in filtered:
            row = self.trip_table.rowCount()
            self.trip_table.insertRow(row)
            self.trip_table.setItem(row, 0, QTableWidgetItem(str(trip[0])))
            self.trip_table.setItem(row, 1, QTableWidgetItem(trip[1]))
            self.trip_table.setItem(row, 2, QTableWidgetItem(trip[2]))
            self.trip_table.setItem(row, 3, QTableWidgetItem(trip[3]))
            self.trip_table.setItem(row, 4, QTableWidgetItem(trip[4]))
            self.trip_table.setItem(row, 5, QTableWidgetItem(f"₺{trip[5]:,.0f}"))
            self.trip_table.setItem(row, 6, QTableWidgetItem(trip[6]))

            status_item = self.trip_table.item(row, 6)
            if trip[6] == "Tamamlandı":
                status_item.setForeground(Qt.green)
            elif trip[6] == "Devam Ediyor":
                status_item.setForeground(Qt.blue)
            elif trip[6] == "İptal Edildi":
                status_item.setForeground(Qt.red)

    def delete_trip(self):
        row = self.trip_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir seyahat seçin!")
            return

        tid = int(self.trip_table.item(row, 0).text())
        city = self.trip_table.item(row, 1).text()

        reply = QMessageBox.question(self, "Silme Onayı",
                                     f"{city} seyahatini silmek istediğinizden emin misiniz?\n"
                                     "Tüm oteller, planlar ve harcamalar da silinecektir!",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db.delete_trip(tid)
            self.load_trips()
            self.update_dashboard()
            self.update_budget_page()
            QMessageBox.information(self, "Başarılı", "Seyahat başarıyla silindi!")

    def view_trip_details(self):
        row = self.trip_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen detaylarını görüntülemek için bir seyahat seçin!")
            return
        tid = int(self.trip_table.item(row, 0).text())
        dialog = TripDetailDialog(self.db, tid, self)
        dialog.exec_()
        self.load_trips()
        self.update_dashboard()
        self.update_budget_page()

    def page_add(self):
        self.add_page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Yeni Seyahat Ekle")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)

        form_card = QFrame()
        form_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(30, 30, 30, 30)

        self.add_city = QLineEdit()
        self.add_city.setPlaceholderText("Örn: İstanbul")
        self.add_city.setStyleSheet("padding: 10px; border-radius: 6px; border: 1px solid #cbd5e1;")

        self.add_country = QLineEdit()
        self.add_country.setPlaceholderText("Örn: Türkiye")
        self.add_country.setStyleSheet("padding: 10px; border-radius: 6px; border: 1px solid #cbd5e1;")

        self.add_start = QDateEdit()
        self.add_start.setDate(QDate.currentDate())
        self.add_start.setCalendarPopup(True)
        self.add_start.setStyleSheet("padding: 10px; border-radius: 6px; border: 1px solid #cbd5e1;")

        self.add_end = QDateEdit()
        self.add_end.setDate(QDate.currentDate().addDays(7))
        self.add_end.setCalendarPopup(True)
        self.add_end.setStyleSheet("padding: 10px; border-radius: 6px; border: 1px solid #cbd5e1;")

        self.add_budget = QDoubleSpinBox()
        self.add_budget.setRange(0, 1000000)
        self.add_budget.setPrefix("₺")
        self.add_budget.setStyleSheet("padding: 10px; border-radius: 6px; border: 1px solid #cbd5e1;")

        self.add_status = QComboBox()
        self.add_status.addItems(["Planlandı", "Devam Ediyor"])

        form_layout.addRow("Şehir *:", self.add_city)
        form_layout.addRow("Ülke *:", self.add_country)
        form_layout.addRow("Başlangıç Tarihi:", self.add_start)
        form_layout.addRow("Bitiş Tarihi:", self.add_end)
        form_layout.addRow("Bütçe (TL):", self.add_budget)
        form_layout.addRow("Durum:", self.add_status)

        form_card.setLayout(form_layout)

        btn_add = QPushButton("✈ Seyahat Oluştur")
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        btn_add.clicked.connect(self.add_trip)

        layout.addWidget(form_card)
        layout.addWidget(btn_add)
        layout.addStretch()

        self.add_page.setLayout(layout)

    def add_trip(self):
        if not self.add_city.text() or not self.add_country.text():
            QMessageBox.warning(self, "Uyarı", "Lütfen şehir ve ülke girin!")
            return

        if self.add_start.date() > self.add_end.date():
            QMessageBox.warning(self, "Uyarı", "Bitiş tarihi başlangıç tarihinden sonra olmalıdır!")
            return

        try:
            tid = self.db.add_trip(
                self.add_city.text(),
                self.add_country.text(),
                self.add_start.date().toString("yyyy-MM-dd"),
                self.add_end.date().toString("yyyy-MM-dd"),
                self.add_budget.value(),
                self.add_status.currentText()
            )

            self.add_city.clear()
            self.add_country.clear()
            self.add_start.setDate(QDate.currentDate())
            self.add_end.setDate(QDate.currentDate().addDays(7))
            self.add_budget.setValue(0)

            self.load_trips()
            self.update_dashboard()
            self.update_budget_page()

            QMessageBox.information(self, "Başarılı", "Seyahat başarıyla oluşturuldu!")

            reply = QMessageBox.question(self, "Detay Ekle",
                                         "Şimdi otel, plan ve harcama eklemek ister misiniz?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                dialog = TripDetailDialog(self.db, tid, self)
                dialog.exec_()
                self.update_budget_page()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Seyahat eklenirken hata oluştu: {str(e)}")

    def page_budget(self):
        self.budget_page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Bütçe Genel Bakış")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)

        self.budget_summary = QLabel()
        self.budget_summary.setStyleSheet("""
            QLabel {
                background-color: white;
                padding: 25px;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                font-size: 16px;
            }
        """)
        self.budget_summary.setWordWrap(True)
        layout.addWidget(self.budget_summary)

        trips_label = QLabel("Seyahat Bazlı Bütçe Dağılımı")
        trips_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(trips_label)

        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(5)
        self.budget_table.setHorizontalHeaderLabels(["Seyahat", "Bütçe", "Harcanan", "Kalan", "Durum"])
        self.budget_table.setAlternatingRowColors(True)

        header_table = self.budget_table.horizontalHeader()
        header_table.setSectionResizeMode(0, QHeaderView.Stretch)
        header_table.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        layout.addWidget(self.budget_table)

        self.update_budget_page()

    def update_budget_page(self):
        trips = self.db.get_trips()
        total_budget = self.db.total_budget()
        total_spent = self.db.total_expenses() + self.db.total_hotel_cost()
        remaining = total_budget - total_spent

        self.budget_summary.setText(f"""
        <table width="100%" cellpadding="10">
        <tr><td style="background:#3b82f6; color:white; border-radius:8px; text-align:center;">
            <b>📊 Toplam Bütçe</b><br>
            <span style="font-size:24px;">₺{total_budget:,.0f}</span>
        </td>
        <td style="background:#ef4444; color:white; border-radius:8px; text-align:center;">
            <b>💰 Toplam Harcama</b><br>
            <span style="font-size:24px;">₺{total_spent:,.0f}</span>
        </td>
        <td style="background:#10b981; color:white; border-radius:8px; text-align:center;">
            <b>✅ Kalan Bütçe</b><br>
            <span style="font-size:24px;">₺{remaining:,.0f}</span>
        </td>
        </tr>
        <tr>
        <td colspan="3" style="background:#f59e0b; color:white; border-radius:8px; text-align:center;">
            <b>📈 Toplam Seyahat Sayısı: {len(trips)}</b>
        </td>
        </tr>
        </table>
        """)

        self.budget_table.setRowCount(0)
        for trip in trips:
            row = self.budget_table.rowCount()
            self.budget_table.insertRow(row)

            trip_spent = self.db.get_trip_expense_total(trip[0]) + self.db.get_hotel_total_by_trip(trip[0])
            trip_remaining = trip[5] - trip_spent

            self.budget_table.setItem(row, 0, QTableWidgetItem(f"{trip[1]}, {trip[2]}"))
            self.budget_table.setItem(row, 1, QTableWidgetItem(f"₺{trip[5]:,.0f}"))
            self.budget_table.setItem(row, 2, QTableWidgetItem(f"₺{trip_spent:,.0f}"))
            self.budget_table.setItem(row, 3, QTableWidgetItem(f"₺{trip_remaining:,.0f}"))
            self.budget_table.setItem(row, 4, QTableWidgetItem(trip[6]))

            if trip_remaining < 0:
                self.budget_table.item(row, 3).setForeground(Qt.red)
            elif trip_remaining < trip[5] * 0.2:
                self.budget_table.item(row, 3).setForeground(Qt.darkYellow)

    def page_stats(self):
        self.stats_page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("İstatistikler ve Raporlar")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)

        status_counts = self.db.get_trip_count_by_status()

        stats_text = f"""
        <h3>Seyahat İstatistikleri</h3>
        <table width="100%" cellpadding="15">
        <tr>
        <td style="background:#3b82f6; color:white; border-radius:10px; text-align:center;">
            📋 Planlandı<br><b style="font-size:28px;">{status_counts['planned']}</b>
        </td>
        <td style="background:#10b981; color:white; border-radius:10px; text-align:center;">
            ▶ Devam Ediyor<br><b style="font-size:28px;">{status_counts['ongoing']}</b>
        </td>
        <td style="background:#f59e0b; color:white; border-radius:10px; text-align:center;">
            ✅ Tamamlandı<br><b style="font-size:28px;">{status_counts['completed']}</b>
        </tr>
        <td style="background:#ef4444; color:white; border-radius:10px; text-align:center;">
            ❌ İptal Edildi<br><b style="font-size:28px;">{status_counts['cancelled']}</b>
        </td>
        </tr>
        </table>
        <br>
        <h3>Toplam Bilgiler</h3>
        <table width="100%" cellpadding="15">
        <tr>
        <td style="background:#8b5cf6; color:white; border-radius:10px; text-align:center;">
            💰 Toplam Bütçe<br><b style="font-size:24px;">₺{self.db.total_budget():,.0f}</b>
        </td>
        <td style="background:#ec489a; color:white; border-radius:10px; text-align:center;">
            🏨 Toplam Otel Harcaması<br><b style="font-size:24px;">₺{self.db.total_hotel_cost():,.0f}</b>
        </td>
        <td style="background:#14b8a6; color:white; border-radius:10px; text-align:center;">
            🍽️ Toplam Diğer Harcama<br><b style="font-size:24px;">₺{self.db.total_expenses():,.0f}</b>
        </td>
        </tr>
        </table>
        """

        stats_label = QLabel(stats_text)
        stats_label.setWordWrap(True)
        stats_label.setStyleSheet("padding: 20px;")

        layout.addWidget(stats_label)
        layout.addStretch()

        self.stats_page.setLayout(layout)

    def go_dashboard(self):
        self.stack.setCurrentIndex(0)
        self.update_dashboard()

    def go_trips(self):
        self.stack.setCurrentIndex(1)
        self.load_trips()

    def go_add(self):
        self.stack.setCurrentIndex(2)

    def go_budget(self):
        self.stack.setCurrentIndex(3)
        self.update_budget_page()

    def go_stats(self):
        self.stack.setCurrentIndex(4)


# ================= ÇALIŞTIR =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = TravelApp()
    window.show()
    sys.exit(app.exec_())
