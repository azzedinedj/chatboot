from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
chat_history = []

# إعداد مفتاح Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# إنشاء الموديل
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(prompt):
    try:
        full_prompt = (
            "أنت مساعد ذكي متخصص في تعليم لغة الإشارة للصم والبكم، تفهم الدارجة الجزائرية جيداً. "
            "يجب أن تكون إجاباتك دقيقة، مختصرة، وعملية، وتركز على لغة الإشارة الجزائرية والعالمية. "
            "ابدأ دائماً إجابتك بالتحية المناسبة. "
            f"السؤال: {prompt.strip()}"
        )
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print("❌ خطأ:", e)
        return "تعذر الاتصال بـ Gemini. تحقق من الاتصال أو مفتاح API."

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"].strip()
        if user_input:
            chat_history.append({"role": "user", "content": user_input})
            reply = ask_gemini(user_input)
            chat_history.append({"role": "assistant", "content": reply})
            if request.headers.get("Accept") == "application/json":
                return jsonify(reply=reply)
    if not chat_history:
        chat_history.append({
            "role": "assistant",
            "content": "مرحباً! أنا مساعدك الذكي لتعلم لغة الإشارة. كيف يمكنني مساعدتك اليوم؟"
        })
    return render_template("index.html", messages=chat_history)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
