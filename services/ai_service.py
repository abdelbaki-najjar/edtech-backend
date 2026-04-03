# services/ai_service.py
# ── محرك الذكاء الاصطناعي المحسّن — منهج تونسي رسمي ───────────

import json
import random
import httpx
from core.config import settings

# ══════════════════════════════════════════════════════════════
#  SYSTEM PROMPT الاحترافي — مرساة المنهج التونسي
# ══════════════════════════════════════════════════════════════
MASTER_SYSTEM_PROMPT = """أنت خبير تربوي متخصص في المنهج الدراسي التونسي الرسمي للتعليم الابتدائي.
لديك معرفة عميقة بـ:
- مناهج وزارة التربية التونسية للمراحل 1 إلى 6 ابتدائي
- الكتب المدرسية الرسمية التونسية (رياضيات، عربية، علوم، فرنسية، إنجليزية)
- المعايير التربوية والكفايات المطلوبة لكل مرحلة
- أساليب التدريس والتقييم المعتمدة في تونس

مهمتك: توليد محتوى تعليمي تفاعلي عالي الجودة يتوافق 100% مع المنهج الرسمي.

قواعد صارمة:
1. الأسئلة يجب أن تكون دقيقة علمياً ومتوافقة مع المستوى الدراسي
2. استخدم المصطلحات الرسمية الواردة في الكتب المدرسية التونسية
3. تدرّج في الصعوبة من السهل للصعب داخل نفس الدرس
4. الخيارات الخاطئة يجب أن تكون منطقية (أخطاء شائعة يقع فيها الطلاب)
5. أعد JSON فقط — لا نص قبله ولا بعده"""


# ══════════════════════════════════════════════════════════════
#  CURRICULUM CONTEXT — سياق المناهج التونسية
# ══════════════════════════════════════════════════════════════
CURRICULUM_CONTEXT = {
    "math": """المنهج التونسي للرياضيات:
- الأعداد والعمليات: الجمع، الطرح، الضرب، القسمة، الكسور، الأعداد العشرية
- الهندسة: الأشكال الهندسية، المحيط، المساحة، التناظر
- القياس: الطول، الكتلة، السعة، الزمن، المساحة
- حل المسائل: التفكير المنطقي والمسائل السياقية
- الإحصاء: الجداول والأعمدة البيانية (السنوات العليا)""",

    "arabic": """المنهج التونسي للغة العربية:
- القراءة والفهم: النصوص الأدبية والوظيفية
- التعبير الكتابي: الوصف، السرد، الحوار
- النحو والصرف: الجملة الاسمية والفعلية، الفاعل والمفعول، الأزمنة
- الإملاء: قواعد الكتابة الصحيحة، الهمزات، التاء المربوطة
- المعجم: تنمية الثروة اللغوية، المترادفات، الأضداد""",

    "science": """المنهج التونسي للعلوم:
- الكائنات الحية: النبات، الحيوان، جسم الإنسان
- البيئة: الماء، الهواء، التربة، الطاقة
- الفيزياء البسيطة: الضوء، الصوت، المغناطيس، الكهرباء
- الصحة والغذاء: التغذية السليمة، النظافة، الوقاية
- علوم الأرض: الفصول، المناخ، الظواهر الطبيعية""",

    "french": """المنهج التونسي للغة الفرنسية:
- المفردات الأساسية: الأسرة، المدرسة، الألوان، الأعداد، الحيوانات
- القواعد الأساسية: الأفعال الشائعة، المذكر والمؤنث، المفرد والجمع
- التعبير الشفوي: التحية، التعريف بالنفس، وصف الأشياء
- القراءة: النصوص البسيطة والحوارات اليومية""",

    "english": """المنهج التونسي للغة الإنجليزية:
- المفردات: الألوان، الأرقام، أيام الأسبوع، الشهور، الحيوانات، الأسرة
- التعبير: التحية، التعريف بالنفس، وصف الأشياء
- القواعد: To be, Have got, Present Simple, Can/Can't
- الأصوات والحروف: الأبجدية، نطق الكلمات"""
}


# ══════════════════════════════════════════════════════════════
#  CALL AI — الاستدعاء الموحّد
# ══════════════════════════════════════════════════════════════
async def call_ai(system: str, user: str) -> str:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "EdTech Tunisia",
    }
    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "max_tokens": 2000,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )

    data = res.json()

    if res.status_code != 200:
        raise Exception(f"OpenRouter Error {res.status_code}: {data}")

    if "choices" not in data or not data["choices"]:
        raise Exception(f"لا يوجد choices في الرد: {data}")

    content = data["choices"][0]["message"]["content"]

    if not content or not content.strip():
        raise Exception("الرد فارغ من النموذج")

    # تنظيف
    content = content.strip()
    if "```" in content:
        for part in content.split("```"):
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                content = part
                break

    return content


# ══════════════════════════════════════════════════════════════
#  FIX QUESTIONS — إصلاح الأسئلة تلقائياً
# ══════════════════════════════════════════════════════════════
def fix_questions(questions: list) -> list:
    """يضمن جودة الأسئلة: الجواب موجود، 4 خيارات، لا تكرار"""
    fixed = []
    for q in questions:
        correct = str(q.get("correct", "")).strip()
        options = [str(o).strip() for o in q.get("options", [])]

        # تأكد أن الجواب الصحيح موجود في الخيارات
        if correct not in options:
            if len(options) >= 4:
                options[0] = correct
            else:
                options.insert(0, correct)

        # إزالة التكرار
        seen = []
        for o in options:
            if o not in seen:
                seen.append(o)
        options = seen

        # أكمل لـ 4 خيارات إذا ناقصة
        while len(options) < 4:
            options.append(f"خيار {len(options)+1}")

        # خذ 4 فقط وخلّط
        options = options[:4]
        random.shuffle(options)

        fixed.append({
            "q": q.get("q", "").strip(),
            "correct": correct,
            "options": options,
        })

    return fixed


# ══════════════════════════════════════════════════════════════
#  GENERATE GAME — التوليد الاحترافي
# ══════════════════════════════════════════════════════════════
async def generate_game(
    grade: int,
    subject: str,
    lesson_title: str,       # ← عنوان حر من المستخدم
    game_type: str,
    difficulty: str = "medium",
    num_questions: int = 8,
) -> dict:

    grades   = ["الأول","الثاني","الثالث","الرابع","الخامس","السادس"]
    diff_map = {
        "easy":   "سهلة — للتعزيز والثقة، أسئلة مباشرة وواضحة",
        "medium": "متوسطة — تقيس الفهم الحقيقي للمفهوم",
        "hard":   "صعبة — تتطلب التفكير النقدي وتطبيق المفهوم في سياقات جديدة",
    }
    subject_ar = {
        "math": "الرياضيات", "arabic": "اللغة العربية",
        "science": "العلوم", "french": "اللغة الفرنسية", "english": "اللغة الإنجليزية",
    }.get(subject, subject)

    language_instruction = {
        "math":    "اكتب الأسئلة والأجوبة باللغة العربية.",
        "arabic":  "اكتب الأسئلة والأجوبة باللغة العربية الفصحى.",
        "science": "اكتب الأسئلة والأجوبة باللغة العربية.",
        "french":  """Write ALL questions and answers in FRENCH only.
                      The questions test French language skills.
                      Options must be French words/phrases.
                      Do NOT use Arabic in questions or options.""",
        "english": """Write ALL questions and answers in ENGLISH only.
                      The questions test English language skills.
                      Options must be English words/phrases.
                      Do NOT use Arabic in questions or options.""",
    }.get(subject, "اكتب الأسئلة والأجوبة باللغة العربية.")

    curriculum = CURRICULUM_CONTEXT.get(subject, "")

    prompt = f"""أنت تُعدّ أسئلة لعبة تعليمية احترافية.

## معلومات الدرس
- القسم: {grades[grade-1]} ابتدائي
- المادة: {subject_ar}
- عنوان الدرس: **{lesson_title}**
- مستوى الصعوبة: {diff_map[difficulty]}
- نوع اللعبة: {game_type}
- عدد الأسئلة المطلوبة: {num_questions}


## ⚠️ لغة الأسئلة — مهم جداً
{language_instruction}

## سياق المنهج التونسي
{curriculum}

## تعليمات الجودة
1. كل سؤال يجب أن يقيس مهارة محددة من درس "{lesson_title}"
2. تنوّع في مستويات التفكير: تذكّر، فهم، تطبيق
3. الخيارات الخاطئة = أخطاء شائعة يقع فيها تلاميذ القسم {grades[grade-1]}
4. الأسئلة متدرجة: من الأسهل للأصعب
5. اجعل الأسئلة ممتعة ومحفزة للطفل

## الشكل المطلوب (JSON فقط)
{{
  "title": "عنوان جذاب للعبة يذكر موضوع الدرس",
  "learning_objectives": ["الهدف التعليمي 1", "الهدف التعليمي 2"],
  "questions": [
    {{
      "q": "نص السؤال الواضح والمحدد؟",
      "correct": "الجواب الصحيح الدقيق",
      "options": ["الجواب الصحيح", "خطأ شائع 1", "خطأ شائع 2", "خطأ شائع 3"]
    }}
  ]
}}

تذكر: {num_questions} أسئلة بالضبط في مصفوفة questions."""

    text = await call_ai(MASTER_SYSTEM_PROMPT, prompt)
    data = json.loads(text)

    # إصلاح وضمان الجودة
    data["questions"] = fix_questions(data.get("questions", []))

    # إذا الأسئلة ناقصة
    if len(data["questions"]) < num_questions:
        raise Exception(f"النموذج ولّد {len(data['questions'])} أسئلة فقط بدل {num_questions}")

    print(f"✅ تم توليد {len(data['questions'])} سؤال لدرس: {lesson_title}")
    return data


# ══════════════════════════════════════════════════════════════
#  GENERATE WORKSHEET
# ══════════════════════════════════════════════════════════════
async def generate_worksheet(
    grade: int,
    subject: str,
    lesson_title: str,
    difficulty: str = "medium",
    student_name: str = None,
) -> dict:

    grades   = ["الأول","الثاني","الثالث","الرابع","الخامس","السادس"]
    diff_ar  = {"easy":"سهلة","medium":"متوسطة","hard":"صعبة"}
    subject_ar = {
        "math":"الرياضيات","arabic":"اللغة العربية",
        "science":"العلوم","french":"اللغة الفرنسية","english":"اللغة الإنجليزية",
    }.get(subject, subject)

    curriculum = CURRICULUM_CONTEXT.get(subject, "")

    language_instruction = {
        "math":    "اكتب كل التمارين باللغة العربية.",
        "arabic":  "اكتب كل التمارين باللغة العربية الفصحى.",
        "science": "اكتب كل التمارين باللغة العربية.",
        "french":  """Write ALL exercises in FRENCH only.
                      This is a French language worksheet.
                      All fill-in-the-blanks, MCQ, and exercises must be in French.
                      Do NOT use Arabic in exercises or answers.""",
        "english": """Write ALL exercises in ENGLISH only.
                      This is an English language worksheet.
                      All fill-in-the-blanks, MCQ, and exercises must be in English.
                      Do NOT use Arabic in exercises or answers.""",
    }.get(subject, "اكتب التمارين باللغة العربية.")

    prompt = f"""أعدّ ورقة عمل مدرسية احترافية متوافقة مع المنهج التونسي.

## معلومات
- القسم: {grades[grade-1]} ابتدائي
- المادة: {subject_ar}
- الدرس: {lesson_title}
- المستوى: {diff_ar[difficulty]}
- اسم التلميذ: {student_name or ".........."}


## ⚠️ لغة ورقة العمل — مهم جداً
{language_instruction}

## سياق المنهج
{curriculum}

## المطلوب
ورقة عمل شاملة تغطي الدرس بأكمله مع 4 أنواع من التمارين.

أعد JSON فقط:
{{
  "title": "عنوان ورقة العمل",
  "objectives": ["كفاية 1", "كفاية 2", "كفاية 3"],
  "sections": [
    {{
      "type": "fill",
      "title": "أكمل الفراغات",
      "items": ["جملة مع ___ فراغ للإجابة", "جملة أخرى ___"]
    }},
    {{
      "type": "mcq",
      "title": "اختر الإجابة الصحيحة",
      "items": [
        {{"q": "سؤال واضح؟", "opts": ["الجواب", "خطأ 1", "خطأ 2", "خطأ 3"], "ans": "الجواب"}}
      ]
    }},
    {{
      "type": "solve",
      "title": "حلّ وأجب",
      "items": ["مسألة أو تمرين تطبيقي 1", "مسألة 2", "مسألة 3"]
    }},
    {{
      "type": "free",
      "title": "أعبّر بأسلوبي",
      "items": ["سؤال مفتوح يحفز التفكير النقدي"]
    }}
  ]
}}"""

    text = await call_ai(MASTER_SYSTEM_PROMPT, prompt)
    return json.loads(text)


# ══════════════════════════════════════════════════════════════
#  ANALYZE STUDENT
# ══════════════════════════════════════════════════════════════
async def analyze_student(student_name: str, sessions_data: list) -> dict:
    if not sessions_data:
        return {
            "overall_level": "لا توجد بيانات",
            "analysis": "لم يكمل التلميذ أي جلسة بعد",
            "recommendations": ["ابدأ بلعبة واحدة يومياً"],
            "encouragement": "أنت قادر على التميز! ابدأ الآن 🌟"
        }

    summary = "\n".join([
        f"- {s.get('subject','')}/{s.get('lesson','')}: {s.get('score',0)}/{s.get('total',10)} ({s.get('percentage',0):.0f}%)"
        for s in sessions_data[-10:]
    ])

    prompt = f"""حلّل أداء التلميذ {student_name} في المنهج التونسي:

{summary}

أعد JSON:
{{
  "overall_level": "ممتاز/جيد جداً/جيد/متوسط/يحتاج دعماً",
  "strong_subjects": ["مادة قوي فيها"],
  "weak_subjects": ["مادة يحتاج تحسيناً"],
  "recommended_difficulty": "easy/medium/hard",
  "analysis": "تحليل تربوي دقيق (3 جمل)",
  "recommendations": ["توصية عملية 1", "توصية 2", "توصية 3"],
  "encouragement": "رسالة تشجيع شخصية للتلميذ"
}}"""

    text = await call_ai(
        "أنت مستشار تربوي متخصص في المنهج التونسي. أعد JSON فقط.",
        prompt
    )
    return json.loads(text)


# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
def calc_adaptive_difficulty(sessions: list) -> str:
    if len(sessions) < 2:
        return "medium"
    recent = sessions[-3:]
    avg = sum(s.get("percentage", 50) for s in recent) / len(recent)
    return "hard" if avg >= 85 else "easy" if avg < 60 else "medium"


def calc_badges(total_xp: int, total_sessions: int, avg_score: float) -> list:
    b = []
    if total_sessions >= 1:  b.append("⭐")
    if avg_score >= 90:      b.append("🔥")
    if total_sessions >= 5:  b.append("🎯")
    if total_xp >= 400:      b.append("💎")
    if total_xp >= 700:      b.append("🏆")
    if total_sessions >= 20: b.append("🚀")
    return b
