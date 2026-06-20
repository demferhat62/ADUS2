import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import json
import os

# --- AYARLAR ---
GROQ_API_KEY = "buraya groq api key yazılacak"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

MEYVELER = {
    "Kayısı": -2.0, "Elma": -3.0, "Kiraz": -2.5, "Ceviz": -1.0,
    "Şeftali": -2.5, "Erik": -2.0, "Armut": -2.5, "Badem": -1.5,
    "Üzüm": -1.0, "Fındık": -2.0, "Limon": 0.0, "Portakal": -1.0
}

# --- RENK PALETİ (YEŞİL & KAHVERENGİ TEMA) ---
BG_COLOR = "#EFEBE3"        
CARD_BG = "#FFFFFF"         
PRIMARY_COLOR = "#4C7236"   
ACCENT_COLOR = "#4E3629"    
DANGER_COLOR = "#A03022"    
FRAME_BORDER = "#D6CFC4"    

DOSYA_BAHCE = "bahceler.json"

class ADUSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ADUS - Zirai Uyarı Sistemi")
        self.root.geometry("450x800")
        self.root.configure(bg=BG_COLOR)
        
        self.sohbet_gecmisi = [{"role": "system", "content": "Sen bir ziraat uzmanısın."}]
        self.bahceleri_yukle()
        
        self.stil_ayarla()
        self.arayuz_insasi()
        
        self.bahce_secildi() # İlk bahçeyi yükle
        self.root.after(1000, self.hava_durumu_al)

    # --- VERİ YÖNETİMİ ---
    def bahceleri_yukle(self):
        if os.path.exists(DOSYA_BAHCE):
            with open(DOSYA_BAHCE, "r", encoding="utf-8") as f:
                self.bahceler = json.load(f)
        else:
            # Varsayılan bahçe (Koordinatlı)
            self.bahceler = {"Merkez Bahçesi": {"meyve": "Kayısı", "alan": 350, "enlem": "38.35", "boylam": "38.31"}}
            self.bahceleri_kaydet()

    def bahceleri_kaydet(self):
        with open(DOSYA_BAHCE, "w", encoding="utf-8") as f:
            json.dump(self.bahceler, f, ensure_ascii=False, indent=4)

    # --- ARAYÜZ ---
    def stil_ayarla(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=BG_COLOR)
        style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=[15, 5], background=FRAME_BORDER, foreground=ACCENT_COLOR)
        style.map("TNotebook.Tab", background=[("selected", CARD_BG)], foreground=[("selected", PRIMARY_COLOR)])
        style.configure("TCombobox", font=("Arial", 11), padding=5)

    def arayuz_insasi(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === GÖSTERGE PANELİ ===
        self.tab_panel = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_panel, text="Gösterge Paneli")
        
        tk.Label(self.tab_panel, text="ADUS", font=("Arial", 22, "bold"), bg=BG_COLOR, fg=PRIMARY_COLOR).pack(pady=(15, 0))
        
        # Dinamik Konum Etiketi
        self.lbl_konum = tk.Label(self.tab_panel, text="Konum: --", font=("Arial", 12), bg=BG_COLOR, fg=ACCENT_COLOR)
        self.lbl_konum.pack(pady=(0, 15))
        
        # --- BAHÇE KARTI ---
        f_bahce = tk.Frame(self.tab_panel, bg=CARD_BG, highlightbackground=FRAME_BORDER, highlightthickness=1)
        f_bahce.pack(fill="x", padx=15, pady=5)
        
        tk.Label(f_bahce, text="Aktif Bahçe:", font=("Arial", 10, "bold"), bg=CARD_BG, fg=ACCENT_COLOR).pack(pady=(10, 0))
        
        self.cb_bahce = ttk.Combobox(f_bahce, values=list(self.bahceler.keys()), state="readonly", width=25)
        if self.bahceler:
            self.cb_bahce.current(0)
        self.cb_bahce.pack(pady=(5, 5))
        self.cb_bahce.bind("<<ComboboxSelected>>", self.bahce_secildi)
        
        self.lbl_bahce_detay = tk.Label(f_bahce, text="--", font=("Arial", 10), bg=CARD_BG, fg=ACCENT_COLOR)
        self.lbl_bahce_detay.pack(pady=(0, 5))
        
        tk.Button(f_bahce, text="+ Yeni Bahçe Ekle", command=self.yeni_bahce_ekran, bg=PRIMARY_COLOR, fg="white", font=("Arial", 9, "bold"), relief="flat", padx=10, pady=4).pack(pady=(0, 10))

        # --- ANLIK DURUM KARTI ---
        self.f_anlik = tk.Frame(self.tab_panel, bg=CARD_BG, highlightbackground=FRAME_BORDER, highlightthickness=1)
        self.f_anlik.pack(fill="x", padx=15, pady=15)
        
        tk.Label(self.f_anlik, text="Anlık Sıcaklık", font=("Arial", 10, "bold"), bg=CARD_BG, fg=ACCENT_COLOR).pack(pady=(15, 0))
        self.lbl_sicaklik = tk.Label(self.f_anlik, text="-- °C", font=("Arial", 36, "bold"), bg=CARD_BG, fg=ACCENT_COLOR)
        self.lbl_sicaklik.pack()
        self.lbl_durum = tk.Label(self.f_anlik, text="Hesaplanıyor...", font=("Arial", 12, "bold"), bg=CARD_BG, fg=ACCENT_COLOR)
        self.lbl_durum.pack(pady=(0, 15))
        
        # --- 48 SAATLİK TAHMİN KARTI ---
        self.f_uyari = tk.Frame(self.tab_panel, bg=CARD_BG, highlightbackground=FRAME_BORDER, highlightthickness=1)
        self.f_uyari.pack(fill="x", padx=15, pady=5)
        
        tk.Label(self.f_uyari, text="48 Saatlik Tahmin", font=("Arial", 10, "bold"), bg=CARD_BG, fg=ACCENT_COLOR).pack(pady=(10, 5))
        self.lbl_uyari = tk.Label(self.f_uyari, text="Hesaplanıyor...", font=("Arial", 11), bg=CARD_BG, fg=ACCENT_COLOR)
        self.lbl_uyari.pack(pady=(0, 15))
        
        tk.Button(self.tab_panel, text="Zirai Asistan", command=lambda: self.notebook.select(1), bg=PRIMARY_COLOR, fg="white", font=("Arial", 11, "bold"), relief="flat", padx=15, pady=8).pack(pady=20)

        # === ZİRAİ ASİSTAN ===
        self.tab_chat = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_chat, text="Zirai Asistan")
        
        self.txt_chat = tk.Text(self.tab_chat, state="disabled", font=("Arial", 11), bg=CARD_BG, fg=ACCENT_COLOR, wrap="word", bd=0, highlightthickness=1, highlightbackground=FRAME_BORDER)
        self.txt_chat.pack(fill="both", expand=True, padx=10, pady=10)
        
        f_mesaj = tk.Frame(self.tab_chat, bg=BG_COLOR)
        f_mesaj.pack(fill="x", padx=10, pady=(0, 10))
        
        self.ent_mesaj = tk.Entry(f_mesaj, font=("Arial", 12), relief="flat", highlightthickness=1, highlightbackground=FRAME_BORDER)
        self.ent_mesaj.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))
        
        tk.Button(f_mesaj, text="Gönder", command=self.mesaj_gonder, bg=PRIMARY_COLOR, fg="white", font=("Arial", 11, "bold"), relief="flat", padx=15).pack(side="right", fill="y")

    # --- İŞLEVLER ---
    def bahce_secildi(self, event=None):
        secilen = self.cb_bahce.get()
        if secilen in self.bahceler:
            bilgi = self.bahceler[secilen]
            # Eski kayıtlarda koordinat yoksa varsayılan Malatya koordinatları kullanılır
            enlem = bilgi.get("enlem", "38.35")
            boylam = bilgi.get("boylam", "38.31")
            
            self.lbl_konum.config(text=f"Konum: {enlem}, {boylam}")
            self.lbl_bahce_detay.config(text=f"Tür: {bilgi['meyve']}  |  Alan: {bilgi['alan']} Dönüm")
            self.hava_durumu_al()

    def yeni_bahce_ekran(self):
        pencere = tk.Toplevel(self.root)
        pencere.title("Yeni Bahçe Ekle")
        pencere.geometry("320x450") # Pencere boyutu büyütüldü
        pencere.configure(bg=BG_COLOR)
        pencere.grab_set() 
        
        # Grid kullanmak için yardımcı bir frame
        f_form = tk.Frame(pencere, bg=BG_COLOR)
        f_form.pack(pady=20, padx=20, fill="both", expand=True)

        tk.Label(f_form, text="Bahçe Adı:", font=("Arial", 10, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w", pady=(0, 2))
        ent_isim = tk.Entry(f_form, font=("Arial", 11))
        ent_isim.pack(fill="x", pady=(0, 10))
        
        tk.Label(f_form, text="Meyve Türü:", font=("Arial", 10, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w", pady=(0, 2))
        meyve_listesi = sorted(list(MEYVELER.keys()))
        cb_yeni_meyve = ttk.Combobox(f_form, values=meyve_listesi, state="readonly", font=("Arial", 11))
        cb_yeni_meyve.current(0)
        cb_yeni_meyve.pack(fill="x", pady=(0, 10))
        
        tk.Label(f_form, text="Alan (Dönüm):", font=("Arial", 10, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w", pady=(0, 2))
        ent_alan = tk.Entry(f_form, font=("Arial", 11))
        ent_alan.pack(fill="x", pady=(0, 10))
        
        tk.Label(f_form, text="Enlem (Örn: 38.35):", font=("Arial", 10, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w", pady=(0, 2))
        ent_enlem = tk.Entry(f_form, font=("Arial", 11))
        ent_enlem.pack(fill="x", pady=(0, 10))
        
        tk.Label(f_form, text="Boylam (Örn: 38.31):", font=("Arial", 10, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w", pady=(0, 2))
        ent_boylam = tk.Entry(f_form, font=("Arial", 11))
        ent_boylam.pack(fill="x", pady=(0, 20))
        
        def kaydet():
            isim = ent_isim.get().strip()
            alan = ent_alan.get().strip()
            meyve = cb_yeni_meyve.get()
            enlem = ent_enlem.get().strip()
            boylam = ent_boylam.get().strip()
            
            if not isim or not alan or not enlem or not boylam:
                messagebox.showwarning("Eksik Bilgi", "Lütfen tüm alanları doldurun.", parent=pencere)
                return
            
            self.bahceler[isim] = {"meyve": meyve, "alan": alan, "enlem": enlem, "boylam": boylam}
            self.bahceleri_kaydet()
            
            self.cb_bahce['values'] = list(self.bahceler.keys())
            self.cb_bahce.set(isim)
            self.bahce_secildi()
            
            pencere.destroy()
            
        tk.Button(f_form, text="Kaydet", command=kaydet, bg=PRIMARY_COLOR, fg="white", font=("Arial", 10, "bold"), relief="flat", pady=5).pack(fill="x")

    def hava_durumu_al(self):
        if not self.cb_bahce.get(): return
        self.lbl_durum.config(text="Güncelleniyor...", fg=ACCENT_COLOR)
        self.lbl_uyari.config(text="Analiz ediliyor...", fg=ACCENT_COLOR)
        threading.Thread(target=self._arka_plan_hava, daemon=True).start()

    def _arka_plan_hava(self):
        try:
            secilen_bahce = self.cb_bahce.get()
            bilgi = self.bahceler[secilen_bahce]
            
            meyve = bilgi["meyve"]
            esik = MEYVELER[meyve]
            enlem = bilgi.get("enlem", "38.35")
            boylam = bilgi.get("boylam", "38.31")
            
            # Dinamik Koordinatlarla API İsteği
            url = f"https://api.open-meteo.com/v1/forecast?latitude={enlem}&longitude={boylam}&current_weather=true&hourly=temperature_2m"
            yanit = requests.get(url, timeout=5).json()
            
            sicaklik = yanit['current_weather']['temperature']
            
            anlik_renk = DANGER_COLOR if sicaklik <= esik else PRIMARY_COLOR
            anlik_durum = "Anlık Risk: Mevcut" if sicaklik <= esik else "Anlık Risk: Yok"
            
            # --- 48 SAATLİK ANALİZ ---
            saatlik_zamanlar = yanit['hourly']['time']
            saatlik_sicakliklar = yanit['hourly']['temperature_2m']
            
            anlik_zaman_str = yanit['current_weather']['time']
            try:
                baslangic_index = saatlik_zamanlar.index(anlik_zaman_str)
            except ValueError:
                baslangic_index = 0
                
            don_tehlikesi = False
            riskli_saat_sonra = 0
            tahmini_dusuk_sicaklik = 0.0
            
            for i in range(1, 49): 
                kontrol_index = baslangic_index + i
                if kontrol_index < len(saatlik_sicakliklar):
                    tahmin_derece = saatlik_sicakliklar[kontrol_index]
                    if tahmin_derece <= esik:
                        don_tehlikesi = True
                        riskli_saat_sonra = i
                        tahmini_dusuk_sicaklik = tahmin_derece
                        break
            
            if don_tehlikesi:
                uyari_metni = f"Uyarı: {riskli_saat_sonra} saat sonra don riski ({tahmini_dusuk_sicaklik}°C)"
                uyari_fg = DANGER_COLOR
            else:
                uyari_metni = f"48 saat içinde {meyve} için risk yok."
                uyari_fg = PRIMARY_COLOR
            
            self.root.after(0, lambda: self.lbl_sicaklik.config(text=f"{sicaklik}°C", fg=anlik_renk))
            self.root.after(0, lambda: self.lbl_durum.config(text=anlik_durum, fg=anlik_renk))
            self.root.after(0, lambda: self.lbl_uyari.config(text=uyari_metni, fg=uyari_fg))
            
        except Exception:
            self.root.after(0, lambda: self.lbl_durum.config(text="Bağlantı Hatası", fg=DANGER_COLOR))
            self.root.after(0, lambda: self.lbl_uyari.config(text="Veri çekilemedi. Koordinatları kontrol edin.", fg=DANGER_COLOR))

    # --- ASİSTAN İLETİŞİMİ ---
    def mesaj_gonder(self):
        mesaj = self.ent_mesaj.get()
        if not mesaj: return
        self.ent_mesaj.delete(0, tk.END)
        self.chat_yaz("Siz", mesaj, is_user=True)
        self.sohbet_gecmisi.append({"role": "user", "content": mesaj})
        threading.Thread(target=self.groq_istek, daemon=True).start()

    def chat_yaz(self, isim, mesaj, is_user=False):
        self.txt_chat.config(state="normal")
        
        tag_name = "user" if is_user else "bot"
        self.txt_chat.tag_config("user", foreground=ACCENT_COLOR, font=("Arial", 11, "bold"))
        self.txt_chat.tag_config("bot", foreground=PRIMARY_COLOR, font=("Arial", 11, "bold"))
        self.txt_chat.tag_config("text", foreground="#000000", font=("Arial", 11))
        
        self.txt_chat.insert(tk.END, f"{isim}:\n", tag_name)
        self.txt_chat.insert(tk.END, f"{mesaj}\n\n", "text")
        
        self.txt_chat.see(tk.END)
        self.txt_chat.config(state="disabled")

    def groq_istek(self):
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": self.sohbet_gecmisi}
        try:
            cevap = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
            if cevap.status_code == 200:
                yanit = cevap.json()['choices'][0]['message']['content']
                self.sohbet_gecmisi.append({"role": "assistant", "content": yanit})
                self.root.after(0, self.chat_yaz, "Asistan", yanit, False)
            else:
                self.root.after(0, self.chat_yaz, "Sistem", "Sunucu hatası.", False)
        except:
            self.root.after(0, self.chat_yaz, "Sistem", "İnternet bağlantısı kurulamadı.", False)

if __name__ == "__main__":
    root = tk.Tk()
    app = ADUSApp(root)
    root.mainloop()