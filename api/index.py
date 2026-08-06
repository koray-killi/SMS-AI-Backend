from flask import Flask, request, jsonify
import os
import json
from openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

# .env dosyasını yükle (lokal geliştirme için; Vercel'de bu dosya olmayacak)
load_dotenv()

app = Flask(__name__)

# DeepSeek istemcisi (OpenAI SDK uyumlu)
deepseek = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# Tavily arama istemcisi
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

# ─── Sistem promptu ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "Sen askerdeki birine SMS üzerinden yanıt veren esprili, kısa ve öz konuşan bir asistansın. "
    "Cevapların bir SMS'e sığacak kadar (maksimum 150 karakter) kısa olmalı. "
    "Güncel bilgi, hava durumu, haberler veya spor sonuçları gibi internet araması gerektiren "
    "sorular için search_web aracını kullan."
)

# ─── Araç (tool) tanımı ──────────────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "İnternette gerçek zamanlı arama yapar. Hava durumu, güncel haberler, "
                "spor sonuçları, fiyatlar veya AI'ın bilmediği güncel konular için kullan."
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
        response = deepseek.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=150,
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

            # ── 3. İstek: Sonuçlarla birlikte final yanıt ───────────────────
            final_response = deepseek.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            bot_reply = final_response.choices[0].message.content
        else:
            # Arama gerekmedi, direkt yanıt
            bot_reply = msg.content

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"reply": f"Bir hata oluştu: {str(e)}"}), 500

# Vercel lokal testler için (Vercel'de çalışırken bu blok tetiklenmez)
if __name__ == '__main__':
    app.run(debug=True)