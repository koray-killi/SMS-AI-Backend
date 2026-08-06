from flask import Flask, request, jsonify
import os
from openai import OpenAI
from dotenv import load_dotenv

# .env dosyasını yükle (lokal geliştirme için; Vercel'de bu dosya olmayacak)
load_dotenv()


app = Flask(__name__)

# DeepSeek, OpenAI SDK'sını tam destekler. Sadece base_url değiştirilir.
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

@app.route('/api/webhook', methods=['POST'])
def webhook():
    # Kestirmeler'den gelen JSON verisini yakala
    data = request.get_json(silent=True) or {}
    user_message = data.get("mesaj", "")

    if not user_message:
        return jsonify({"reply": "Mesaj alınamadı."}), 400

    try:
        # DeepSeek API'sine istek at
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system", 
                    "content": "Sen askerdeki birine SMS üzerinden yanıt veren esprili, kısa ve öz konuşan bir asistansın. Cevapların bir SMS'e sığacak kadar (maksimum 150 karakter) kısa olmalı."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            max_tokens=100, # SMS maliyetini ve API tepki süresini düşük tutmak için
            temperature=0.7
        )
        
        bot_reply = response.choices[0].message.content
        
        # Sadece cevabı JSON olarak döndür
        return jsonify({"reply": bot_reply})
        
    except Exception as e:
        return jsonify({"reply": f"Bir hata oluştu: {str(e)}"}), 500

# Vercel lokal testler için (Vercel'de çalışırken bu blok tetiklenmez)
if __name__ == '__main__':
    app.run(debug=True)