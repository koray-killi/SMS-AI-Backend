# 📱 SMS AI Backend

> **TR:** Apple Kestirmeler ile entegre çalışan, gelen SMS mesajlarını yapay zeka ile yanıtlayan Vercel tabanlı bir backend sunucusu.
>
> **EN:** A Vercel-based backend server that integrates with Apple Shortcuts to process incoming SMS messages and respond using AI.

---

## 🇹🇷 Türkçe

### Proje Hakkında

Bu proje, iPhone'da çalışan bir **Apple Kestirmesi (Shortcut)** tarafından tetiklenir. Kullanıcıya SMS gelen anda Kestirme devreye girer, mesajı bu backend sunucusuna iletir ve sunucu **OpenAI GPT-5.6 Luna** kullanarak kısa, SMS'e uygun bir yanıt üretir. Güncel bilgi gereken sorularda OpenAI'ın yerleşik **web araması** otomatik devreye girer. Yanıt tekrar Kestirme'ye döner ve otomatik SMS olarak gönderilebilir.

### Nasıl Çalışır?

```
Gelen SMS
    │
    ▼
Apple Kestirmesi (Shortcut)
    │  JSON body: { "mesaj": "..." }
    ▼
POST /api/webhook
    │
    ▼
OpenAI Responses API (GPT-5.6 Luna)
    ├─ Gerekirse: web_search_preview (yerleşik)
    │
    ▼
JSON yanıt: { "reply": "..." }  (maks. 152 karakter)
    │
    ▼
Apple Kestirmesi otomatik yanıt gönderir
```

### Özellikler

- 🤖 **OpenAI GPT-5.6 Luna** — hızlı ve ucuz ($0.20/1M input)
- 🔍 **Yerleşik Web Araması** — güncel bilgi için otomatik arama (Tavily'ye gerek yok)
- 📲 **Apple Kestirmeler** ile tam uyumluluk
- ⚡ **Vercel** serverless deployment
- 🔐 Tek API key ile güvenli yönetim
- 📏 Türkçe SMS boyutuna uygun yanıtlar (maks. 152 karakter — UCS-2 encoding)

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

```bash
cp .env.example .env
```

`.env` dosyasını düzenle:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

> OpenAI API anahtarını [platform.openai.com](https://platform.openai.com) adresinden edinebilirsin.

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
  "mesaj": "Bugün hava nasıl İstanbul'da?"
}
```

**Başarılı Yanıt (200):**

```json
{
  "reply": "İstanbul'da bugün 28°C, güneşli ama akşam bulut gelecek. ☀️"
}
```

**Hata Yanıtları:**

| Kod | Açıklama |
|-----|----------|
| 400 | Mesaj gövdesi boş |
| 429 | Rate limit aşıldı |
| 502 | Bağlantı hatası |
| 503 | AI servisi meşgul |
| 504 | Zaman aşımı |
| 500 | Genel hata |

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

Vercel Dashboard'da **Settings → Environment Variables** bölümüne ekle:

| Değişken | Açıklama |
|----------|----------|
| `OPENAI_API_KEY` | OpenAI API anahtarı |

---

## 🇬🇧 English

### About the Project

This project is triggered by an **Apple Shortcut** running on iPhone. When an SMS arrives, the Shortcut fires, forwards the message to this backend server, and the server generates a short, SMS-friendly reply using **OpenAI GPT-5.6 Luna**. For queries requiring current information, OpenAI's built-in **web search** is used automatically.

### How It Works

```
Incoming SMS
    │
    ▼
Apple Shortcuts
    │  JSON body: { "mesaj": "..." }
    ▼
POST /api/webhook
    │
    ▼
OpenAI Responses API (GPT-5.6 Luna)
    ├─ If needed: web_search_preview (built-in)
    │
    ▼
JSON response: { "reply": "..." }  (max 152 chars)
    │
    ▼
Apple Shortcuts sends automated reply
```

### Features

- 🤖 **OpenAI GPT-5.6 Luna** — fast and cost-effective ($0.20/1M input)
- 🔍 **Built-in Web Search** — automatic search for current information
- 📲 Full **Apple Shortcuts** compatibility
- ⚡ **Vercel** serverless deployment
- 🔐 Single API key management
- 📏 Turkish SMS-optimized replies (max 152 chars — UCS-2 encoding)

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

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

> Get your OpenAI API key at [platform.openai.com](https://platform.openai.com).

#### 4. Run the Local Server

```bash
python api/index.py
```

Server starts at `http://localhost:5000`.

### Deploy to Vercel

```bash
npm i -g vercel
vercel
```

Add `OPENAI_API_KEY` in Vercel Dashboard under **Settings → Environment Variables**.

---

## 📁 Project Structure

```
vercel-sms-ai/
├── api/
│   └── index.py        # Flask app & OpenAI Responses API handler
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
| OpenAI GPT-5.6 Luna | AI language model |
| OpenAI Responses API | Built-in web search + response generation |
| python-dotenv | Local environment variable loading |
| Vercel | Serverless hosting |
| Apple Shortcuts | SMS automation trigger |

## 📄 License

MIT
