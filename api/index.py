from flask import Flask, request, jsonify
from openai import OpenAI
import openai as openai_lib
from dotenv import load_dotenv

# .env dosyasını yükle (lokal geliştirme için; Vercel'de bu dosya olmayacak)
load_dotenv()

app = Flask(__name__)

# ─── OpenAI istemcisi ────────────────────────────────────────────────────────
client = OpenAI(
    timeout=20.0,      # Vercel 30s limit için güvenli marj
    max_retries=0       # Fail fast — kullanıcıya hemen hata dön
)

# ─── Sistem promptu ─────────────────────────────────────────────────────────
# Not: Türkçe SMS'te özel karakterler (ğ, ü, ş, ı, ö, ç) UCS-2 encoding
# kullandığından GSM sınırı 70 değil, max 152 karakter (2 segment) olarak ayarlandı.
SYSTEM_PROMPT = (
    "Sen askerdeki birine SMS üzerinden yanıt veren, kısa ve öz konuşan bir asistansın. "
    "Cevapların maksimum 152 karakter olmalı — bunu kesinlikle aşma. "
    "Esprili ama bilgilendirici ol. "
    "Güncel bilgi gereken sorularda (hava, haberler, spor, kur, fiyat vb.) web araması yap."
)

# ─── Webhook endpoint ────────────────────────────────────────────────────────
@app.route('/api/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True) or {}
    user_message = data.get("mesaj", "")

    if not user_message:
        return jsonify({"reply": "Mesaj alınamadı."}), 400

    try:
        # OpenAI Responses API — tek çağrıda hem arama hem yanıt
        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=SYSTEM_PROMPT,
            input=user_message,
            tools=[{
                "type": "web_search_preview",
                "user_location": {
                    "type": "approximate",
                    "country": "TR"
                }
            }],
            max_output_tokens=512
        )

        # ── Yanıt metnini çıkar ─────────────────────────────────────────────
        # output_text bazen boş dönebilir; output item'lardan elle çıkar.
        bot_reply = response.output_text

        if not bot_reply:
            # output listesindeki tüm metin parçalarını topla
            parts = []
            for item in response.output:
                if hasattr(item, 'content'):
                    for content_part in item.content:
                        if hasattr(content_part, 'text') and content_part.text:
                            parts.append(content_part.text)
                elif hasattr(item, 'text') and item.text:
                    parts.append(item.text)
            bot_reply = "".join(parts)

        # Hâlâ boşsa, incomplete olabilir
        if not bot_reply:
            status = getattr(response, 'status', 'unknown')
            details = getattr(response, 'incomplete_details', None)
            bot_reply = f"Yanıt oluşturulamadı (status: {status}, details: {details})"

        return jsonify({"reply": bot_reply})

    except openai_lib.RateLimitError:
        return jsonify({"reply": "Şu an yoğunluk var, birazdan tekrar yaz."}), 429
    except openai_lib.APIStatusError as e:
        error_body = str(e.body) if hasattr(e, 'body') else str(e)
        if e.status_code == 503:
            return jsonify({"reply": "AI servisi şu an meşgul, biraz sonra dene."}), 503
        if e.status_code in (504, 408):
            return jsonify({"reply": "Yanıt geç geldi, tekrar dene."}), 504
        return jsonify({"reply": f"API hatası ({e.status_code}): {error_body[:150]}"}), 500
    except openai_lib.APITimeoutError:
        return jsonify({"reply": "Yanıt geç geldi, tekrar dene."}), 504
    except openai_lib.APIConnectionError:
        return jsonify({"reply": "Bağlantı hatası, tekrar dene."}), 502
    except Exception as e:
        return jsonify({"reply": f"Bir hata oluştu: {str(e)[:150]}"}), 500

# Vercel lokal testler için (Vercel'de çalışırken bu blok tetiklenmez)
if __name__ == '__main__':
    app.run(debug=True)