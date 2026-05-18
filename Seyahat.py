import sys
import sqlite3
import random
import traceback
from hashlib import sha256
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QMessageBox, 
                             QStackedWidget, QFrame, QComboBox, QDateEdit, 
                             QTimeEdit, QDoubleSpinBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QGridLayout, QDialog, 
                             QAbstractItemView, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QDate, QTime, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QColor

# --- MODERN, ESNEK VE GELİŞMİŞ GLOBAL STİL (QSS) ---
GLOBAL_STYLE = """
    QWidget {
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        color: #2c3e50;
    }
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QDoubleSpinBox {
        padding: 12px 15px;
        border: 2px solid #e0e6ed;
        border-radius: 8px;
        background-color: #fdfdfd;
        color: #34495e;
        font-size: 15px;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QDoubleSpinBox:focus {
        border: 2px solid #3498db;
        background-color: #ffffff;
    }
    QPushButton {
        border-radius: 8px;
        font-weight: bold;
        padding: 12px 15px;
        font-size: 15px;
        border: none;
    }
    QTableWidget {
        border: 1px solid #e0e6ed;
        border-radius: 10px;
        background-color: white;
        gridline-color: #ecf0f1;
        alternate-background-color: #fbfcfc;
    }
    QHeaderView::section:horizontal {
        background-color: #2c3e50;
        color: white;
        padding: 12px;
        font-weight: bold;
        border: none;
        border-right: 1px solid #34495e;
    }
    QHeaderView::section:vertical {
        background-color: #2c3e50;
        color: white;
        padding: 2px 8px;
        font-weight: bold;
        border: none;
        border-bottom: 1px solid #34495e;
    }
    QDialog {
        background-color: #f4f7f6;
    }
"""

# GRADIENT (RENK GEÇİŞLİ) BUTON STİLLERİ
BTN_BLUE = """QPushButton { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980b9, stop:1 #3498db); color: white; } 
              QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1f618d, stop:1 #2980b9); }"""
BTN_GREEN = """QPushButton { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #27ae60, stop:1 #2ecc71); color: white; } 
               QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e8449, stop:1 #27ae60); }"""
BTN_RED = """QPushButton { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c0392b, stop:1 #e74c3c); color: white; } 
             QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #922b21, stop:1 #c0392b); }"""
BTN_PURPLE = """QPushButton { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8e44ad, stop:1 #9b59b6); color: white; } 
                QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6c3483, stop:1 #8e44ad); }"""
BTN_ORANGE = """QPushButton { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d35400, stop:1 #f39c12); color: white; } 
                QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a04000, stop:1 #d35400); }"""
BTN_DARK = """QPushButton { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2c3e50, stop:1 #34495e); color: white; } 
              QPushButton:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a252f, stop:1 #2c3e50); }"""

def golge_ekle(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setXOffset(0)
    shadow.setYOffset(5)
    shadow.setColor(QColor(0, 0, 0, 40))
    widget.setGraphicsEffect(shadow)

# --- 1. VERİTABANI VE MANTIK ---
DB_NAME = "seyahat_v27_iklim.db" 

# İklim Tipi eklenmiş global rehber
SEHIR_REHBERI = {
    "İstanbul": {"iklim": "Ilıman", "yerler": "Ayasofya, Topkapı Sarayı, Galata Kulesi", "aktiviteler": "Boğaz turu yapmak, Kapalıçarşı'da alışveriş, Adalar'da bisiklet sürmek"},
    "Ankara": {"iklim": "Ilıman", "yerler": "Anıtkabir, Ankara Kalesi, Kocatepe Camii", "aktiviteler": "Kuğulu Park'ta yürüyüş, müzeleri gezmek, Kale'de kahve içmek"},
    "İzmir": {"iklim": "Sıcak", "yerler": "Saat Kulesi, Kemeraltı Çarşısı, Kordon", "aktiviteler": "Kordon'da çimlerde oturmak, boyoz tatmak, Efes Antik Kenti'ni keşfetmek"},
    "Antalya": {"iklim": "Sıcak", "yerler": "Kaleiçi, Düden Şelalesi, Aspendos", "aktiviteler": "Konyaaltı'nda denize girmek, tekne turu, tarihi sokaklarda fotoğraf çekilmek"},
    "Bursa": {"iklim": "Ilıman", "yerler": "Ulu Cami, Yeşil Türbe, Uludağ", "aktiviteler": "Teleferikle Uludağ'a çıkmak, İskender kebap yemek, Koza Han'da ipek bakmak"},
    "Eskişehir": {"iklim": "Ilıman", "yerler": "Odunpazarı Evleri, Sazova Parkı, Porsuk Çayı", "aktiviteler": "Porsuk'ta gondol turu, lületaşı atölyelerini gezmek, çiğbörek denemek"},
    "Trabzon": {"iklim": "Soğuk", "yerler": "Sümela Manastırı, Uzungöl, Boztepe", "aktiviteler": "Boztepe'de semaverde çay, yayla yürüyüşü, Karadeniz pidesi yemek"},
    "Amsterdam": {"iklim": "Soğuk", "yerler": "Kanallar, Van Gogh Müzesi, Dam Meydanı", "aktiviteler": "Kanallarda tekne turu, bisikletle şehri gezmek, peynir tadımı yapmak"},
    "Atina": {"iklim": "Sıcak", "yerler": "Akropolis, Parthenon, Plaka", "aktiviteler": "Tarihi kalıntıları fotoğraflamak, Yunan tavernalarında sirtaki izlemek"},
    "Barselona": {"iklim": "Sıcak", "yerler": "La Sagrada Familia, Park Güell, La Rambla", "aktiviteler": "Gaudí mimarisini incelemek, Tapas ve Paella tatmak, plajda vakit geçirmek"},
    "Belgrad": {"iklim": "Ilıman", "yerler": "Kalemegdan, Knez Mihailova", "aktiviteler": "Tuna ve Sava nehirlerinin birleşimini izlemek, gece hayatını deneyimlemek"},
    "Berlin": {"iklim": "Soğuk", "yerler": "Brandenburg Kapısı, Berlin Duvarı, Reichstag", "aktiviteler": "Müzeler Adası'nı gezmek, sokak sanatlarını incelemek, Currywurst yemek"},
    "Bratislava": {"iklim": "Ilıman", "yerler": "Bratislava Kalesi, St. Martin Katedrali", "aktiviteler": "Tuna nehri kıyısında yürüyüş, UFO köprüsüne çıkmak, eski şehri turlamak"},
    "Brugge": {"iklim": "Soğuk", "yerler": "Belfry Kulesi, Çikolata Müzesi, Minnewater", "aktiviteler": "Ortaçağ sokaklarında kaybolmak, Belçika çikolatası atölyesine katılmak"},
    "Brüksel": {"iklim": "Ilıman", "yerler": "Grand Place, Atomium, Manneken Pis", "aktiviteler": "Avrupa Parlamentosu'nu görmek, waffle ve midye yemek"},
    "Budapeşte": {"iklim": "Ilıman", "yerler": "Parlamento Binası, Buda Kalesi, Zincir Köprü", "aktiviteler": "Tarihi termal hamamlara girmek, Tuna nehrinde akşam yemeği turu"},
    "Bükreş": {"iklim": "Ilıman", "yerler": "Parlamento Sarayı, Eski Şehir", "aktiviteler": "Büyük parklarda bisiklet sürmek, geleneksel Rumen mutfağını tatmak"},
    "Cenevre": {"iklim": "Soğuk", "yerler": "Cenevre Gölü, Jet d'Eau", "aktiviteler": "Göl etrafında piknik, İsviçre saat mağazalarını gezmek"},
    "Dublin": {"iklim": "Soğuk", "yerler": "Guinness Storehouse, Temple Bar, Trinity College", "aktiviteler": "Canlı İrlanda müziği dinlemek, eski kütüphaneleri keşfetmek"},
    "Edinburgh": {"iklim": "Soğuk", "yerler": "Edinburgh Kalesi, Royal Mile, Arthur's Seat", "aktiviteler": "Tepeden şehri izlemek, tarihi publarda vakit geçirmek, gayda dinlemek"},
    "Roma": {"iklim": "Sıcak", "yerler": "Kolezyum, Trevi Çeşmesi, Pantheon, Vatikan", "aktiviteler": "Aşk çeşmesine para atmak, gladyatör arenasını gezmek, hakiki dondurma (Gelato) yemek"},
    "Paris": {"iklim": "Ilıman", "yerler": "Eyfel Kulesi, Louvre Müzesi, Şanzelize", "aktiviteler": "Seine nehrinde tekne turu, kruvasan ve kahve keyfi, Mona Lisa'yı görmek"},
    "New York": {"iklim": "Ilıman", "yerler": "Özgürlük Anıtı, Central Park, Times Meydanı", "aktiviteler": "Broadway şovu izlemek, Central Park'ta fayton turu, gökdelen tepesine çıkmak"},
    "Tokyo": {"iklim": "Ilıman", "yerler": "Senso-ji, Shibuya Geçidi, Tokyo Skytree, Shinjuku", "aktiviteler": "Dünyanın en kalabalık yaya geçidinden geçmek, anime/manga bölgelerini gezmek, Sushi yemek"},
    "Helsinki": {"iklim": "Soğuk", "yerler": "Suomenlinna, Senato Meydanı", "aktiviteler": "Deniz kalesini gezmek, geleneksel Fin saunasına girmek"},
    "Kopenhag": {"iklim": "Soğuk", "yerler": "Tivoli Bahçeleri, Nyhavn, Küçük Deniz Kızı", "aktiviteler": "Eğlence parkında vakit geçirmek, renkli evlerin önünde fotoğraf çekilmek"},
    "Oslo": {"iklim": "Soğuk", "yerler": "Vigeland Park, Viking Gemi Müzesi, Opera Binası", "aktiviteler": "Heykel parkında dolaşmak, Viking tarihini öğrenmek"},
    "Dubai": {"iklim": "Sıcak", "yerler": "Burj Khalifa, Dubai Mall, Palm Jumeirah", "aktiviteler": "Çölde safari ve ATV turu, dünyanın en yüksek binasından manzarayı izlemek"},
    "Miami": {"iklim": "Sıcak", "yerler": "South Beach, Everglades Ulusal Parkı, Little Havana", "aktiviteler": "Timsah turuna çıkmak, beyaz kumsallarda yüzmek, Küba kahvesi içmek"},
    "Singapur": {"iklim": "Sıcak", "yerler": "Marina Bay Sands, Gardens by the Bay, Universal Studios", "aktiviteler": "Işıklı dev yapay ağaçların gösterisini izlemek, gece safarisine katılmak"}
}

# --- İKLİME DUYARLI YENİ HAVA DURUMU MOTORU ---
def dinamik_hava_durumu_getir(sehir, tarih_str, iklim="Ilıman"):
    random.seed(sehir + tarih_str)
    try: ay = int(tarih_str.split('.')[1])
    except: ay = 5 
        
    # Şehrin iklim tipine göre taban sıcaklığı (Base Temperature) belirlenir
    if iklim == "Soğuk":
        if ay in [12, 1, 2]: base = random.randint(-15, -2)
        elif ay in [3, 4, 10, 11]: base = random.randint(-5, 8)
        else: base = random.randint(10, 18)
    elif iklim == "Sıcak":
        if ay in [12, 1, 2]: base = random.randint(15, 22)
        elif ay in [3, 4, 10, 11]: base = random.randint(22, 30)
        else: base = random.randint(30, 42)
    else: # Ilıman
        if ay in [12, 1, 2]: base = random.randint(0, 10)
        elif ay in [3, 4, 10, 11]: base = random.randint(10, 20)
        else: base = random.randint(22, 32)
    
    temp = base + random.randint(-3, 3)
    
    durumlar = ["Güneşli ☀️", "Parçalı Bulutlu ⛅", "Sağanak Yağışlı 🌧️", "Açık 🌤️", "Bulutlu ☁️"]
    if temp < 5: 
        durumlar.extend(["Karlı ❄️", "Yoğun Kar Yağışlı 🌨️", "Sulu Kar 🌨️", "Buzlanma 🧊"])
    elif temp > 30:
        durumlar.extend(["Çok Sıcak 🌡️", "Bunaltıcı Nem 💧"])
        
    secilen_durum = random.choice(durumlar)
    random.seed() 
    return f"{temp}°C, {secilen_durum}"

def veritabani_hazirla():
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT UNIQUE NOT NULL,
            sifre TEXT NOT NULL,
            ad_soyad TEXT,
            telefon TEXT,
            dogum_tarihi TEXT,
            bakiye REAL DEFAULT 25000.0
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS seferler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kalkis TEXT NOT NULL,
            varis TEXT NOT NULL,
            tarih TEXT NOT NULL,
            saat TEXT NOT NULL,
            fiyat REAL NOT NULL,
            kapasite INTEGER DEFAULT 40,
            durum TEXT DEFAULT 'Planlandı'
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS biletler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER,
            sefer_id INTEGER,
            koltuk_no INTEGER,
            odenen_tutar REAL,
            UNIQUE(sefer_id, koltuk_no)
        )""")
        # İKLİM SÜTUNU EKLENDİ
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sehirler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT UNIQUE NOT NULL,
            yerler TEXT NOT NULL,
            aktiviteler TEXT NOT NULL,
            iklim TEXT DEFAULT 'Ilıman'
        )""")
        baglanti.commit()
    admin_olustur()
    sehirleri_veritabanina_aktar()
    ornek_seferleri_yukle()
    ornek_yolculari_ve_biletleri_yukle()

def sehirleri_veritabanina_aktar():
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        cursor.execute("SELECT COUNT(*) FROM sehirler")
        if cursor.fetchone()[0] == 0:
            for isim, detay in SEHIR_REHBERI.items():
                iklim = detay.get("iklim", "Ilıman")
                aktivite = detay.get("aktiviteler", "Aktivite bulunmuyor.")
                cursor.execute("INSERT INTO sehirler (isim, yerler, aktiviteler, iklim) VALUES (?, ?, ?, ?)", 
                               (isim, detay["yerler"], aktivite, iklim))
            baglanti.commit()

def sehir_isimlerini_getir():
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        cursor.execute("SELECT isim FROM sehirler ORDER BY isim ASC")
        return [row[0] for row in cursor.fetchall()]

def sehir_detay_getir(sehir_adi):
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        cursor.execute("SELECT yerler, aktiviteler, iklim FROM sehirler WHERE isim = ?", (sehir_adi,))
        sonuc = cursor.fetchone()
        if sonuc: return {"yerler": sonuc[0], "aktiviteler": sonuc[1], "iklim": sonuc[2]}
        return {"yerler": "Bilinmiyor", "aktiviteler": "Bilinmiyor", "iklim": "Ilıman"}

def sehir_ekle_db(isim, yerler, aktiviteler, iklim):
    try:
        with sqlite3.connect(DB_NAME) as baglanti:
            cursor = baglanti.cursor()
            isim = isim.strip().title()
            cursor.execute("INSERT INTO sehirler (isim, yerler, aktiviteler, iklim) VALUES (?, ?, ?, ?)", (isim, yerler, aktiviteler, iklim))
            baglanti.commit()
            return True
    except: return False

def admin_olustur():
    k_adi, sifre = "admin", "1234"
    sifre_hash = sha256(sifre.encode()).hexdigest()
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = ?", (k_adi,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, ad_soyad, telefon, dogum_tarihi, bakiye) VALUES (?, ?, ?, ?, ?, ?)", 
                           (k_adi, sifre_hash, "Sistem Yöneticisi", "00000000000", "01.01.1990", 999999.0))
            baglanti.commit()

def ornek_seferleri_yukle():
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        cursor.execute("SELECT COUNT(*) FROM seferler")
        if cursor.fetchone()[0] == 0:
            ornekler = []
            sehirler_listesi = sehir_isimlerini_getir()
            for _ in range(60):
                kalkis = random.choice(sehirler_listesi)
                varis = random.choice(sehirler_listesi)
                while kalkis == varis: varis = random.choice(sehirler_listesi)
                
                ay = random.choice([4, 5, 6]) 
                gun = random.randint(1, 28)
                tarih = f"{gun:02d}.{ay:02d}.2026"
                saat = f"{random.randint(0, 23):02d}:{random.choice(['00', '15', '30', '45'])}"
                fiyat = float(random.randint(15, 350) * 100) 
                ornekler.append((kalkis, varis, tarih, saat, fiyat))
            for s in ornekler:
                cursor.execute("INSERT INTO seferler (kalkis, varis, tarih, saat, fiyat) VALUES (?, ?, ?, ?, ?)", s)
            baglanti.commit()

def ornek_yolculari_ve_biletleri_yukle():
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        cursor.execute("SELECT COUNT(*) FROM kullanicilar WHERE kullanici_adi != 'admin'")
        if cursor.fetchone()[0] == 0:
            isimler = ["Ahmet", "Mehmet", "Ali", "Veli", "Can", "Ece", "Elif", "Zeynep", "Murat", "Burak", "Hakan", "Selin", "Aslı", "Deniz"]
            soyisimler = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Öztürk", "Arslan", "Aydın"]
            sifre_hash = sha256("1234".encode()).hexdigest()
            yolcu_idleri = []
            for i in range(1, 101):
                k_adi = f"yolcu{i}"
                ad = random.choice(isimler) + " " + random.choice(soyisimler)
                tel = f"0555{random.randint(1000000, 9999999)}"
                dt = f"{random.randint(1,28):02d}.{random.randint(1,12):02d}.{random.randint(1980,2010)}"
                cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, ad_soyad, telefon, dogum_tarihi, bakiye) VALUES (?, ?, ?, ?, ?, ?)",
                               (k_adi, sifre_hash, ad, tel, dt, 500000.0))
                yolcu_idleri.append(cursor.lastrowid)
            
            cursor.execute("SELECT id, fiyat FROM seferler")
            seferler = cursor.fetchall()
            for sefer in seferler:
                sefer_id, fiyat = sefer
                yolcu_sayisi = random.randint(10, 35)
                secilen_yolcular = random.sample(yolcu_idleri, yolcu_sayisi)
                koltuklar = random.sample(range(1, 41), yolcu_sayisi)
                for i in range(yolcu_sayisi):
                    try:
                        cursor.execute("UPDATE kullanicilar SET bakiye = bakiye - ? WHERE id = ?", (fiyat, secilen_yolcular[i]))
                        cursor.execute("INSERT INTO biletler (kullanici_id, sefer_id, koltuk_no, odenen_tutar) VALUES (?, ?, ?, ?)",
                                       (secilen_yolcular[i], sefer_id, koltuklar[i], fiyat))
                    except: pass
            baglanti.commit()

def kullanici_kaydet(k_adi, sifre, ad_soyad, telefon, d_tarihi):
    sifre_hash = sha256(sifre.encode()).hexdigest()
    try:
        with sqlite3.connect(DB_NAME) as baglanti:
            cursor = baglanti.cursor()
            cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, ad_soyad, telefon, dogum_tarihi) VALUES (?, ?, ?, ?, ?)", 
                           (k_adi, sifre_hash, ad_soyad, telefon, d_tarihi))
            baglanti.commit()
            return True
    except: return False

def kullanici_kontrol(k_adi, sifre):
    sifre_hash = sha256(sifre.encode()).hexdigest()
    try:
        with sqlite3.connect(DB_NAME) as baglanti:
            cursor = baglanti.cursor()
            cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?", (k_adi, sifre_hash))
            return cursor.fetchone()
    except: return None

def kullanici_getir_by_id(uid):
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        cursor.execute("SELECT * FROM kullanicilar WHERE id = ?", (uid,))
        return cursor.fetchone()

def bakiye_artir(uid, miktar):
    try:
        with sqlite3.connect(DB_NAME) as baglanti:
            cursor = baglanti.cursor()
            cursor.execute("UPDATE kullanicilar SET bakiye = bakiye + ? WHERE id = ?", (miktar, uid))
            baglanti.commit()
            return True
    except: return False

def seferleri_getir():
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        cursor.execute("SELECT id, kalkis, varis, tarih, saat, fiyat, durum FROM seferler")
        seferler = cursor.fetchall()
        
        guncel_seferler = []
        bugun = QDate.currentDate()
        suan = QTime.currentTime()
        
        for s in seferler:
            s_list = list(s)
            if s_list[6] == 'Planlandı':
                s_tarih = QDate.fromString(s_list[3], "dd.MM.yyyy")
                s_saat = QTime.fromString(s_list[4], "HH:mm")
                if s_tarih < bugun or (s_tarih == bugun and s_saat <= suan):
                    s_list[6] = 'Tamamlandı'
                    cursor.execute("UPDATE seferler SET durum = 'Tamamlandı' WHERE id = ?", (s_list[0],))
            guncel_seferler.append(tuple(s_list))
            
        baglanti.commit()
        return guncel_seferler

def sefer_ekle(k, v, t, s, f):
    try:
        with sqlite3.connect(DB_NAME) as baglanti:
            cursor = baglanti.cursor()
            cursor.execute("INSERT INTO seferler (kalkis, varis, tarih, saat, fiyat, durum) VALUES (?, ?, ?, ?, ?, 'Planlandı')", (k, v, t, s, f))
            baglanti.commit()
            return True
    except: return False

def sefer_sil(sefer_id):
    try:
        with sqlite3.connect(DB_NAME) as baglanti:
            cursor = baglanti.cursor()
            cursor.execute("SELECT kullanici_id, odenen_tutar FROM biletler WHERE sefer_id = ?", (sefer_id,))
            satilan_biletler = cursor.fetchall()
            for bilet in satilan_biletler:
                cursor.execute("UPDATE kullanicilar SET bakiye = bakiye + ? WHERE id = ?", (bilet[1], bilet[0]))
            cursor.execute("DELETE FROM biletler WHERE sefer_id = ?", (sefer_id,))
            cursor.execute("UPDATE seferler SET durum = 'İptal Edildi' WHERE id = ?", (sefer_id,))
            baglanti.commit()
            return True, f"Sefer iptal edildi. {len(satilan_biletler)} yolcuya iade yapıldı."
    except Exception as e: return False, str(e)

def dolu_koltuklari_getir(sefer_id):
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        cursor.execute("SELECT koltuk_no FROM biletler WHERE sefer_id = ?", (sefer_id,))
        return [row[0] for row in cursor.fetchall()]

def bilet_satin_al(k_id, s_id, koltuk_no, fiyat):
    try:
        with sqlite3.connect(DB_NAME) as baglanti:
            cursor = baglanti.cursor()
            cursor.execute("SELECT bakiye FROM kullanicilar WHERE id = ?", (k_id,))
            bakiye = cursor.fetchone()[0]
            if bakiye < fiyat: return False, "Yetersiz bakiye!"
            cursor.execute("UPDATE kullanicilar SET bakiye = bakiye - ? WHERE id = ?", (fiyat, k_id))
            cursor.execute("INSERT INTO biletler (kullanici_id, sefer_id, koltuk_no, odenen_tutar) VALUES (?, ?, ?, ?)", (k_id, s_id, koltuk_no, fiyat))
            baglanti.commit()
            return True, "Bilet başarıyla alındı!"
    except sqlite3.IntegrityError: return False, "Koltuk dolu!"
    except Exception as e: return False, str(e)

def kullanici_biletlerini_getir(k_id):
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        sorgu = "SELECT b.id, s.kalkis, s.varis, s.tarih, s.saat, b.koltuk_no, b.odenen_tutar, s.durum FROM biletler b JOIN seferler s ON b.sefer_id = s.id WHERE b.kullanici_id = ?"
        cursor.execute(sorgu, (k_id,))
        return cursor.fetchall()

def bilet_iptal_et(bilet_id):
    try:
        with sqlite3.connect(DB_NAME) as baglanti:
            cursor = baglanti.cursor()
            cursor.execute("SELECT kullanici_id, odenen_tutar FROM biletler WHERE id = ?", (bilet_id,))
            row = cursor.fetchone()
            if not row: return False, "Bilet bulunamadı!"
            k_id, iade_tutari = row
            cursor.execute("DELETE FROM biletler WHERE id = ?", (bilet_id,))
            cursor.execute("UPDATE kullanicilar SET bakiye = bakiye + ? WHERE id = ?", (iade_tutari, k_id))
            baglanti.commit()
            return True, f"Bilet iptal edildi.\n{iade_tutari:.2f} TL hesabınıza iade edilmiştir."
    except Exception as e: return False, f"İptal işlemi başarısız: {e}"

def sefer_yolculari_getir(sefer_id):
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        sorgu = """
        SELECT b.koltuk_no, k.ad_soyad, k.telefon, b.odenen_tutar 
        FROM biletler b JOIN kullanicilar k ON b.kullanici_id = k.id 
        WHERE b.sefer_id = ? ORDER BY b.koltuk_no ASC
        """
        cursor.execute(sorgu, (sefer_id,))
        return cursor.fetchall()

def donus_bileti_kontrol_et(kullanici_id, kalkis, varis, donus_tarih_str):
    with sqlite3.connect(DB_NAME) as baglanti:
        cursor = baglanti.cursor()
        sorgu = """
        SELECT b.koltuk_no, s.tarih FROM biletler b 
        JOIN seferler s ON b.sefer_id = s.id 
        WHERE b.kullanici_id = ? AND s.kalkis = ? AND s.varis = ? AND s.durum != 'İptal Edildi'
        """
        cursor.execute(sorgu, (kullanici_id, varis, kalkis))
        gidis_biletleri = cursor.fetchall()
        d_tarih = QDate.fromString(donus_tarih_str, "dd.MM.yyyy")
        for bilet in gidis_biletleri:
            g_tarih = QDate.fromString(bilet[1], "dd.MM.yyyy")
            if d_tarih >= g_tarih: return bilet[0]
        return None

# --- 2. DİALOG VE YAN BİLEŞENLER ---
class PasswordField(QWidget):
    def __init__(self, placeholder):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        self.input.setStyleSheet("border-top-right-radius: 0px; border-bottom-right-radius: 0px; border-right: none;")
        self.input.setMinimumHeight(55)
        
        self.btn = QPushButton("👁")
        self.btn.setFixedWidth(55)
        self.btn.setMinimumHeight(55)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa; 
                border: 2px solid #e0e6ed; 
                border-left: none; 
                border-top-left-radius: 0px; 
                border-bottom-left-radius: 0px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                color: #2c3e50;
                font-size: 18px;
            }
            QPushButton:hover { background-color: #eaeded; }
        """)
        self.btn.pressed.connect(lambda: self.input.setEchoMode(QLineEdit.EchoMode.Normal))
        self.btn.released.connect(lambda: self.input.setEchoMode(QLineEdit.EchoMode.Password))
        
        layout.addWidget(self.input)
        layout.addWidget(self.btn)

class SehirDetayPenceresi(QDialog):
    def __init__(self, sehir, tarih, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{sehir} Şehir Rehberi")
        self.setFixedSize(500, 360)
        self.setStyleSheet("background-color: white; border-radius: 10px;")
        golge_ekle(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        veriler = sehir_detay_getir(sehir)
        iklim_tipi = veriler.get("iklim", "Ilıman")
        
        # İKLİM TİPİ VERİLERE EKLENDİ
        guncel_hava = dinamik_hava_durumu_getir(sehir, tarih, iklim_tipi)
        
        lbl_baslik = QLabel(f"<h1 style='color:#2980b9; margin:0;'>🌍 {sehir}</h1>")
        lbl_baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_baslik)
        
        lbl_hava = QLabel(f"<span style='font-size:15px; color:#d35400;'><b>🌤 {tarih} Uçuşu İçin Canlı Hava Tahmini:</b><br>{guncel_hava} ({iklim_tipi} İklim)</span>")
        lbl_hava.setStyleSheet("background-color: #fdf2e9; padding: 10px; border-radius: 8px;")
        layout.addWidget(lbl_hava)
        
        lbl_yerler = QLabel(f"<span style='font-size:15px; color:#34495e;'><b>📍 Gezilecek Yerler:</b><br>{veriler['yerler']}</span>")
        lbl_yerler.setWordWrap(True)
        layout.addWidget(lbl_yerler)
        
        lbl_akt = QLabel(f"<span style='font-size:15px; color:#27ae60;'><b>🎯 Yapılabilecek Aktiviteler:</b><br>{veriler['aktiviteler']}</span>")
        lbl_akt.setWordWrap(True)
        layout.addWidget(lbl_akt)
        
        layout.addStretch()
        
        btn = QPushButton("Kapat")
        btn.setStyleSheet(BTN_DARK)
        btn.clicked.connect(self.close)
        layout.addWidget(btn)

class BiletCiktisiPenceresi(QDialog):
    def __init__(self, bilet_detay, yolcu_adi, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✈️ Dijital Biniş Kartı")
        self.setFixedSize(520, 340)
        self.setStyleSheet("background-color: #fdfdfd; border-radius: 12px; border: 2px dashed #3498db;")
        golge_ekle(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        lbl_baslik = QLabel("<h2 style='color:#2980b9; margin:0; text-align:center;'>SKYBOUND AIRLINES</h2><p style='color:#7f8c8d; margin:0; text-align:center;'>Biniş Kartı / Boarding Pass</p>")
        lbl_baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_baslik)
        
        layout.addSpacing(15)

        bilgi_html = f"""
        <table width='100%' style='font-size:15px; color:#2c3e50;'>
            <tr>
                <td style='padding-bottom:12px;'><b>Yolcu:</b> {yolcu_adi}</td>
                <td style='padding-bottom:12px;'><b>Koltuk:</b> <span style='color:#d35400; font-weight:bold;'>{bilet_detay[5]}</span></td>
            </tr>
            <tr>
                <td style='padding-bottom:12px;'><b>Kalkış:</b> {bilet_detay[1]}</td>
                <td style='padding-bottom:12px;'><b>Varış:</b> {bilet_detay[2]}</td>
            </tr>
            <tr>
                <td style='padding-bottom:12px;'><b>Tarih:</b> {bilet_detay[3]}</td>
                <td style='padding-bottom:12px;'><b>Saat:</b> {bilet_detay[4]}</td>
            </tr>
            <tr>
                <td colspan='2' style='padding-top:12px; border-top:1px solid #ecf0f1;'>
                    <b style='color:#27ae60;'>Ödenen Tutar:</b> {bilet_detay[6]:.2f} TL
                </td>
            </tr>
        </table>
        """
        lbl_bilgi = QLabel(bilgi_html)
        layout.addWidget(lbl_bilgi)

        barkod_html = f"""
        <div style='text-align:center; font-family:monospace; font-size:24px; font-weight:bold; letter-spacing:5px; color:#34495e;'>
            ||||| |||| || ||||||| |||| ||
            <br><span style='font-size:12px; letter-spacing:2px; color:#7f8c8d;'>SB-TKT-{bilet_detay[0]}-2026</span>
        </div>
        """
        lbl_barkod = QLabel(barkod_html)
        lbl_barkod.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_barkod)

        layout.addStretch()
        
        btn = QPushButton("Kapat")
        btn.setStyleSheet("QPushButton { background-color: #34495e; color: white; padding:8px; border-radius:4px; } QPushButton:hover { background-color: #2c3e50; }")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)

class BiletlerimPenceresi(QDialog):
    def __init__(self, kullanici_id, parent=None):
        super().__init__(parent)
        self.kullanici_id = kullanici_id
        self.setWindowTitle("Geçmiş ve Aktif Biletlerim")
        self.setMinimumSize(850, 480)
        self.setStyleSheet("background-color: #f8f9fa;")
        golge_ekle(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("<h2 style='color:#2c3e50; margin:0;'>🎟 Biletlerim</h2>"))
        
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["KALKIŞ", "VARIŞ", "TARİH", "SAAT", "KOLTUK", "ÖDENEN", "DURUM"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(15)
        
        btn_goruntule = QPushButton("🎫 BİNİŞ KARTINI GÖRÜNTÜLE")
        btn_goruntule.setStyleSheet(BTN_BLUE)
        btn_goruntule.clicked.connect(self.bileti_goruntule)
        btn_lay.addWidget(btn_goruntule)
        
        btn_iptal = QPushButton("BİLETİ İPTAL ET VE İADE AL")
        btn_iptal.setStyleSheet(BTN_RED)
        btn_iptal.clicked.connect(self.iptal_et)
        btn_lay.addWidget(btn_iptal)
        
        layout.addLayout(btn_lay)
        self.yukle()

    def yukle(self):
        self.data = kullanici_biletlerini_getir(self.kullanici_id)
        self.table.setRowCount(len(self.data))
        for i, b in enumerate(self.data):
            for j in range(1, 5): 
                self.table.setItem(i, j-1, QTableWidgetItem(str(b[j])))
            self.table.setItem(i, 4, QTableWidgetItem(f"Koltuk {b[5]}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{b[6]:.2f} TL"))
            
            item_durum = QTableWidgetItem(str(b[7]))
            item_durum.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font = item_durum.font()
            font.setBold(True)
            item_durum.setFont(font)
            
            if b[7] == 'Tamamlandı': item_durum.setForeground(QColor("#27ae60"))
            elif b[7] == 'İptal Edildi': item_durum.setForeground(QColor("#c0392b"))
            else: item_durum.setForeground(QColor("#f39c12"))
            self.table.setItem(i, 6, item_durum)

    def bileti_goruntule(self):
        row = self.table.currentRow()
        if row < 0:
            return QMessageBox.warning(self, "Uyarı", "Lütfen görüntülemek istediğiniz bileti tablodan seçin!")
        
        bilet_data = self.data[row]
        yolcu = kullanici_getir_by_id(self.kullanici_id)
        BiletCiktisiPenceresi(bilet_data, yolcu[3], self).exec()

    def iptal_et(self):
        row = self.table.currentRow()
        if row < 0: return
        
        if self.data[row][7] == 'Tamamlandı':
            return QMessageBox.warning(self, "Uyarı", "Uçuşu gerçekleşmiş (Tamamlanmış) bir bileti iptal edemezsiniz!")
        if self.data[row][7] == 'İptal Edildi':
            return QMessageBox.warning(self, "Uyarı", "Bu biletin ait olduğu sefer zaten iptal edilmiş!")
            
        cevap = QMessageBox.question(self, "İptal Onayı", "Seçili bileti iptal edip ücret iadesi almak istiyor musunuz?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if cevap == QMessageBox.StandardButton.Yes:
            basarili, msg = bilet_iptal_et(self.data[row][0])
            QMessageBox.information(self, "İşlem Sonucu", msg)
            self.yukle()

class BakiyeYuklePenceresi(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cüzdan - Para Yükle")
        self.setFixedSize(340, 240)
        self.setStyleSheet("background-color: white; border-radius: 10px;")
        golge_ekle(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        layout.addWidget(QLabel("<h3 style='color:#2c3e50; text-align:center; margin:0;'>💳 Yüklenecek Tutar</h3>"))
        layout.addSpacing(10)
        
        self.spin = QDoubleSpinBox()
        self.spin.setRange(100, 100000)
        self.spin.setValue(5000)
        self.spin.setSuffix(" TL")
        self.spin.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60;")
        layout.addWidget(self.spin)
        
        layout.addStretch()
        btn = QPushButton("ÖDEMEYİ ONAYLA")
        btn.setStyleSheet(BTN_GREEN)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

class SeferEklePenceresi(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Uçuş Planı Oluştur")
        self.setFixedSize(480, 450)
        self.setStyleSheet("background-color: white; border-radius: 10px;")
        golge_ekle(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("<h2 style='color:#2980b9; margin:0;'>✈️ Uçuş Bilgileri</h2>"))
        
        guncel_sehirler = sehir_isimlerini_getir()
        
        self.ck = QComboBox(); self.ck.addItems(guncel_sehirler)
        self.cv = QComboBox(); self.cv.addItems(guncel_sehirler)
        
        self.dt = QDateEdit(); self.dt.setCalendarPopup(True); self.dt.setDate(QDate.currentDate())
        
        takvim = self.dt.calendarWidget()
        takvim.setMinimumSize(350, 250)
        takvim.setStyleSheet("""
            QCalendarWidget QWidget { background-color: white; }
            QCalendarWidget QToolButton { height: 30px; font-size: 14px; font-weight: bold; }
            QCalendarWidget QAbstractItemView:enabled { font-size: 14px; selection-background-color: #2ecc71; selection-color: white; }
        """)

        self.tm = QTimeEdit(); self.tm.setTime(QTime.currentTime())
        self.pr = QDoubleSpinBox(); self.pr.setRange(0, 500000); self.pr.setSuffix(" TL")
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.addWidget(QLabel("<b>Kalkış Noktası:</b>"), 0, 0); form_layout.addWidget(self.ck, 0, 1)
        form_layout.addWidget(QLabel("<b>Varış Noktası:</b>"), 1, 0); form_layout.addWidget(self.cv, 1, 1)
        form_layout.addWidget(QLabel("<b>Tarih:</b>"), 2, 0); form_layout.addWidget(self.dt, 2, 1)
        form_layout.addWidget(QLabel("<b>Saat:</b>"), 3, 0); form_layout.addWidget(self.tm, 3, 1)
        form_layout.addWidget(QLabel("<b>Taban Fiyat:</b>"), 4, 0); form_layout.addWidget(self.pr, 4, 1)
        layout.addLayout(form_layout)
        
        layout.addStretch()
        btn = QPushButton("SEFERİ SİSTEME KAYDET")
        btn.setStyleSheet(BTN_ORANGE)
        btn.clicked.connect(self.save)
        layout.addWidget(btn)

    def save(self):
        if self.ck.currentText() == self.cv.currentText(): 
            return QMessageBox.warning(self, "Hata", "Kalkış ve Varış aynı şehir olamaz!")
        if sefer_ekle(self.ck.currentText(), self.cv.currentText(), self.dt.date().toString("dd.MM.yyyy"), self.tm.time().toString("HH:mm"), self.pr.value()): 
            self.accept()

class AdminYeniSehirPenceresi(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sisteme Yeni Şehir Ekle")
        self.setFixedSize(480, 480) # Yükseklik biraz artırıldı
        self.setStyleSheet("background-color: white; border-radius: 10px;")
        golge_ekle(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        layout.addWidget(QLabel("<h2 style='color:#8e44ad; margin:0;'>🌍 Yeni Destinasyon</h2>"))

        self.isim = QLineEdit(); self.isim.setPlaceholderText("Şehir Adı (Örn: Berlin)")
        
        # YENİ EKLENEN İKLİM KUTUSU
        self.iklim_cb = QComboBox()
        self.iklim_cb.addItems(["Soğuk", "Ilıman", "Sıcak"])
        
        self.yerler = QLineEdit(); self.yerler.setPlaceholderText("Gezilecek Yerler (Virgülle ayırın)")
        self.aktiviteler = QLineEdit(); self.aktiviteler.setPlaceholderText("Yapılabilecek Aktiviteler (Örn: Boğaz turu)")

        layout.addWidget(QLabel("<b>Şehir Adı:</b>")); layout.addWidget(self.isim)
        layout.addWidget(QLabel("<b>İklim Tipi:</b>")); layout.addWidget(self.iklim_cb)
        layout.addWidget(QLabel("<b>Gezilecek Yerler:</b>")); layout.addWidget(self.yerler)
        layout.addWidget(QLabel("<b>Yapılabilecek Aktiviteler:</b>")); layout.addWidget(self.aktiviteler)
        
        layout.addStretch()
        btn = QPushButton("ŞEHRİ VERİTABANINA EKLE")
        btn.setStyleSheet(BTN_PURPLE)
        btn.clicked.connect(self.kaydet)
        layout.addWidget(btn)

    def kaydet(self):
        if not self.isim.text() or not self.yerler.text() or not self.aktiviteler.text():
            return QMessageBox.warning(self, "Hata", "Tüm alanları doldurmalısınız!")
            
        iklim_secimi = self.iklim_cb.currentText()
            
        if sehir_ekle_db(self.isim.text(), self.yerler.text(), self.aktiviteler.text(), iklim_secimi):
            QMessageBox.information(self, "Başarılı", f"{self.isim.text().title()} sisteme başarıyla eklendi!\nArtık seferlerde ve uçuş aramalarında görünecek.")
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", "Bu şehir zaten sistemde kayıtlı veya bir hata oluştu!")

class AdminSeferDetayPenceresi(QDialog):
    def __init__(self, sefer_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yolcu Manifestosu")
        self.setMinimumSize(680, 480)
        self.setStyleSheet("background-color: #f8f9fa;")
        golge_ekle(self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel(f"<h3 style='color:#2c3e50; margin:0;'>✈️ {sefer_data[1]} -> {sefer_data[2]} Uçuşu Yolcu Listesi</h3>"))
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["KOLTUK NO", "YOLCU ADI", "TELEFON", "ÖDENEN"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        yolcular = sefer_yolculari_getir(sefer_data[0])
        self.table.setRowCount(len(yolcular))
        
        toplam_gelir = 0
        for i, y in enumerate(yolcular):
            self.table.setItem(i, 0, QTableWidgetItem(f"Koltuk {y[0]}"))
            self.table.setItem(i, 1, QTableWidgetItem(y[1]))
            self.table.setItem(i, 2, QTableWidgetItem(y[2]))
            self.table.setItem(i, 3, QTableWidgetItem(f"{y[3]:.2f} TL"))
            toplam_gelir += y[3]
            
        layout.addWidget(QLabel(f"<span style='font-size:16px; color:#27ae60;'><b>👥 Toplam Doluluk:</b> {len(yolcular)}/40 &nbsp;&nbsp;|&nbsp;&nbsp; <b>💰 Kazanılan Toplam Gelir:</b> {toplam_gelir:.2f} TL</span>"))
        
        btn = QPushButton("Pencereyi Kapat")
        btn.setStyleSheet(BTN_DARK)
        btn.clicked.connect(self.close)
        layout.addWidget(btn)

# --- 3. ANA EKRAN BİLEŞENLERİ ---
class LoginScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        l = QVBoxLayout(self)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        f = QFrame()
        f.setFixedWidth(500)
        f.setStyleSheet("QFrame { background-color: white; border-radius: 16px; }")
        golge_ekle(f)
        
        fl = QVBoxLayout(f)
        fl.setContentsMargins(40, 50, 40, 50)
        fl.setSpacing(20)
        
        lbl_baslik = QLabel("<h1 style='color:#2980b9; margin:0; font-size:36px;'>✈️ SkyBound</h1><p style='color:#7f8c8d; margin:0; font-size:16px;'>Premium Biletleme Sistemi</p>")
        lbl_baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(lbl_baslik)
        
        fl.addSpacing(15)
        
        self.u = QLineEdit()
        self.u.setPlaceholderText("Kullanıcı Adı")
        self.u.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[^0-9]*$")))
        self.u.setMinimumHeight(55)
        self.u.setStyleSheet("font-size: 16px;")
        fl.addWidget(self.u)
        
        self.p = PasswordField("Şifre")
        fl.addWidget(self.p)
        
        fl.addSpacing(15)
        
        btn_giris = QPushButton("GİRİŞ YAP")
        btn_giris.setStyleSheet(BTN_BLUE)
        btn_giris.setMinimumHeight(55)
        font = btn_giris.font()
        font.setPointSize(12)
        btn_giris.setFont(font)
        btn_giris.clicked.connect(self.login)
        fl.addWidget(btn_giris)
        
        btn_yeni = QPushButton("Hesap Oluştur")
        btn_yeni.setStyleSheet("QPushButton { color: #3498db; background: transparent; font-weight: bold; font-size: 16px; } QPushButton:hover { color: #2980b9; text-decoration: underline; }")
        btn_yeni.clicked.connect(self.hesap_olustura_git)
        fl.addWidget(btn_yeni)
        
        l.addWidget(f)

    def hesap_olustura_git(self):
        self.parent.setCurrentIndex(1)

    def login(self):
        user = kullanici_kontrol(self.u.text(), self.p.input.text())
        if user: 
            self.parent.login_basarili(user)
        else: 
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre hatalı!")

class RegisterScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        l = QVBoxLayout(self)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        f = QFrame()
        f.setFixedWidth(550)
        f.setStyleSheet("QFrame { background-color: white; border-radius: 16px; }")
        golge_ekle(f)
        
        fl = QVBoxLayout(f)
        fl.setContentsMargins(40, 40, 40, 40)
        fl.setSpacing(15)
        
        lbl = QLabel("<h2 style='color:#2c3e50; margin:0; font-size:28px;'>Sisteme Kayıt Ol</h2>")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(lbl)
        
        fl.addSpacing(10)
        
        harf_val = QRegularExpressionValidator(QRegularExpression(r"^[^0-9]*$"))
        
        self.n = QLineEdit()
        self.n.setPlaceholderText("Ad Soyad")
        self.n.setValidator(harf_val)
        self.n.setMinimumHeight(55)
        self.n.setStyleSheet("font-size: 16px;")
        
        self.u = QLineEdit()
        self.u.setPlaceholderText("Kullanıcı Adı")
        self.u.setValidator(harf_val)
        self.u.setMinimumHeight(55)
        self.u.setStyleSheet("font-size: 16px;")
        
        self.tel = QLineEdit()
        self.tel.setPlaceholderText("Telefon (11 Hane Örn: 0555...)")
        self.tel.setMaxLength(11)
        self.tel.setValidator(QRegularExpressionValidator(QRegularExpression(r"^[0-9]*$")))
        self.tel.setMinimumHeight(55)
        self.tel.setStyleSheet("font-size: 16px;")
        
        fl.addWidget(self.n)
        fl.addWidget(self.u)
        fl.addWidget(self.tel)
        
        dt_layout = QHBoxLayout()
        lbl_dt = QLabel("<b>Doğum Tarihi:</b>")
        lbl_dt.setStyleSheet("font-size: 16px;")
        dt_layout.addWidget(lbl_dt)
        
        self.dt = QDateEdit()
        self.dt.setCalendarPopup(True)
        self.dt.setDate(QDate(2000,1,1))
        self.dt.setMinimumHeight(55)
        self.dt.setStyleSheet("font-size: 16px;")
        
        takvim = self.dt.calendarWidget()
        takvim.setMinimumSize(350, 250) 
        takvim.setStyleSheet("""
            QCalendarWidget QWidget { background-color: white; }
            QCalendarWidget QToolButton { height: 30px; font-size: 14px; font-weight: bold; }
            QCalendarWidget QAbstractItemView:enabled { font-size: 14px; selection-background-color: #2ecc71; selection-color: white; }
        """)

        dt_layout.addWidget(self.dt)
        fl.addLayout(dt_layout)
        
        self.p = PasswordField("Şifre")
        fl.addWidget(self.p)
        
        fl.addSpacing(15)
        
        btn_kayit = QPushButton("KAYDI TAMAMLA")
        btn_kayit.setStyleSheet(BTN_GREEN)
        btn_kayit.setMinimumHeight(55)
        font = btn_kayit.font()
        font.setPointSize(12)
        btn_kayit.setFont(font)
        btn_kayit.clicked.connect(self.reg)
        fl.addWidget(btn_kayit)
        
        btn_geri = QPushButton("Geri Dön")
        btn_geri.setStyleSheet("QPushButton { color: #7f8c8d; background: transparent; font-weight: bold; font-size: 16px; } QPushButton:hover { color: #34495e; text-decoration: underline; }")
        btn_geri.clicked.connect(self.geriye_git)
        fl.addWidget(btn_geri)
        
        l.addWidget(f)

    def geriye_git(self):
        self.parent.setCurrentIndex(0)

    def reg(self):
        if not self.u.text() or not self.p.input.text() or len(self.tel.text()) != 11: 
            return QMessageBox.warning(self, "Uyarı", "Lütfen tüm bilgileri eksiksiz ve doğru (Telefon 11 hane) giriniz!")
        if kullanici_kaydet(self.u.text(), self.p.input.text(), self.n.text(), self.tel.text(), self.dt.date().toString("dd.MM.yyyy")): 
            QMessageBox.information(self, "Başarılı", "Kayıt işlemi tamamlandı! Şimdi giriş yapabilirsiniz.")
            self.parent.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Hata", "Bu kullanıcı adı sistemde zaten mevcut!")

class AdminPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.seferler_cache = []
        l = QVBoxLayout(self)
        l.setContentsMargins(30, 30, 30, 30)
        l.setSpacing(20)
        
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: white; border-radius: 12px;")
        golge_ekle(top_bar)
        
        h = QHBoxLayout(top_bar)
        h.setContentsMargins(20, 15, 20, 15)
        h.setSpacing(15)
        
        h.addWidget(QLabel("<h2 style='color:#2c3e50; margin:0;'>👨‍✈️ Yönetici Kontrol Paneli</h2>"))
        h.addStretch()
        
        btn_sehir_ekle = QPushButton("🌍 YENİ ŞEHİR EKLE")
        btn_sehir_ekle.setStyleSheet(BTN_PURPLE)
        btn_sehir_ekle.clicked.connect(self.sehir_ekle_ac)
        h.addWidget(btn_sehir_ekle)
        
        btn_ekle = QPushButton("✈️ YENİ SEFER OLUŞTUR")
        btn_ekle.setStyleSheet(BTN_ORANGE)
        btn_ekle.clicked.connect(self.ekle_ac)
        h.addWidget(btn_ekle)
        
        btn_cikis = QPushButton("Çıkış Yap")
        btn_cikis.setStyleSheet(BTN_DARK)
        btn_cikis.clicked.connect(self.cikisa_git)
        h.addWidget(btn_cikis)
        
        l.addWidget(top_bar)
        
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["KALKIŞ ŞEHRİ", "VARIŞ ŞEHRİ", "TARİH", "SAAT", "TABAN FİYAT", "DURUM"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        golge_ekle(self.table)
        l.addWidget(self.table)
        
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(15)
        
        btn_yolcu = QPushButton("📋 SEÇİLİ SEFERİN YOLCU LİSTESİNİ GÖR")
        btn_yolcu.setStyleSheet(BTN_BLUE)
        btn_yolcu.clicked.connect(self.yolcu_gor)
        btn_lay.addWidget(btn_yolcu)
        
        btn_sil = QPushButton("🗑️ SEÇİLİ SEFERİ İPTAL ET / SİL")
        btn_sil.setStyleSheet(BTN_RED)
        btn_sil.clicked.connect(self.sil_islem)
        btn_lay.addWidget(btn_sil)
        
        l.addLayout(btn_lay)

    def cikisa_git(self):
        self.parent.setCurrentIndex(0)

    def yenile(self):
        self.seferler_cache = seferleri_getir()
        self.table.setRowCount(len(self.seferler_cache))
        for i, r in enumerate(self.seferler_cache):
            for j in range(1, 7): 
                val = f"{r[j]:.2f} TL" if j == 5 else str(r[j])
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                if j == 6:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                    if r[j] == 'İptal Edildi': item.setForeground(QColor("#c0392b"))
                    elif r[j] == 'Tamamlandı': item.setForeground(QColor("#27ae60"))
                    else: item.setForeground(QColor("#f39c12"))
                    
                self.table.setItem(i, j-1, item)

    def ekle_ac(self):
        if SeferEklePenceresi(self).exec(): 
            self.yenile()

    def sehir_ekle_ac(self):
        if AdminYeniSehirPenceresi(self).exec():
            self.parent.pass_scr.sehir_filtrelerini_guncelle()

    def yolcu_gor(self):
        row = self.table.currentRow()
        if row >= 0: 
            AdminSeferDetayPenceresi(self.seferler_cache[row], self).exec()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen listeden bir sefer seçin!")

    def sil_islem(self):
        row = self.table.currentRow()
        if row >= 0:
            sefer = self.seferler_cache[row]
            if sefer[6] == 'İptal Edildi':
                return QMessageBox.warning(self, "Uyarı", "Bu sefer zaten iptal edilmiş!")
            if sefer[6] == 'Tamamlandı':
                return QMessageBox.warning(self, "Uyarı", "Tamamlanmış (uçuşu gerçekleşmiş) bir seferi iptal edemezsiniz!")
                
            cevap = QMessageBox.question(self, "İptal Onayı", "Bu seferi iptal edip, bilet alan tüm yolcuların parasını iade etmek istediğinize emin misiniz?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if cevap == QMessageBox.StandardButton.Yes:
                sefer_sil(sefer[0])
                self.yenile()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen iptal edilecek seferi seçin!")

class PassengerPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.tum_seferler = []
        self.gosterilen = []
        
        l = QVBoxLayout(self)
        l.setContentsMargins(30, 30, 30, 30)
        l.setSpacing(20)
        
        top_h_layout = QHBoxLayout()
        top_h_layout.setSpacing(20)
        
        self.profil_karti = QFrame()
        self.profil_karti.setStyleSheet("background-color: white; border-radius: 12px;")
        golge_ekle(self.profil_karti)
        p_lay = QVBoxLayout(self.profil_karti)
        p_lay.setContentsMargins(20, 15, 20, 15)
        p_lay.setSpacing(8)
        
        p_baslik = QLabel("<b style='color:#2980b9; font-size: 16px;'>👤 Yolcu Profili</b>")
        self.lbl_ad = QLabel()
        self.lbl_kadi = QLabel()
        self.lbl_dtarih = QLabel()
        
        p_lay.addWidget(p_baslik)
        p_lay.addWidget(self.lbl_ad)
        p_lay.addWidget(self.lbl_kadi)
        p_lay.addWidget(self.lbl_dtarih)
        p_lay.addStretch()
        
        top_h_layout.addWidget(self.profil_karti, stretch=2)
        
        self.bakiye_karti = QFrame()
        self.bakiye_karti.setStyleSheet("background-color: white; border-radius: 12px;")
        golge_ekle(self.bakiye_karti)
        bak_lay = QVBoxLayout(self.bakiye_karti)
        bak_lay.setContentsMargins(20, 15, 20, 15)
        bak_lay.setSpacing(10)
        bak_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_bakiye = QLabel()
        self.lbl_bakiye.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_para = QPushButton("💰 BAKİYE YÜKLE")
        btn_para.setStyleSheet(BTN_GREEN)
        btn_para.clicked.connect(self.para_yukle_aksiyon)
        
        bak_lay.addWidget(self.lbl_bakiye)
        bak_lay.addWidget(btn_para)
        
        top_h_layout.addWidget(self.bakiye_karti, stretch=2)
        
        islem_karti = QFrame()
        islem_karti.setStyleSheet("background-color: white; border-radius: 12px;")
        golge_ekle(islem_karti)
        islem_lay = QVBoxLayout(islem_karti)
        islem_lay.setContentsMargins(20, 15, 20, 15)
        islem_lay.setSpacing(10)
        islem_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_biletlerim = QPushButton("🎟 BİLETLERİM")
        btn_biletlerim.setStyleSheet(BTN_ORANGE)
        btn_biletlerim.clicked.connect(self.biletlerim_ac)
        
        btn_cikis = QPushButton("Çıkış Yap")
        btn_cikis.setStyleSheet(BTN_DARK)
        btn_cikis.clicked.connect(self.cikisa_git)
        
        islem_lay.addStretch()
        islem_lay.addWidget(btn_biletlerim)
        islem_lay.addWidget(btn_cikis)
        islem_lay.addStretch()
        
        top_h_layout.addWidget(islem_karti, stretch=2)
        
        l.addLayout(top_h_layout)
        
        search_card = QFrame()
        search_card.setStyleSheet("background-color: white; border-radius: 12px;")
        golge_ekle(search_card)
        fl = QHBoxLayout(search_card)
        fl.setContentsMargins(20, 20, 20, 20)
        fl.setSpacing(15)
        
        fl.addWidget(QLabel("<b>🛫 Nereden:</b>"))
        self.cb_k = QComboBox()
        fl.addWidget(self.cb_k)
        
        fl.addWidget(QLabel("<b>🛬 Nereye:</b>"))
        self.cb_v = QComboBox()
        fl.addWidget(self.cb_v)
        
        self.sehir_filtrelerini_guncelle()
        
        btn_ara = QPushButton("🔍 UÇUŞLARI LİSTELE")
        btn_ara.setStyleSheet(BTN_BLUE)
        btn_ara.clicked.connect(self.filtrele)
        fl.addWidget(btn_ara)
        l.addWidget(search_card)
        
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["KALKIŞ", "VARIŞ", "TARİH", "SAAT", "FİYAT"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        golge_ekle(self.table)
        l.addWidget(self.table)
        
        b_lay = QHBoxLayout()
        b_lay.setSpacing(15)
        
        btn_detay = QPushButton("🌍 VARIŞ ŞEHRİ REHBERİNİ İNCELE")
        btn_detay.setStyleSheet(BTN_PURPLE)
        btn_detay.clicked.connect(self.rehber_ac)
        b_lay.addWidget(btn_detay)
        
        btn_al = QPushButton("🎫 SEÇİLİ UÇUŞ İÇİN BİLET AL")
        btn_al.setStyleSheet(BTN_GREEN)
        btn_al.clicked.connect(self.bilet_sureci)
        b_lay.addWidget(btn_al)
        l.addLayout(b_lay)

    def sehir_filtrelerini_guncelle(self):
        guncel_sehirler = sehir_isimlerini_getir()
        mevcut_kalkis = self.cb_k.currentText()
        mevcut_varis = self.cb_v.currentText()
        
        self.cb_k.clear(); self.cb_k.addItem("Tümü"); self.cb_k.addItems(guncel_sehirler)
        self.cb_v.clear(); self.cb_v.addItem("Tümü"); self.cb_v.addItems(guncel_sehirler)
        
        if self.cb_k.findText(mevcut_kalkis) >= 0: self.cb_k.setCurrentText(mevcut_kalkis)
        if self.cb_v.findText(mevcut_varis) >= 0: self.cb_v.setCurrentText(mevcut_varis)

    def cikisa_git(self):
        self.parent.setCurrentIndex(0)

    def update_user(self, user):
        self.lbl_ad.setText(f"<span style='color:#34495e; font-size:14px;'><b>Ad Soyad:</b> {user[3]}</span>")
        self.lbl_kadi.setText(f"<span style='color:#34495e; font-size:14px;'><b>Kullanıcı Adı:</b> @{user[1]}</span>")
        self.lbl_dtarih.setText(f"<span style='color:#34495e; font-size:14px;'><b>Doğum Tarihi:</b> {user[5]}</span>")
        
        self.lbl_bakiye.setText(f"<div style='font-size:14px; color:#7f8c8d; text-align:center;'>Güncel Bakiye</div><div style='font-size: 24px; font-weight: bold; color: #27ae60; text-align:center;'>{user[6]:.2f} TL</div>")
        
        self.tum_seferler = [s for s in seferleri_getir() if s[6] == 'Planlandı']
        self.gosterilen = self.tum_seferler
        self.tablo_doldur()

    def filtrele(self):
        self.gosterilen = [s for s in self.tum_seferler if (self.cb_k.currentText() == "Tümü" or s[1] == self.cb_k.currentText()) and (self.cb_v.currentText() == "Tümü" or s[2] == self.cb_v.currentText())]
        self.tablo_doldur()

    def tablo_doldur(self):
        self.table.setRowCount(len(self.gosterilen))
        for i, r in enumerate(self.gosterilen):
            for j in range(1, 6): 
                item = QTableWidgetItem(str(r[j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j-1, item)

    def para_yukle_aksiyon(self):
        pencere = BakiyeYuklePenceresi(self)
        if pencere.exec():
            tutar = pencere.spin.value()
            bakiye_artir(self.parent.aktif_kullanici[0], tutar)
            self.parent.aktif_kullanici = kullanici_getir_by_id(self.parent.aktif_kullanici[0])
            self.update_user(self.parent.aktif_kullanici)
            QMessageBox.information(self, "Başarılı İşlem", f"{tutar:.2f} TL cüzdanınıza başarıyla yüklendi!")

    def rehber_ac(self):
        row = self.table.currentRow()
        if row >= 0: 
            sehir = self.gosterilen[row][2]
            tarih = self.gosterilen[row][3]
            SehirDetayPenceresi(sehir, tarih, self).exec()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen rehberini görmek istediğiniz uçuşu seçin!")

    def biletlerim_ac(self): 
        BiletlerimPenceresi(self.parent.aktif_kullanici[0], self).exec()
        self.parent.aktif_kullanici = kullanici_getir_by_id(self.parent.aktif_kullanici[0])
        self.update_user(self.parent.aktif_kullanici)

    def bilet_sureci(self):
        row = self.table.currentRow()
        if row < 0: 
            return QMessageBox.warning(self, "Uyarı", "Lütfen bilet almak için listeden bir uçuş seçin!")
            
        sefer = self.gosterilen[row]
        k_id = self.parent.aktif_kullanici[0]
        
        eski_koltuk = donus_bileti_kontrol_et(k_id, sefer[1], sefer[2], sefer[3])
        if eski_koltuk:
            indirimli = sefer[5] * 0.60
            
            user_bday = QDate.fromString(self.parent.aktif_kullanici[5], "dd.MM.yyyy")
            today = QDate.currentDate()
            is_birthday = False
            if user_bday.isValid():
                is_birthday = (user_bday.day() == today.day() and user_bday.month() == today.month())
            
            if is_birthday:
                indirimli *= 0.75
                msg = f"Bu rota için gidiş biletiniz var!\n\n🎂 Hem %40 Dönüş, Hem %25 Doğum Günü İndirimi Uygulandı!\nKoltuk Sabitlendi: Koltuk {eski_koltuk}\nÖdenecek: {indirimli:.2f} TL\n\nOnaylıyor musunuz?"
            else:
                msg = f"Bu rota için gidiş biletiniz var!\n\n%40 Dönüş İndirimi Uygulandı!\nKoltuk Sabitlendi: Koltuk {eski_koltuk}\nÖdenecek: {indirimli:.2f} TL\n\nOnaylıyor musunuz?"
                
            if QMessageBox.question(self, "Dönüş İndirimi!", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.parent.bilet_satin_al_islem(k_id, sefer[0], eski_koltuk, indirimli)
            return
            
        cevap = QMessageBox.question(self, "Koltuk Seçimi", "Özel koltuk seçmek 150 TL ek ücrete tabidir.\n\nKendi koltuğunuzu seçmek istiyor musunuz?\n(Hayır derseniz sistem ücretsiz ve rastgele bir koltuk atayacaktır.)", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if cevap == QMessageBox.StandardButton.Yes:
            self.parent.koltuk_secim_ekranini_ac(sefer)
        else:
            self.parent.rastgele_koltuk_ata(sefer)

class SeatSelectionPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.l = QVBoxLayout(self)
        self.l.setContentsMargins(40, 40, 40, 40)
        
        self.header_card = QFrame()
        self.header_card.setStyleSheet("background-color: white; border-radius: 12px;")
        golge_ekle(self.header_card)
        h_layout = QVBoxLayout(self.header_card)
        h_layout.setContentsMargins(20, 20, 20, 20)
        
        self.header = QLabel("Koltuk Seç")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(self.header)
        self.l.addWidget(self.header_card)
        
        self.l.addSpacing(20)
        
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.l.addLayout(self.grid)
        
        self.l.addStretch()
        
        btn_geri = QPushButton("Vazgeç ve Geri Dön")
        btn_geri.setStyleSheet(BTN_DARK)
        btn_geri.clicked.connect(self.geriye_git)
        self.l.addWidget(btn_geri)

    def geriye_git(self):
        self.parent.setCurrentIndex(3)

    def ekran_hazirla(self, sefer_data):
        self.sefer_id = sefer_data[0]
        self.fiyat = sefer_data[5] + 150 
        
        varis_rehber = sehir_detay_getir(sefer_data[2])
        iklim_tipi = varis_rehber.get("iklim", "Ilıman")
        
        guncel_hava = dinamik_hava_durumu_getir(sefer_data[2], sefer_data[3], iklim_tipi)
        
        user_bday = QDate.fromString(self.parent.aktif_kullanici[5], "dd.MM.yyyy")
        today = QDate.currentDate()
        is_birthday = False
        if user_bday.isValid():
            is_birthday = (user_bday.day() == today.day() and user_bday.month() == today.month())
        
        if is_birthday:
            self.fiyat *= 0.75
            self.header.setText(f"🎂 Doğum Günü İndirimi! Ödenecek: {self.fiyat:.2f} TL\nVarış: {sefer_data[2]} | Tahmini Hava: {guncel_hava}")
            self.header.setStyleSheet("font-size: 18px; font-weight: bold; color: #d35400;")
        else: 
            self.header.setText(f"Sefer Fiyatı (+150 TL Koltuk Seçim): {self.fiyat:.2f} TL\nVarış: {sefer_data[2]} | Tahmini Hava: {guncel_hava}")
            self.header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        dolu = dolu_koltuklari_getir(self.sefer_id)
        
        for i in reversed(range(self.grid.count())): 
            item = self.grid.takeAt(i)
            if item.widget(): 
                item.widget().deleteLater()
            
        for n in range(1, 41):
            btn = QPushButton(str(n))
            btn.setFixedSize(50, 50)
            btn.setStyleSheet("font-size: 16px; font-weight: bold;")
            golge_ekle(btn)
            
            if n in dolu: 
                btn.setStyleSheet(btn.styleSheet() + "background-color: #e74c3c; color: white; border-radius: 10px;")
                btn.setEnabled(False)
            else:
                btn.setStyleSheet(btn.styleSheet() + "background-color: #2ecc71; color: white; border-radius: 10px;")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda ch, kno=n: self.onay(kno))
            sutun = (n-1)%4
            self.grid.addWidget(btn, (n-1)//4, sutun if sutun < 2 else sutun + 1)
        self.grid.setColumnMinimumWidth(2, 70)

    def onay(self, kno):
        cevap = QMessageBox.question(self, "Bilet Al", f"{kno} numaralı koltuğu {self.fiyat:.2f} TL karşılığında onaylıyor musunuz?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if cevap == QMessageBox.StandardButton.Yes:
            self.parent.bilet_satin_al_islem(self.parent.aktif_kullanici[0], self.sefer_id, kno, self.fiyat)

# --- 4. ANA PENCERE YÖNETİCİSİ ---
class SkyBoundApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        veritabani_hazirla()
        self.aktif_kullanici = None
        
        self.login_scr = LoginScreen(self)
        self.reg_scr = RegisterScreen(self)
        self.admin_scr = AdminPanel(self)
        self.pass_scr = PassengerPanel(self)
        self.seat_scr = SeatSelectionPanel(self)
        
        self.addWidget(self.login_scr)
        self.addWidget(self.reg_scr)
        self.addWidget(self.admin_scr)
        self.addWidget(self.pass_scr)
        self.addWidget(self.seat_scr)
        
        self.setMinimumSize(1100, 800)
        self.setWindowTitle("✈️ SkyBound Premium - Havayolu Biletleme Sistemi")
        self.setStyleSheet(GLOBAL_STYLE)

    def login_basarili(self, user):
        self.aktif_kullanici = user
        if user[1] == "admin": 
            self.admin_scr.yenile()
            self.setCurrentIndex(2)
        else: 
            self.pass_scr.update_user(user)
            self.setCurrentIndex(3)

    def koltuk_secim_ekranini_ac(self, data):
        self.seat_scr.ekran_hazirla(data)
        self.setCurrentIndex(4)

    def bilet_satin_al_islem(self, kid, sid, kno, fiyat):
        ok, msg = bilet_satin_al(kid, sid, kno, fiyat)
        if ok:
            QMessageBox.information(self, "Bilet Onaylandı", f"🎉 Biletiniz başarıyla tanımlandı!\n\nKoltuk No: {kno}\nÖdenen Tutar: {fiyat:.2f} TL")
            self.aktif_kullanici = kullanici_getir_by_id(kid)
            self.pass_scr.update_user(self.aktif_kullanici)
            self.setCurrentIndex(3)
        else: 
            QMessageBox.warning(self, "Hata Oluştu", msg)

    def rastgele_koltuk_ata(self, sefer_data):
        sefer_id, base_fiyat = sefer_data[0], sefer_data[5]
        dolu = dolu_koltuklari_getir(sefer_id)
        bos = [i for i in range(1, 41) if i not in dolu]
        
        if not bos: 
            return QMessageBox.warning(self, "Kapasite Dolu", "Maalesef bu uçakta boş yer kalmadı!")
        
        atanan = random.choice(bos)
        
        user_bday = QDate.fromString(self.aktif_kullanici[5], "dd.MM.yyyy")
        today = QDate.currentDate()
        is_birthday = False
        if user_bday.isValid():
            is_birthday = (user_bday.day() == today.day() and user_bday.month() == today.month())
        
        fiyat = base_fiyat * 0.75 if is_birthday else base_fiyat
        
        ok, msg = bilet_satin_al(self.aktif_kullanici[0], sefer_id, atanan, fiyat)
        if ok:
            if fiyat < base_fiyat:
                QMessageBox.information(self, "Doğum Günü Sürprizi", f"🎂 Doğum Gününüz Kutlu Olsun!\n\nSistem size ücretsiz olarak Koltuk {atanan} atadı.\n%25 İndirimli Ödenen Tutar: {fiyat:.2f} TL")
            else:
                QMessageBox.information(self, "Bilet Onaylandı", f"Sistem size ücretsiz olarak Koltuk {atanan} atadı.\n\nÖdenen Tutar: {fiyat:.2f} TL")
                
            self.aktif_kullanici = kullanici_getir_by_id(self.aktif_kullanici[0])
            self.pass_scr.update_user(self.aktif_kullanici)
        else: 
            QMessageBox.warning(self, "Hata Oluştu", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    try:
        ex = SkyBoundApp()
        ex.show()
        sys.exit(app.exec())
    except Exception as e:
        err_msg = traceback.format_exc()
        QMessageBox.critical(None, "Kritik Sistem Hatası", f"Program başlatılırken veya çalışırken bir hata ile karşılaştı!\nLütfen şu hatayı kontrol edin:\n\n{err_msg}")
        sys.exit(1)