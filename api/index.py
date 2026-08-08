from flask import Flask, request, jsonify
import os
import json
from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

# .env dosyasını yükle (lokal geliştirme için; Vercel'de bu dosya olmayacak)
load_dotenv()

app = Flask(__name__)

# ─── Provider seçici ────────────────────────────────────────────────────────
def _build_client() -> tuple[OpenAI, str]:
    """
    LLM_PROVIDER env değişkenine göre istemci ve model adını döndürür.
    Desteklenen değerler: 'nvidia' (varsayılan), 'deepseek'
    """
    provider = os.environ.get("LLM_PROVIDER", "nvidia").lower()
    if provider == "deepseek":
        client = OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        model = "deepseek-chat"
    else:
        # Varsayılan: NVIDIA NIM
        client = OpenAI(
            api_key=os.environ.get("NVIDIA_API_KEY"),
            base_url="https://integrate.api.nvidia.com/v1"
        )
        model = "meta/llama-3.3-70b-instruct"
    return client, model

llm, MODEL = _build_client()

# Tavily arama istemcisi
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

# ─── Sistem promptu ─────────────────────────────────────────────────────────
# Not: Türkçe SMS'te özel karakterler (ğ, ü, ş, ı, ö, ç) UCS-2 encoding
# kullandığından GSM sınırı 70 değil, max 152 karakter (2 segment) olarak ayarlandı.
SYSTEM_PROMPT = (
    "Sen askerdeki birine SMS üzerinden yanıt veren, kısa ve öz konuşan bir asistansın. "
    "Cevapların maksimum 152 karakter olmalı — bunu kesinlikle aşma. "
    "Esprili ama bilgilendirici ol.\n\n"
    "ARAMA KURALI: Aşağıdaki konularda MUTLAKA search_web aracını kullan, "
    "kendi bilgine güvenme:\n"
    "- Tarih, saat, bugün/yarın/dün içeren sorular\n"
    "- Hava durumu\n"
    "- Güncel haberler, son dakika, bugünkü gelişmeler\n"
    "- Spor sonuçları, maç skoru, puan durumu\n"
    "- Döviz kuru, altın fiyatı, borsa\n"
    "- 'Kaç', 'ne kadar', 'kim kazandı', 'hangi takım' gibi güncel rakam/sonuç soruları\n"
    "- Herhangi bir konuda güncel/doğru olup olmadığından şüphe ettiğin bilgi\n\n"
    "Araştırmadan kesin tarih, fiyat veya rakam verme."
)

# ─── Araç (tool) tanımı ──────────────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "İnternette gerçek zamanlı arama yapar. Hava durumu, güncel haberler, "
                "spor sonuçları, fiyatlar veya AI'ın bilmediği/güncel olmayabileceği "
                "her konu için kullan."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Arama sorgusu. Kısa ve net tut."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# ─── Tavily arama fonksiyonu ─────────────────────────────────────────────────
def search_web(query: str) -> str:
    """Tavily ile web araması yapar; özet metni döndürür."""
    try:
        result = tavily.search(
            query=query,
            search_depth="basic",   # "advanced" daha iyi ama daha yavaş
            max_results=3,
            include_answer=True     # Tavily'nin kendi özetini de ekle
        )
        # Tavily'nin hazır özeti varsa onu kullan, yoksa snippet'leri birleştir
        if result.get("answer"):
            return result["answer"]

        snippets = [
            f"{r.get('title', '')}: {r.get('content', '')[:200]}"
            for r in result.get("results", [])
        ]
        return "\n".join(snippets) if snippets else "Arama sonucu bulunamadı."
    except Exception as e:
        return f"Arama hatası: {str(e)}"

# ─── Webhook endpoint ────────────────────────────────────────────────────────
@app.route('/api/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True) or {}
    user_message = data.get("mesaj", "")

    if not user_message:
        return jsonify({"reply": "Mesaj alınamadı."}), 400

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_message}
    ]

    try:
        # ── 1. İstek: AI arama yapmak istiyor mu? ───────────────────────────
        # max_tokens=500: tool call JSON'ı üretimi için yeterli alan gerekir.
        # Düşük limit NVIDIA NIM'de 400 hatasına neden olur.
        response = llm.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=500,
            temperature=0.7
        )

        msg = response.choices[0].message

        # ── 2. Tool call var mı? ─────────────────────────────────────────────
        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            args      = json.loads(tool_call.function.arguments)
            query     = args.get("query", user_message)

            # Tavily ile arama yap
            search_result = search_web(query)

            # Arama sonucunu mesaj geçmişine ekle
            messages.append(msg)                         # asistan mesajı (tool call içeren)
            messages.append({
                "role":         "tool",
                "tool_call_id": tool_call.id,
                "content":      search_result
            })

            # ── 3. İstek: Arama sonucuyla birlikte final SMS yanıtı ─────────
            # max_tokens=152: Türkçe UCS-2 SMS sınırı (2 segment)
            final_response = llm.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=152,
                temperature=0.7
            )
            bot_reply = final_response.choices[0].message.content
        else:
            # Arama gerekmedi, direkt yanıt
            bot_reply = msg.content

        return jsonify({"reply": bot_reply})

    except Exception as e:
        error_msg = str(e)
        # Rate limit veya servis hatası
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            return jsonify({"reply": "Şu an yoğunluk var, birazdan tekrar yaz."}), 429
        # Timeout
        if "timeout" in error_msg.lower():
            return jsonify({"reply": "Yanıt geç geldi, tekrar dene."}), 504
        # Genel hata
        return jsonify({"reply": f"Bir hata oluştu: {error_msg}"}), 500

# Vercel lokal testler için (Vercel'de çalışırken bu blok tetiklenmez)
if __name__ == '__main__':
    app.run(debug=True)