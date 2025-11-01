# streamlit_app.py
import os, json, random, streamlit as st
from openai import OpenAI   # ใช้ Groq (DeepSeek) ผ่าน OpenAI-compatible client

# ========== Page / i18n ==========
st.set_page_config(page_title="HanyuMate — HSK Vocabulary Trainer", page_icon="🎓", layout="centered")
ui_en = st.toggle("Switch UI to English", value=True)  # True = English UI, False = Thai UI

TXT = {
    "title_en": "HanyuMate — Chinese Vocabulary + Pinyin + Quiz (HSK1–3)",
    "title_th": "HanyuMate — สอนคำศัพท์จีน + พินอิน + แบบทดสอบ (HSK1–3)",
    "mode_label_en": "Mode", "mode_label_th": "โหมด",
    "lesson_tab_en": "Lesson", "lesson_tab_th": "โหมดเรียนศัพท์",
    "quiz_tab_en": "Quiz", "quiz_tab_th": "แบบทดสอบ",
    "level_label_en": "Pick HSK level", "level_label_th": "เลือกระดับ HSK",
    "learn_header_en": "Learn Vocabulary (Chinese + Pinyin + Meaning)",
    "learn_header_th": "เรียนคำศัพท์ (จีน + พินอิน + ความหมาย)",
    "pinyin_en": "Pinyin", "pinyin_th": "พินอิน",
    "meaning_en": "Meaning", "meaning_th": "ความหมาย",
    "next_en": "Next", "next_th": "ถัดไป",
    "start_quiz_en": "Start Quiz for this level", "start_quiz_th": "เริ่มทำแบบทดสอบจากระดับนี้",
    "ai_examples_en": "Generate AI examples for this word", "ai_examples_th": "ให้ AI สร้างประโยค/ทิปจำคำนี้",
    "new_set_en": "🆕 New quiz set", "new_set_th": "🆕 สร้างชุดใหม่",
    "regen_en": "♻️ Regenerate", "regen_th": "♻️ สุ่มใหม่",
    "clear_en": "🧹 Clear answers", "clear_th": "🧹 ล้างคำตอบ",
    "back_lesson_en": "Back to Lesson", "back_lesson_th": "กลับไปหน้าเรียน",
    "submit_en": "Submit", "submit_th": "ส่งคำตอบ",
    "score_en": "Score", "score_th": "คะแนน",
    "no_quiz_en": "No quiz yet — click New quiz set or go to Lesson and click Start Quiz.",
    "no_quiz_th": "ยังไม่มีชุดข้อสอบ — กดสร้างชุดใหม่ หรือไปหน้าเรียนแล้วกดเริ่มทำแบบทดสอบ",
}
def t(key): return TXT[f"{key}_{'en' if ui_en else 'th'}"]

with st.expander("🧠 Core Prompt (for future LLM connection) — Click to view"):
    st.code("""Role: You are a friendly Chinese language tutor.
Instruction: Given a Chinese word and its pinyin, create:
1) two short example sentences (Chinese + pinyin + EN + TH),
2) one short memory tip (tone/meaning).
Constraints: HSK1–3 only; CEFR A1–A2; options/wording concise.""", language="text")

st.title(t("title"))

# ========== Data ==========
HSK_VOCAB = {
    "HSK1": [
        {"word": "我", "pinyin": "wǒ", "meaning_en": "I; me", "meaning_th": "ฉัน/ผม"},
        {"word": "你", "pinyin": "nǐ", "meaning_en": "you", "meaning_th": "คุณ/เธอ"},
        {"word": "他", "pinyin": "tā", "meaning_en": "he", "meaning_th": "เขา (ผู้ชาย)"},
        {"word": "她", "pinyin": "tā", "meaning_en": "she", "meaning_th": "เธอ (ผู้หญิง)"},
        {"word": "我们", "pinyin": "wǒ men", "meaning_en": "we; us", "meaning_th": "พวกเรา"},
        {"word": "喜欢", "pinyin": "xǐ huan", "meaning_en": "to like", "meaning_th": "ชอบ"},
        {"word": "喝", "pinyin": "hē", "meaning_en": "to drink", "meaning_th": "ดื่ม"},
        {"word": "吃", "pinyin": "chī", "meaning_en": "to eat", "meaning_th": "กิน"},
        {"word": "看", "pinyin": "kàn", "meaning_en": "to watch/read", "meaning_th": "ดู/อ่าน"},
        {"word": "书", "pinyin": "shū", "meaning_en": "book", "meaning_th": "หนังสือ"},
    ],
    "HSK2": [
        {"word": "颜色", "pinyin": "yán sè", "meaning_en": "color", "meaning_th": "สี"},
        {"word": "机场", "pinyin": "jī chǎng", "meaning_en": "airport", "meaning_th": "สนามบิน"},
        {"word": "旅游", "pinyin": "lǚ yóu", "meaning_en": "to travel", "meaning_th": "ท่องเที่ยว"},
        {"word": "鱼", "pinyin": "yú", "meaning_en": "fish", "meaning_th": "ปลา"},
        {"word": "牛奶", "pinyin": "niú nǎi", "meaning_en": "milk", "meaning_th": "นมวัว"},
    ],
    "HSK3": [
        {"word": "环境", "pinyin": "huán jìng", "meaning_en": "environment", "meaning_th": "สิ่งแวดล้อม"},
        {"word": "认真", "pinyin": "rèn zhēn", "meaning_en": "serious; earnest", "meaning_th": "ตั้งใจ/จริงจัง"},
        {"word": "解决", "pinyin": "jiě jué", "meaning_en": "to solve", "meaning_th": "แก้ปัญหา"},
        {"word": "盘子", "pinyin": "pán zi", "meaning_en": "plate", "meaning_th": "จาน"},
        {"word": "电梯", "pinyin": "diàn tī", "meaning_en": "elevator", "meaning_th": "ลิฟต์"},
    ],
}
LEVELS = ["HSK1", "HSK2", "HSK3"]
N_QUESTIONS = 6
def mean_key(): return "meaning_en" if ui_en else "meaning_th"

# ========== Session ==========
ss = st.session_state
if "view" not in ss: ss.view = "lesson"                 # lesson / quiz
if "level" not in ss: ss.level = "HSK1"
if "lesson_idx" not in ss: ss.lesson_idx = 0
if "quiz_map" not in ss: ss.quiz_map = {lvl: [] for lvl in LEVELS}
if "answers_map" not in ss: ss.answers_map = {lvl: {} for lvl in LEVELS}
if "submitted_map" not in ss: ss.submitted_map = {lvl: False for lvl in LEVELS}

# ========== DeepSeek via Groq ==========
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = None
if DEEPSEEK_API_KEY:
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.groq.com/openai/v1")

def deepseek_chat(messages, temperature=0.4, model="deepseek-chat"):
    if not client:
        raise RuntimeError("API key not found")
    resp = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
    return resp.choices[0].message.content

# ========== Helpers ==========
def ai_examples_for_word(word, pinyin, meaning_en):
    prompt = f"""You are a friendly Chinese tutor.
Word: {word}
Pinyin: {pinyin}
Meaning(EN): {meaning_en}
Make 2 short examples (Chinese + pinyin + EN + TH) and 1 short memory tip (tone/meaning). A1–A2 level."""
    try:
        return deepseek_chat([{"role":"user","content":prompt}], temperature=0.3)
    except Exception as e:
        return f"⚠️ AI unavailable ({e})."

def build_one_local_q(item, vocab):
    correct = item[mean_key()]
    distractors = random.sample([v[mean_key()] for v in vocab if v != item], min(3, len(vocab)-1))
    options = [correct] + distractors
    random.shuffle(options)
    letters = ["A","B","C","D"]
    return {
        "word": item["word"], "pinyin": item["pinyin"],
        "q": f"{item['word']} — {TXT['meaning_en'] if ui_en else TXT['meaning_th']}",
        "opts": list(zip(letters[:len(options)], options)),
        "correct": letters[options.index(correct)],
        "explain": f"{item['word']} ({item['pinyin']}) → {correct}"
    }

def call_deepseek_mcq(item, vocab, level):
    pool_en = [v["meaning_en"] for v in vocab]
    user = f"""Create ONE MCQ (A–D) testing the meaning of the word.
Return STRICT JSON:
{{"question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}},"correct":"A|B|C|D","explain":"..."}}
Word:{item['word']}  Pinyin:{item['pinyin']}  HSK:{level}
Helpful meanings: {pool_en[:30]}"""
    try:
        txt = deepseek_chat([{"role":"system","content":"Chinese tutor for HSK learners."},
                             {"role":"user","content":user}], temperature=0.4)
        data = json.loads(txt)
        letters = ["A","B","C","D"]
        return {
            "word": item["word"], "pinyin": item["pinyin"],
            "q": data["question"],
            "opts": [(k, data["options"][k]) for k in letters],
            "correct": data["correct"].strip().upper(),
            "explain": data.get("explain", f"{item['word']} ({item['pinyin']})")
        }
    except Exception:
        return build_one_local_q(item, vocab)

def generate_quiz(level, use_ai):
    vocab = HSK_VOCAB[level]
    items = random.sample(vocab, min(N_QUESTIONS, len(vocab)))
    if use_ai and client: return [call_deepseek_mcq(it, vocab, level) for it in items]
    return [build_one_local_q(it, vocab) for it in items]

def show_results(level):
    qset = ss.quiz_map[level]; answers = ss.answers_map[level]; score = 0
    for i, q in enumerate(qset, start=1):
        opt_map = {k:v for k,v in q["opts"]}; ans = answers.get(i); corr = q["correct"]
        title = f"{q.get('word','')} ({q.get('pinyin','')})"
        if ans == corr:
            st.success(f"Q{i} ✅ {title} | Your answer: {ans}. {opt_map[corr]}")
            score += 1
        else:
            chosen = f"{ans}. {opt_map[ans]}" if ans in opt_map else "-"
            st.error(f"Q{i} ❌ {title} | Your answer: {chosen} | Correct: {corr}. {opt_map.get(corr,'-')}")
        st.caption(f"• Explanation: {q['explain']}")
    st.info(f"🏆 {t('score')}: {score}/{len(qset)}")

# ========== Header Controls (ปุ่มด้านบน) ==========
mode_value = st.radio(t("mode_label"), ["lesson","quiz"],
                      index=0 if ss.view=="lesson" else 1,
                      format_func=lambda x: t("lesson_tab") if x=="lesson" else t("quiz_tab"))
ss.view = mode_value

level_value = st.radio(t("level_label"), LEVELS, index=LEVELS.index(ss.level))
ss.level = level_value
level = ss.level

use_ai_quiz = st.toggle("Use AI (DeepSeek) to generate quiz", value=False,
                        help="If off, uses built-in logic.")
if use_ai_quiz and not client:
    st.warning("DeepSeek API key not found (env: DEEPSEEK_API_KEY). Using local quiz logic.")

st.divider()

# ========== Views ==========
if ss.view == "lesson":
    st.subheader(t("learn_header"))
    vocab = HSK_VOCAB[level]
    entry = vocab[ss.lesson_idx % len(vocab)]

    st.markdown(f"### {entry['word']}")
    st.write(f"• {t('pinyin')}: {entry['pinyin']}")
    st.write(f"• {t('meaning')}: {entry[mean_key()]}")

    c1, c2, c3 = st.columns([1,1,1.6])
    if c1.button(t("next"), use_container_width=True):
        ss.lesson_idx = (ss.lesson_idx + 1) % len(vocab)

    if c2.button(t("start_quiz"), use_container_width=True):
        ss.quiz_map[level] = generate_quiz(level, use_ai_quiz)
        ss.answers_map[level] = {}
        ss.submitted_map[level] = False
        ss.view = "quiz"
        st.rerun()

    if c3.button(t("ai_examples"), use_container_width=True):
        with st.spinner("AI is generating..."):
            out = ai_examples_for_word(entry["word"], entry["pinyin"], entry["meaning_en"])
        st.markdown("### 🤖 AI Examples / Tip")
        st.write(out)

else:
    qset = ss.quiz_map[level]

    c0, c1, c2, c3 = st.columns([1.2,1,1,1.2])
    if c0.button(t("new_set"), use_container_width=True):
        ss.quiz_map[level] = generate_quiz(level, use_ai_quiz)
        ss.answers_map[level] = {}
        ss.submitted_map[level] = False
        st.rerun()
    if c1.button(t("regen"), use_container_width=True):
        ss.quiz_map[level] = generate_quiz(level, use_ai_quiz)
        ss.answers_map[level] = {}
        ss.submitted_map[level] = False
        st.rerun()
    if c2.button(t("clear"), use_container_width=True):
        ss.answers_map[level] = {}
        ss.submitted_map[level] = False
        st.rerun()
    if c3.button(t("back_lesson"), use_container_width=True):
        ss.view = "lesson"
        st.rerun()

    st.divider()

    if not qset:
        st.info(t("no_quiz"))
    else:
        for i, q in enumerate(qset, start=1):
            st.markdown(f"**Q{i}. {q['q']}**")
            labels = [f"{k}. {txt}" for k, txt in q["opts"]]
            picked = st.radio(f"Answer_{level}_{i}", labels,
                              key=f"{level}_q{i}",
                              disabled=ss.submitted_map[level])
            if picked: ss.answers_map[level][i] = picked.split(".")[0]

        if not ss.submitted_map[level] and st.button(t("submit"), type="primary"):
            ss.submitted_map[level] = True
            st.rerun()

        if ss.submitted_map[level]:
            st.divider(); show_results(level)
