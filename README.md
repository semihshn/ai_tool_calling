# Proje Kurulum ve Çalıştırma Rehberi

Bu projede iki Python scripti bulunmaktadır: `function_calling.py` ve `gemini_cli.py`. Her ikisi de komut satırından çalıştırılabilir ve API anahtarları gerektirir.

Aşağıdaki adımları takip ederek projeyi kolayca çalıştırabilirsiniz.

---

## 1. Python Kurulumu

Öncelikle bilgisayarınızda **Python 3.8 veya üzeri** kurulu olmalıdır. Kontrol etmek için terminale şunu yazın:

```sh
python3 --version
```

Eğer Python yüklü değilse, [python.org](https://www.python.org/downloads/) adresinden indirip kurabilirsiniz.

---

## 2. Sanal Ortam (Önerilir)

Projeyi izole bir ortamda çalıştırmak için sanal ortam oluşturun:

```sh
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# veya
.venv\Scripts\activate   # Windows
```

---

## 3. Bağımlılıkların Kurulumu

Gerekli kütüphaneleri yüklemek için:

```sh
pip install -r requirements.txt
```

---

## 4. .env Dosyasını Oluşturun

API anahtarlarınızı saklamak için proje kök dizininde bir `.env` dosyası oluşturun. Örnek içerik:

```
GEMINI_API_KEY="buraya-gemini-api-key"
WEATHER_API_KEY="buraya-weather-api-key"
OPENAI_API_KEY="buraya-openai-api-key"
```

Gerçek anahtarlarınızı ilgili yerlere yazın. Eğer anahtarlarınız yoksa, ilgili servislerden ücretsiz anahtar alabilirsiniz.

---

## 5. Scriptleri Çalıştırma

### Gemini CLI

```sh
python gemini_cli.py
```

### OpenAI Function Calling CLI

```sh
python function_calling.py
```

Her iki script de komut satırında çalışır ve sizden giriş bekler.

---

## Sık Karşılaşılan Sorunlar

- **ModuleNotFoundError**: Bağımlılıkları yüklediğinizden emin olun (`pip install -r requirements.txt`).
- **API Key Hatası**: `.env` dosyanızda anahtarların doğru yazıldığından ve dosyanın proje kökünde olduğundan emin olun.
- **Python Sürümü Hatası**: Python 3.8 veya üzeri kullandığınızdan emin olun.

---

## Yardım veya Katkı
Sorularınız için issue açabilir veya katkıda bulunmak için pull request gönderebilirsiniz. 