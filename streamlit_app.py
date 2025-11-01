# streamlit_app.py
import os
import json
import random
import requests
import streamlit as st

# ================= Page Setup =================
st.set_page_config(
    page_title="HanyuMate — HSK Vocabulary Trainer",
    page_icon="🎓",
    layout="centered"
)

# ================= Language Toggle (TH/EN for UI only) =================
ui_en = st.toggle("Switch UI to English", value=True)  # True=EN UI, False=TH UI

# ================= Core Prompt (for instructor) =================
PROMPT_EN = """
Role:
You are a friendly Chinese language tutor who helps university students learn vocabulary and pronunciation.

Instruction:
When given a Chinese word and its pinyin, generate:
1) Two fields: the word (Chinese) + its pinyin + Thai/English meaning (short A1–A2).
2) A short multiple-choice question (3–4 options) testing the meaning.
3) Provide the correct answer clearly.

Constraints:
- Use HSK1–3 vocabulary only.
- Keep sentences simple (CEFR A1–A2).
- Options must be realistic and non-repetitive.
"""
with st.expander("🧠 Core Prompt (for future LLM connection) — Click to view"):
    st.code(PROMPT_EN, language="text")

# ================= UI Labels (Bilingual) =================
TXT = {
    "title_en": "HanyuMate — Chinese Vocabulary + Pinyin + Quiz (HSK1–3)",
    "title_th": "HanyuMate — สอนคำศัพท์จีน + พินอิน + แบบทดสอบ (HSK1–3)",

    "mode_label_en": "Mode",
    "mode_label_th": "โหมด",

    "lesson_tab_en": "Lesson",
    "lesson_tab_th": "โหมดเรียนศัพท์",

    "quiz_tab_en": "Quiz",
    "quiz_tab_th": "แบบทดสอบ",

    "level_label_en": "Pick HSK level",
    "level_label_th": "เลือกระดับ HSK",

    "learn_header_en": "Learn Vocabulary (Chinese + Pinyin + Meaning)",
    "learn_header_th": "เรียนคำศัพท์ (จีน + พินอิน + ความหมาย)",

    "vocab_en": "Vocab",
    "vocab_th": "คำศัพท์",

    "pinyin_en": "Pinyin",
    "pinyin_th": "พินอิน",

    "meaning_en": "Meaning",
    "meaning_th": "ความหมาย",

    "next_en": "Next",
    "next_th": "ถัดไป",

    "start_quiz_en": "Start Quiz for this level",
    "start_quiz_th": "เริ่มทำแบบทดสอบจากระดับนี้",

    "submit_en": "Submit",
    "submit_th": "ส่งคำตอบ",

    "score_en": "Score",
    "score_th": "คะแนน",

    "no_quiz_en": "No quiz yet — click New quiz set or go to Lesson and click Start Quiz.",
    "no_quiz_th": "ยังไม่มีชุดข้อสอบ — กดสร้างชุดใหม่ หรือไปหน้าเรียนแล้วกดเริ่มทำแบบทดสอบ",

    "back_lesson_en": "Back to Lesson",
    "back_lesson_th": "กลับไปหน้าเรียน",

    "new_set_en": "🆕 New quiz set",
    "new_set_th": "🆕 สร้างชุดใหม่",

    "regen_en": "♻️ Regenerate",
    "regen_th": "♻️ สุ่มใหม่",

    "clear_en": "🧹 Clear answers",
    "clear_th": "🧹 ล้างคำตอบ",
}

def t(key):
    return TXT[f"{key}_{'en' if ui_en else 'th'}"]

st.title(t("title"))

# ================= Vocab Bank =================
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
    ]
}

LEVELS = ["HSK1", "HSK2", "HSK3"]
N_QUESTIONS = 6

def mean_key():
    return "meaning_en" if ui_en else "meaning_th"

# ================= Session State =================
ss = st.session_state
if "view" not in ss: ss.view = "lesson"                  # "lesson" / "quiz"
if "level" not in ss: ss.level = "HSK1"
if "lesson_idx" not in ss: ss.lesson_idx = 0

# per-level states (ไม่ปนกัน)
if "quiz_map" not in ss: ss.quiz_map = {lvl: [] for lvl in LEVELS}
if "answers_map" not in ss: ss.answers_map = {lvl: {} for lvl in LEVELS}
if "submitted_map" not in ss: ss.submitted_map = {lvl: False for lvl in LEVELS}

# ================= Optional AI (DeepSeek) =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = "deepseek-chat"  # or "deepseek-reasoner"

def call_deepseek_generate(word: str, pinyin: str, level: str, meanings_pool_en: list):
    """Return one MCQ generated by DeepSeek (strict JSON)."""
    system = (
        "You are a Chinese vocabulary tutor for HSK learners. "
        "Return ONLY a JSON with fields: question, options(A,B,C,D), correct, explain."
    )
    user = f"""
HSK level: {level}
Word: {word}
Pinyin: {pinyin}
Task: Provide the standard CEFR A1–A2 English meaning as the correct option and create 3 realistic distractors.
Helpful pool of possible meanings: {list(set(meanings_pool_en))[:30]}
Return STRICT JSON, no extra text.
"""
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.4,
        "response_format": {"type": "json_object"}
    }
    url = "https://api.deepseek.com/chat/completions"
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    data = json.loads(content)

    letters = ["A", "B", "C", "D"]
    opts = [(k, data["options"][k]) for k in letters]
    return {
        "q": data["question"],
        "opts": opts,
        "correct": data["correct"].strip().upper(),
        "explain": data.get("explain", f"{word} ({pinyin})")
    }

# ================= Quiz Builders =================
def build_one_local_q(item, vocab):
    correct = item[mean_key()]
    distractors = random.sample([v[mean_key()] for v in vocab if v != item], min(3, len(vocab)-1))
    opts = [correct] + distractors
    random.shuffle(opts)
    letters = ["A", "B", "C", "D"]
    return {
        "q": f"{item['word']} — {TXT['meaning_en'] if ui_en else TXT['meaning_th']}",
        "opts": list(zip(letters[:len(opts)], opts)),
        "correct": letters[opts.index(correct)],
        "explain": f"{item['word']} ({item['pinyin']}) → {correct}"
    }

def generate_quiz(level: str, use_ai: bool):
    vocab = HSK_VOCAB[level]
    items = random.sample(vocab, min(N_QUESTIONS, len(vocab)))

    quiz = []
    if use_ai and DEEPSEEK_API_KEY:
        pool_en = [v["meaning_en"] for v in vocab]  # ให้โมเดลใช้ EN เป็นฐาน
        for it in items:
            try:
                quiz.append(call_deepseek_generate(it["word"], it["pinyin"], level, pool_en))
            except Exception:
                quiz.append(build_one_local_q(it, vocab))
    else:
        for it in items:
            quiz.append(build_one_local_q(it, vocab))
    return quiz

def show_results(level: str):
    qset = ss.quiz_map[level]
    answers = ss.answers_map[level]
    correct_n = 0
    for i, q in enumerate(qset, start=1):
        ans = answers.get(i)
        opt_map = {k: v for k, v in q["opts"]}
        if ans == q["correct"]:
            st.success(f"Q{i} ✅ {q['explain']}")
            correct_n += 1
        else:
            st.error(f"Q{i} ❌ {t('your_ans_'+('en' if ui_en else 'th')) if 'your_ans_en' in TXT else 'Your answer'}: {ans or '-'} | "
                     f"{t('correct')}: {q['correct']} ({opt_map[q['correct']]})")
    st.info(f"🏆 {t('score')}: {correct_n}/{len(qset)}")

# ================= Header Controls =================
view = st.radio(t("mode_label"), ["lesson", "quiz"],
                index=0 if ss.view == "lesson" else 1,
                format_func=lambda x: t("lesson_tab") if x == "lesson" else t("quiz_tab"))
ss.view = view  # sync back

# ระดับ (แก้บั๊ก key ซ้ำ: ไม่ใส่ key; ใช้ตัวแปรกลางแล้วค่อยอัปเดต ss.level)
selected_level = st.radio(t("level_label"), LEVELS, index=LEVELS.index(ss.level))
ss.level = selected_level
level = ss.level

use_ai = st.toggle("Use AI (DeepSeek) to generate quiz", value=False,
                   help="If off, uses built-in logic.")
if use_ai and not DEEPSEEK_API_KEY:
    st.warning("DeepSeek API key not found. Set environment variable DEEPSEEK_API_KEY or turn off the AI toggle.")

# ================= Views =================
if ss.view == "lesson":
    st.subheader(t("learn_header"))
    vocab = HSK_VOCAB[level]
    entry = vocab[ss.lesson_idx % len(vocab)]
    st.markdown(f"### {entry['word']}")
    st.write(f"• {t('pinyin')}: {entry['pinyin']}")
    st.write(f"• {t('meaning')}: {entry[mean_key()]}")

    c1, c2 = st.columns(2)
    if c1.button(t("next"), use_container_width=True):
        ss.lesson_idx = (ss.lesson_idx + 1) % len(vocab)

    if c2.button(t("start_quiz"), use_container_width=True):
        ss.quiz_map[level] = generate_quiz(level, use_ai)
        ss.answers_map[level] = {}
        ss.submitted_map[level] = False
        ss.view = "quiz"
        st.rerun()

else:
    qset = ss.quiz_map[level]

    c0, c1, c2, c3 = st.columns([1.2, 1, 1, 1.2])
    if c0.button(t("new_set"), use_container_width=True):
        ss.quiz_map[level] = generate_quiz(level, use_ai)
        ss.answers_map[level] = {}
        ss.submitted_map[level] = False
        st.rerun()
    if c1.button(t("regen"), use_container_width=True):
        ss.quiz_map[level] = generate_quiz(level, use_ai)
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
            # ใช้ key ต่อระดับเพื่อกันชนกัน
            picked = st.radio(f"Answer_{level}_{i}", labels,
                              key=f"{level}_q{i}",
                              disabled=ss.submitted_map[level])
            if picked:
                ss.answers_map[level][i] = picked.split(".")[0]

        if not ss.submitted_map[level] and st.button(t("submit"), type="primary"):
            ss.submitted_map[level] = True
            st.rerun()

        if ss.submitted_map[level]:
            st.divider()
            show_results(level)
