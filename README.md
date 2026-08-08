# 📱 SMS AI Backend

> **TR:** Apple Kestirmeler ile entegre çalışan, gelen SMS mesajlarını yapay zeka ile yanıtlayan Vercel tabanlı bir backend sunucusu.
>
> **EN:** A Vercel-based backend server that integrates with Apple Shortcuts to process incoming SMS messages and respond using AI.

---

## 🇹🇷 Türkçe

### Proje Hakkında

Bu proje, iPhone'da çalışan bir **Apple Kestirmesi (Shortcut)** tarafından tetiklenir. Kullanıcıya SMS gelen anda Kestirme devreye girer, mesajı bu backend sunucusuna iletir ve sunucu **Google Gemini (gemini-3.5-flash)** kullanarak kısa, SMS'e uygun bir yanıt üretir. Güncel bilgi gereken sorularda (hava, haberler, spor) **Tavily** ile gerçek zamanlı web araması yapılır. Yanıt tekrar Kestirme'ye döner ve otomatik SMS olarak gönderilebilir.

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
    ├─► Gemini 3.5 Flash — Arama gerekiyor mu?
    │         │
    │    Evet ▼
    │   Tavily Web Araması
    │         │
    └─────────▼
         Final SMS Yanıtı (maks. 152 karakter)
    │
    ▼
JSON yanıt: { "reply": "..." }
    │
    ▼
Apple Kestirmesi otomatik yanıt gönderir
```

### Özellikler

- 🤖 **Google Gemini** — `gemini-3.5-flash` modeli (ücretsiz tier: 15 RPM, 1500 RPD)
- 🔄 **Provider Seçici** — `LLM_PROVIDER` env değişkeni ile NVIDIA NIM veya DeepSeek'e geçiş
- 🔍 **Agresif Arama Politikası** — Tarih, hava, haberler, kur, spor sorularında otomatik Tavily araması
- 📲 **Apple Kestirmeler** ile tam uyumluluk
- ⚡ **Vercel** serverless deployment
- 🔐 `.env` ile güvenli API key yönetimi
- 📏 Türkçe SMS boyutuna uygun yanıtlar (maks. 152 karakter — UCS-2 encoding, 2 segment)

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
GEMINI_API_KEY=AIzaSy-xxxxxxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=gemini
```

> Gemini API anahtarını [aistudio.google.com](https://aistudio.google.com) adresinden edinebilirsin (ücretsiz).  
> Tavily API anahtarını [app.tavily.com](https://app.tavily.com) adresinden edinebilirsin.

#### 4. Yerel Sunucuyu Başlat

```bash
python api/index.py
```

Sunucu `http://localhost:5000` adresinde çalışmaya başlar.

### Provider Değiştirme

`.env` dosyasında `LLM_PROVIDER` değerini değiştirerek provider geçişi yapabilirsin:

| Provider | `LLM_PROVIDER` | API Key | Model |
|----------|----------------|---------|-------|
| **Google Gemini** (varsayılan) | `gemini` | `GEMINI_API_KEY` | `gemini-3.5-flash` |
| NVIDIA NIM | `nvidia` | `NVIDIA_API_KEY` | `meta/llama-3.3-70b-instruct` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` | `deepseek-chat` |

Kod değişikliğine gerek yok — tüm providerlar OpenAI SDK uyumlu endpoint kullanır.

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

Vercel Dashboard'da **Settings → Environment Variables** bölümüne şu değerleri ekle:

| Değişken | Açıklama |
|----------|----------|
| `GEMINI_API_KEY` | Google Gemini API anahtarı |
| `TAVILY_API_KEY` | Tavily web arama API anahtarı |
| `LLM_PROVIDER` | `gemini`, `nvidia` veya `deepseek` |

---

## 🇬🇧 English

### About the Project

This project is triggered by an **Apple Shortcut** running on iPhone. When an SMS arrives, the Shortcut fires, forwards the message to this backend server, and the server generates a short, SMS-friendly reply using **Google Gemini (gemini-3.5-flash)**. For queries requiring current information (weather, news, sports), the server performs a real-time web search via **Tavily**.

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
    ├─► Gemini 3.5 Flash — Does this need a search?
    │         │
    │    Yes  ▼
    │   Tavily Web Search
    │         │
    └─────────▼
         Final SMS Reply (max 152 characters)
    │
    ▼
JSON response: { "reply": "..." }
    │
    ▼
Apple Shortcuts sends automated reply
```

### Features

- 🤖 **Google Gemini** — `gemini-3.5-flash` model (free tier: 15 RPM, 1500 RPD)
- 🔄 **Provider Switcher** — Switch to NVIDIA NIM or DeepSeek via `LLM_PROVIDER` env var
- 🔍 **Aggressive Search Policy** — Auto Tavily search for dates, weather, news, prices, sports
- 📲 Full **Apple Shortcuts** compatibility
- ⚡ **Vercel** serverless deployment
- 🔐 Secure API key management via `.env`
- 📏 Turkish SMS-optimized replies (max 152 chars — UCS-2 encoding, 2 segments)

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
GEMINI_API_KEY=AIzaSy-xxxxxxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=gemini
```

> Get your Gemini API key for free at [aistudio.google.com](https://aistudio.google.com).  
> Get your Tavily API key at [app.tavily.com](https://app.tavily.com).

#### 4. Run the Local Server

```bash
python api/index.py
```

Server starts at `http://localhost:5000`.

### Switching Providers

| Provider | `LLM_PROVIDER` | API Key | Model |
|----------|----------------|---------|-------|
| **Google Gemini** (default) | `gemini` | `GEMINI_API_KEY` | `gemini-3.5-flash` |
| NVIDIA NIM | `nvidia` | `NVIDIA_API_KEY` | `meta/llama-3.3-70b-instruct` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` | `deepseek-chat` |

No code changes required — all providers use OpenAI SDK compatible endpoints.

### Deploy to Vercel

```bash
npm i -g vercel
vercel
```

Add these environment variables in Vercel Dashboard under **Settings → Environment Variables**:

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `TAVILY_API_KEY` | Tavily web search API key |
| `LLM_PROVIDER` | `gemini`, `nvidia` or `deepseek` |

---

## 📁 Project Structure

```
vercel-sms-ai/
├── api/
│   └── index.py        # Flask app, LLM provider selector & webhook handler
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
| Google Gemini (gemini-3.5-flash) | Primary AI language model (free tier) |
| NVIDIA NIM / DeepSeek | Fallback AI providers |
| OpenAI SDK | API client (compatible with all providers) |
| Tavily | Real-time web search for current information |
| python-dotenv | Local environment variable loading |
| Vercel | Serverless hosting |
| Apple Shortcuts | SMS automation trigger |

## 📄 License

MIT
