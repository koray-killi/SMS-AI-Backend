# 📱 SMS AI Backend

> **TR:** Apple Kestirmeler ile entegre çalışan, gelen SMS mesajlarını yapay zeka ile yanıtlayan Vercel tabanlı bir backend sunucusu.
>
> **EN:** A Vercel-based backend server that integrates with Apple Shortcuts to process incoming SMS messages and respond using AI.

---

## 🇹🇷 Türkçe

### Proje Hakkında

Bu proje, iPhone'da çalışan bir **Apple Kestirmesi (Shortcut)** tarafından tetiklenir. Kullanıcıya SMS gelen anda Kestirme devreye girer, mesajı bu backend sunucusuna iletir ve sunucu **NVIDIA NIM üzerinde çalışan Llama-3.3-70B** kullanarak kısa, SMS'e uygun bir yanıt üretir. Güncel bilgi gereken sorularda (hava, haberler, spor) **Tavily** ile gerçek zamanlı web araması yapılır. Yanıt tekrar Kestirme'ye döner ve otomatik SMS olarak gönderilebilir.

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
    ├─► NVIDIA NIM (Llama-3.3-70B) — Arama gerekiyor mu?
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

- 🤖 **NVIDIA NIM** — `meta/llama-3.3-70b-instruct` modeli
- 🔄 **Provider Seçici** — `LLM_PROVIDER` env değişkeni ile DeepSeek'e tek satırda geçiş
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
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=nvidia
```

> NVIDIA API anahtarını [build.nvidia.com](https://build.nvidia.com) adresinden edinebilirsin.  
> Tavily API anahtarını [app.tavily.com](https://app.tavily.com) adresinden edinebilirsin.

#### 4. Yerel Sunucuyu Başlat

```bash
python api/index.py
```

Sunucu `http://localhost:5000` adresinde çalışmaya başlar.

### Provider Değiştirme (DeepSeek Fallback)

Modeli DeepSeek ile kullanmak istersen `.env` dosyasında:

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

Başka bir kod değişikliğine gerek yok.

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
| `NVIDIA_API_KEY` | NVIDIA NIM API anahtarı |
| `TAVILY_API_KEY` | Tavily web arama API anahtarı |
| `LLM_PROVIDER` | `nvidia` veya `deepseek` |

---

## 🇬🇧 English

### About the Project

This project is triggered by an **Apple Shortcut** running on iPhone. When an SMS arrives, the Shortcut fires, forwards the message to this backend server, and the server generates a short, SMS-friendly reply using **Llama-3.3-70B on NVIDIA NIM**. For queries requiring current information (weather, news, sports), the server performs a real-time web search via **Tavily**.

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
    ├─► NVIDIA NIM (Llama-3.3-70B) — Does this need a search?
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

- 🤖 **NVIDIA NIM** — `meta/llama-3.3-70b-instruct` model
- 🔄 **Provider Switcher** — Switch to DeepSeek via `LLM_PROVIDER` env var
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
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=nvidia
```

> Get your NVIDIA API key at [build.nvidia.com](https://build.nvidia.com).  
> Get your Tavily API key at [app.tavily.com](https://app.tavily.com).

#### 4. Run the Local Server

```bash
python api/index.py
```

Server starts at `http://localhost:5000`.

### Switching Providers (DeepSeek Fallback)

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

No code changes required.

### API Reference

#### `POST /api/webhook`

**Request Body (JSON):**

```json
{
  "mesaj": "What's the weather in Istanbul today?"
}
```

**Success Response (200):**

```json
{
  "reply": "Istanbul: 28°C, sunny with clouds expected in the evening. ☀️"
}
```

### Deploy to Vercel

```bash
npm i -g vercel
vercel
```

Add these environment variables in Vercel Dashboard under **Settings → Environment Variables**:

| Variable | Description |
|----------|-------------|
| `NVIDIA_API_KEY` | NVIDIA NIM API key |
| `TAVILY_API_KEY` | Tavily web search API key |
| `LLM_PROVIDER` | `nvidia` or `deepseek` |

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
| NVIDIA NIM (Llama-3.3-70B) | Primary AI language model |
| DeepSeek | Fallback AI provider |
| OpenAI SDK | API client (compatible with both NVIDIA NIM & DeepSeek) |
| Tavily | Real-time web search for current information |
| python-dotenv | Local environment variable loading |
| Vercel | Serverless hosting |
| Apple Shortcuts | SMS automation trigger |

## 📄 License

MIT
