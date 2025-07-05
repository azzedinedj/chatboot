from flask import Flask, render_template, request, jsonify
import requests
import os


app = Flask(__name__)
chat_history = []

# 🔑 المفتاح يوضع هنا مباشرة
API_KEY = f"Bearer {os.getenv('DEEPSEEK_API_KEY')}" 

def ask_deepseek(prompt):
    full_prompt = (
        "أنت مساعد ذكي متخصص في تعليم لغة الإشارة للصم والبكم، وتفهم الدارجة الجزائرية جيداً. "
        "يجب أن تكون إجاباتك دقيقة، مختصرة، وعملية، وتركز على كل ما يخص الصم والبكم: "
        "تعليم لغة الإشارة الجزائرية والعالمية، طرق التواصل، نصائح للأهل والمعلمين، حقوق الصم والبكم، "
        "التقنيات المساعدة، الثقافة المجتمعية، وكل ما يتعلق بتسهيل حياة الصم والبكم في الجزائر والعالم العربي. "
        "افهم أسئلة المستخدمين مهما كانت باللهجة الجزائرية أو العربية الفصحى أو حتى الفرنسية البسيطة، "
        "واشرح دائماً بالعربية الفصحى المبسطة، ويمكنك توضيح المصطلحات باللهجة الجزائرية عند الحاجة. "
        "إذا كان السؤال عن لغة الإشارة الجزائرية أو الدارجة الجزائرية، وضّح الأمثلة باللهجة الجزائرية. "
        "ابدأ دائماً إجابتك بالتحية المناسبة (مثلاً: السلام عليكم). "
        "اختصر الإجابة قدر الإمكان وقدم فقط المعلومات المفيدة والجوهرية دون إطالة أو تكرار. "
        "رتب إجابتك بشكل منظم وواضح، ويفضل استخدام التعداد أو الفقرات عند الحاجة. "
        "إذا كان السؤال غير واضح، اطلب توضيحاً. "
        "مهم جداً: لا تضع أي رموز أو إيموجي أو علامات زخرفية في الرد. "
        "إذا احتجت لعرض قائمة أو شرح خطوات، استخدم فقط نقاط مرتبة تحت بعضها هكذا:\n"
        "• النقطة الأولى\n• النقطة الثانية\n• ...الخ\n"
        f"السؤال: {prompt.strip()}"
    )

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": API_KEY
        }

        data = {
            "model": "deepseek/deepseek-r1-0528:free",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "أنت مساعد ذكي متخصص في كل ما يخص الصم والبكم في الجزائر والعالم العربي. "
                        "يجب أن تفهم الدارجة الجزائرية جيداً وتشرح دائماً بالعربية الفصحى المبسطة، "
                        "مع توضيح المصطلحات باللهجة الجزائرية عند الحاجة. "
                        "ركز على تعليم لغة الإشارة الجزائرية والعالمية، نصائح التواصل، حقوق الصم والبكم، "
                        "التقنيات المساعدة، الثقافة المجتمعية، وكل ما يسهل حياة الصم والبكم. "
                        "ابدأ دائماً إجابتك بالتحية المناسبة (مثلاً: السلام عليكم). "
                        "اختصر الإجابة قدر الإمكان وقدم فقط المعلومات المفيدة والجوهرية دون إطالة أو تكرار. "
                        "رتب إجابتك بشكل منظم وواضح، ويفضل استخدام التعداد أو الفقرات عند الحاجة. "
                        "مهم جداً: لا تضع أي رموز أو إيموجي أو علامات زخرفية في الرد. "
                        "إذا احتجت لعرض قائمة أو شرح خطوات، استخدم فقط نقاط مرتبة تحت بعضها هكذا:\n"
                        "• النقطة الأولى\n• النقطة الثانية\n• ...الخ\n"
                    )
                },
                *chat_history,
                {"role": "user", "content": full_prompt}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        reply = result["choices"][0]["message"]["content"]
        return reply

    except Exception as e:
        print("❌ فشل الاتصال بـ OpenRouter:", e)
        return "تعذر الاتصال بـ DeepSeek. تحقق من الاتصال أو مفتاح API."

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"].strip()
        if user_input:
            chat_history.append({"role": "user", "content": user_input})
            reply = ask_deepseek(user_input)
            chat_history.append({"role": "assistant", "content": reply})
            # إذا كان الطلب AJAX أرجع JSON فقط
            if request.headers.get("Accept") == "application/json":
                return jsonify(reply=reply)
    if not chat_history:
        chat_history.append({
            "role": "assistant",
            "content": "مرحباً! أنا مساعدك الذكي لتعلم لغة الإشارة. كيف يمكنني مساعدتك اليوم؟"
        })
    return render_template("index.html", messages=chat_history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

