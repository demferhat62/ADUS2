# 🌱 ADUS - Akıllı Don Uyarı Sistemi

ADUS, çiftçiler ve tarım uzmanları için geliştirilmiş yapay zeka destekli bir erken uyarı sistemidir. Seçilen meyve türünün donma eşiğine ve bahçenin özel koordinatlarına göre 48 saatlik hava durumu verilerini analiz ederek potansiyel don risklerini önceden bildirir.

## ✨ Özellikler

* **Koordinat Tabanlı Analiz:** Her bahçe için özel enlem ve boylam girerek noktasal hava durumu tahmini alma.
* **48 Saatlik Erken Uyarı:** Open-Meteo API entegrasyonu ile önümüzdeki 48 saati tarayarak ilk riskli anı saat ve derece olarak tespit etme.
* **Çoklu Bahçe Yönetimi:** Birden fazla bahçeyi meyve türü, dönüm bilgisi ve koordinatlarıyla birlikte sisteme ekleme ve `bahceler.json` dosyasına kalıcı olarak kaydetme.
* **Yapay Zeka Destekli Zirai Asistan:** Llama 3 (Groq API) entegrasyonu sayesinde ziraat uzmanı profilindeki yapay zekaya anında tarımsal sorular sorabilme.
* **Modern Arayüz (GUI):** Python Tkinter ile geliştirilmiş, doğa temalı (yeşil ve toprak tonları) kullanıcı dostu arayüz.

## 🛠️ Kullanılan Teknolojiler

* **Dil:** Python
* **Arayüz:** Tkinter & ttk
* **Hava Durumu Verisi:** Open-Meteo API
* **Yapay Zeka:** Groq API (Llama-3.3-70b-versatile)

## 🚀 Kurulum ve Kullanım

1. Projeyi bilgisayarınıza indirin veya klonlayın.
2. Gerekli kütüphaneyi kurun:
   `pip install requests`
3. Proje içindeki `GROQ_API_KEY` değişkenine kendi Groq API anahtarınızı girin. *(Güvenlik için API anahtarınızı herkese açık paylaşmayın!)*
4. Uygulamayı başlatın:
   `python dosya_adiniz.py`

## ⚠️ Önemli Not
Bu yazılım bir karar destek sistemidir. Meteorolojik veriler anlık değişiklik gösterebileceğinden, don riskine karşı sahada ek önlemler alınması tavsiye edilir.