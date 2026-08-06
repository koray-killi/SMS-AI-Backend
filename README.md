# 📱 SMS AI Backend

> **TR:** Apple Kestirmeler ile entegre çalışan, gelen SMS mesajlarını yapay zeka ile yanıtlayan Vercel tabanlı bir backend sunucusu.
>
> **EN:** A Vercel-based backend server that integrates with Apple Shortcuts to process incoming SMS messages and respond using AI.

---

## 🇹🇷 Türkçe

### Proje Hakkında

Bu proje, iPhone'da çalışan bir **Apple Kestirmesi (Shortcut)** tarafından tetiklenir. Kullanıcıya SMS gelen anda Kestirme devreye girer, mesajı bu backend sunucusuna iletir ve sunucu **DeepSeek AI** kullanarak kısa, SMS'e uygun bir yanıt üretir. Yanıt tekrar Kestirme'ye döner ve otomatik SMS olarak gönderilebilir.

### Nasıl Çalışır?

```
Gelen SMS
    │
    ▼
Apple Kestirmesi (Shortcut)
    │  JSON body: { "mesaj": "..." }
    ▼
POST /api/webhook  ──►  DeepSeek AI
    │
    ▼
JSON yanıt: { "reply": "..." }
    │
    ▼
Apple Kestirmesi otomatik yanıt gönderir
```

### Özellikler

- 🤖 **DeepSeek AI** entegrasyonu (OpenAI SDK uyumlu)
- 📲 **Apple Kestirmeler** ile tam uyumluluk
- ⚡ **Vercel** serverless deployment
- 🔐 `.env` ile güvenli API key yönetimi
- 📏 SMS boyutuna uygun kısa yanıtlar (maks. ~150 karakter)

### Kurulum

#### 1. Projeyi Klonla

```bash
git clone <repo-url>
cd vercel-sms-ai
```

#### 2. Sanal Ortam ve Bağımlılıklar

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Ortam Değişkenlerini Ayarla

`.env.example` dosyasını kopyalayarak `.env` oluştur:

```bash
cp .env.example .env
```

`.env` dosyasını düzenle:

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

> DeepSeek API anahtarını [platform.deepseek.com](https://platform.deepseek.com) adresinden edinebilirsin.

#### 4. Yerel Sunucuyu Başlat

```bash
python api/index.py
```

Sunucu `http://localhost:5000` adresinde çalışmaya başlar.

### API Kullanımı

#### `POST /api/webhook`

**İstek Gövdesi (JSON):**

```json
{
  "mesaj": "Bugün nasılsın?"
}
```

**Başarılı Yanıt (200):**

```json
{
  "reply": "İyiyim, teşekkürler! Sen nasılsın?"
}
```

**Hata Yanıtı (400):**

```json
{
  "reply": "Mesaj alınamadı."
}
```

### Apple Kestirmesi Kurulumu

1. iPhone'da **Kestirmeler** uygulamasını aç
2. **Otomasyon** sekmesine git ve yeni otomasyon oluştur
3. **"Mesaj Aldığımda"** tetikleyicisini seç
4. **"URL İçeriğini Al"** eylemini ekle:
   - URL: `https://<vercel-domain>/api/webhook`
   - Yöntem: `POST`
   - Gövde: `JSON` → `mesaj: [Gelen SMS metni]`
5. Dönen `reply` değerini **"Mesaj Gönder"** eylemine bağla

### Vercel'e Deploy

```bash
npm i -g vercel
vercel
```

Vercel Dashboard'da **Settings → Environment Variables** bölümüne `DEEPSEEK_API_KEY` değerini ekle.

---

## 🇬🇧 English

### About the Project

This project is triggered by an **Apple Shortcut** running on iPhone. When an SMS arrives, the Shortcut fires, forwards the message to this backend server, and the server generates a short, SMS-friendly reply using **DeepSeek AI**. The reply is sent back to the Shortcut, which can then automatically respond to the SMS.

### How It Works

```
Incoming SMS
    │
    ▼
Apple Shortcuts
    │  JSON body: { "mesaj": "..." }
    ▼
POST /api/webhook  ──►  DeepSeek AI
    │
    ▼
JSON response: { "reply": "..." }
    │
    ▼
Apple Shortcuts sends automated reply
```

### Features

- 🤖 **DeepSeek AI** integration (OpenAI SDK compatible)
- 📲 Full **Apple Shortcuts** compatibility
- ⚡ **Vercel** serverless deployment
- 🔐 Secure API key management via `.env`
- 📏 SMS-length optimized replies (max ~150 characters)

### Setup

#### 1. Clone the Repository

```bash
git clone <repo-url>
cd vercel-sms-ai
```

#### 2. Virtual Environment & Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Configure Environment Variables

Copy the example env file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

> Get your DeepSeek API key from [platform.deepseek.com](https://platform.deepseek.com).

#### 4. Run the Local Server

```bash
python api/index.py
```

The server starts at `http://localhost:5000`.

### API Reference

#### `POST /api/webhook`

**Request Body (JSON):**

```json
{
  "mesaj": "How are you today?"
}
```

**Success Response (200):**

```json
{
  "reply": "I'm doing great, thanks for asking!"
}
```

**Error Response (400):**

```json
{
  "reply": "Mesaj alınamadı."
}
```

### Apple Shortcuts Setup

1. Open the **Shortcuts** app on iPhone
2. Go to the **Automation** tab and create a new automation
3. Choose **"When I receive a message"** as the trigger
4. Add a **"Get Contents of URL"** action:
   - URL: `https://<your-vercel-domain>/api/webhook`
   - Method: `POST`
   - Request Body: `JSON` → `mesaj: [Shortcut Input / SMS text]`
5. Connect the returned `reply` value to a **"Send Message"** action

### Deploy to Vercel

```bash
npm i -g vercel
vercel
```

In the Vercel Dashboard, add `DEEPSEEK_API_KEY` under **Settings → Environment Variables**.

---

## 📁 Project Structure

```
vercel-sms-ai/
├── api/
│   └── index.py        # Flask app & DeepSeek API handler
├── .env                # Local secrets (git ignored)
├── .env.example        # Template for environment variables
├── .gitignore
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel deployment config
└── README.md
```

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| Python + Flask | Web server |
| DeepSeek API | AI language model |
| OpenAI SDK | API client (DeepSeek compatible) |
| python-dotenv | Local environment variable loading |
| Vercel | Serverless hosting |
| Apple Shortcuts | SMS automation trigger |

## 📄 License

MIT
