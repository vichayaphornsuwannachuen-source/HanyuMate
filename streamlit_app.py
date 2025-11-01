import os
import json
import random
import streamlit as st
from openai import OpenAI

# =============== Page Setup ===============
st.set_page_config(page_title="HanyuMate — Chinese Vocabulary + Pinyin + Quiz (HSK1–3)", page_icon="🎓", layout="centered")

# =============== UI Language Toggle ===============
ui_en = st.toggle("Switch UI to English", value=True)

# =============== DeepSeek Setup ===============
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = None
if DEEPSEEK_API_KEY:
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.groq.com/openai/v1")

# =============== Core Prompt (for display only) ===============
PROMPT_EN = """
Role: You are a friendly Chinese tutor.
Instruction:
When given a Chinese word and pinyin, generate:
1. Two example sentences (Chinese + Pinyin + English + Thai)
2. A short tip to remember tone or meaning
Constraints:
- Use HSK1–3 vocabulary only
- Keep sentences simple (CEFR A1–A2)
"""
with st.expander("🧠 Core Prompt (for future LLM connection) — Click to view"):
    st.code(PROMPT_EN, language="text")

# =============== Text Labels ===============
TXT = {
    "title_en": "HanyuMate — Chinese Vocabulary + Pinyin + Quiz (HSK1–3)",
    "title_th": "HanyuMate — สอนคำศัพท์จีน + พินอิน + แบบทดสอบ (HSK1–3)",
    "mode_label_en": "Mode", "mode_label_th": "โหมด",
    "lesson_tab_en": "Lesson", "lesson_tab_th": "โหมดเรียนศัพท์",
    "quiz_tab_en": "Quiz", "quiz_tab_th": "แบบทดสอบ",
    "level_label_en": "Pick HSK level", "level_label_th": "เลือกระดับ HSK",
    "learn_header_en": "Learn Vocabulary (Chinese + Pinyin + Meaning)",
    "learn_header_th": "เรียนคำศัพท์ (จีน + พินอิน + ความหมาย)",
    "vocab_en": "Vocab", "vocab_th": "คำศัพท์",
    "pinyin_en": "Pinyin", "pinyin_th": "พินอิน",
    "meaning_en": "Meaning", "meaning_th": "ความหมาย",
    "next_en": "Next", "next_th": "ถัดไป",
    "start_quiz_en": "Start Quiz for this level", "start_quiz_th": "เริ่มทำแบบทดสอบจากระดับนี้",
    "submit_en": "Submit", "submit_th": "ส่งคำตอบ",
    "score_en": "Score", "score_th": "คะแนน",
    "ai_examples_en": "Generate AI examples for this word", "ai_examples_th": "ให้ AI สร้างประโยคตัวอย่าง/ทิปจำคำนี้",
    "new_set_en": "🆕 New quiz set", "new_set_th": "🆕 สร้างชุดใหม่",
    "regen_en": "♻️ Regenerate", "regen_th": "♻️ สุ่มใหม่",
    "clear_en": "🧹 Clear answers", "clear_th": "🧹 ล้างคำตอบ",
    "back_lesson_en": "⬅️ Back to Lesson", "back_lesson_th": "⬅️ กลับไปหน้าเรียน",
}
def t(key): return TXT[f"{key}_{'en' if ui_en else 'th'}"]

st.title(t("title"))

# =============== Vocabulary Data ===============
HSK_VOCAB = {
    "HSK1": [
        {"word": "我", "pinyin": "wǒ", "meaning_en": "I; me", "meaning_th": "ฉัน/ผม"},
        {"word": "你", "pinyin": "nǐ", "meaning_en": "you", "meaning_th": "คุณ/เธอ"},
        {"word": "他", "pinyin": "tā", "meaning_en": "he", "meaning_th": "เขา"},
        {"word": "她", "pinyin": "tā", "meaning_en": "she", "meaning_th": "เธอ"},
        {"word": "喜欢", "pinyin": "xǐ huan", "meaning_en": "to like", "meaning_th": "ชอบ"},
    ],
    "HSK2": [
        {"word": "颜色", "pinyin": "yán sè", "meaning_en": "color", "meaning_th": "สี"},
        {"word": "机场", "pinyin": "jī chǎng", "meaning_en": "airport", "meaning_th": "สนามบิน"},
        {"word": "旅游", "pinyin": "lǚ yóu", "meaning_en": "to travel", "meaning_th": "ท่องเที่ยว"},
        {"word": "牛奶", "pinyin": "niú nǎi", "meaning_en": "milk", "meaning_th": "นม"},
        {"word": "地图", "pinyin": "dì tú", "meaning_en": "map", "meaning_th": "แผนที่"},
    ],
    "HSK3": [
        {"word": "环境", "pinyin": "huán jìng", "meaning_en": "environment", "meaning_th": "สิ่งแวดล้อม"},
        {"word": "认真", "pinyin": "rèn zhēn", "meaning_en": "serious", "meaning_th": "ตั้งใจ"},
        {"word": "解决", "pinyin": "jiě jué", "meaning_en": "to solve", "meaning_th": "แก้ปัญหา"},
        {"word": "文化", "pinyin": "wén huà", "meaning_en": "culture", "meaning_th": "วัฒนธรรม"},
        {"word": "电梯", "pinyin": "diàn tī", "meaning_en": "elevator", "meaning_th": "ลิฟต์"},
    ]
}
LEVELS = ["HSK1", "HSK2", "HSK3"]
def mean_key(): return "meaning_en" if ui_en else "meaning_th"

# =============== State ===============
ss = st.session_state
if "view" not in ss: ss.view = "lesson"
if "level" not in ss: ss.level = "HSK1"
if "lesson_idx" not in ss: ss.lesson_idx = 0
if "quiz_map" not in ss: ss.quiz_map = {lvl: [] for lvl in LEVELS}
if "answers_map" not in ss: ss.answers_map = {lvl: {} for lvl in LEVELS}
if "submitted_map" not in ss: ss.submitted_map = {lvl: False for lvl in LEVELS}

# =============== DeepSeek Function ===============
def deepseek_chat(messages, temperature=0.4, model="deepseek-chat"):
    if not client:
        raise RuntimeError("API key not found")
    resp = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
    return resp.choices[0].message.content

# =============== Build Question ===============
def build_one_local_q(item, vocab):
    correct = item[mean_key()]
    distractors = random.sample([v[mean_key()] for v in vocab if v != item], min(3, len(vocab)-1))
    opts = [correct] + distractors
    random.shuffle(opts)
    letters = ["A", "B", "C", "D"]
    return {
        "word": item["word"],
        "pinyin": item["pinyin"],
        "q": f"{item['word']} — {TXT['meaning_en'] if ui_en else TXT['meaning_th']}",
        "opts": list(zip(letters[:len(opts)], opts)),
        "correct": letters[opts.index(correct)],
        "explain": f"{item['word']} ({item['pinyin']}) → {correct}"
    }

# =============== Show Results (Show Answer Always) ===============
def show_results(level: str):
    qset = ss.quiz_map[level]
    answers = ss.answers_map[level]
    score = 0

    for i, q in enumerate(qset, start=1):
        opt_map = {k: v for k, v in q["opts"]}
        ans = answers.get(i)
        corr = q["correct"]
        corr_txt = opt_map.get(corr, "-")
        title = f"{q['word']} ({q['pinyin']})"

        if ans == corr:
            st.success(f"Q{i} ✅ {title} | Your answer: {ans}. {opt_map[ans]}")
            score += 1
        else:
            ans_txt = f"{ans}. {opt_map[ans]}" if ans in opt_map else "-"
            st.error(f"Q{i} ❌ {title} | Your answer: {ans_txt} | Correct: {corr}. {corr_txt}")

        st.caption(f"• Explanation: {q['explain']}")

    st.info(f"🏆 {t('score')}: {score}/{len(qset)}")

# =============== View Logic ===============
view = st.radio(t("mode_label"), ["lesson", "quiz"], format_func=lambda x: t("lesson_tab") if x=="lesson" else t("quiz_tab"))
ss.view = view
ss.level = st.radio(t("level_label"), LEVELS, index=LEVELS.index(ss.level))
level = ss.level
use_ai_quiz = st.toggle("Use AI (DeepSeek) to generate quiz", value=False)
if use_ai_quiz and not client:
    st.warning("DeepSeek API key not found (env: DEEPSEEK_API_KEY). Using local quiz logic.")

# =============== Lesson Mode ===============
if ss.view == "lesson":
    st.subheader(t("learn_header"))
    vocab = HSK_VOCAB[level]
    entry = vocab[ss.lesson_idx % len(vocab)]
    st.markdown(f"### {entry['word']}")
    st.write(f"• {t('pinyin')}: {entry['pinyin']}")
    st.write(f"• {t('meaning')}: {entry[mean_key()]}")

    c1, c2 = st.columns([1, 1])
    if c1.button(t("next"), use_container_width=True):
        ss.lesson_idx = (ss.lesson_idx + 1) % len(vocab)
    if c2.button(t("start_quiz"), use_container_width=True):
        ss.quiz_map[level] = [build_one_local_q(it, vocab) for it in random.sample(vocab, len(vocab))]
        ss.answers_map[level] = {}
        ss.submitted_map[level] = False
        ss.view = "quiz"
        st.rerun()

# =============== Quiz Mode ===============
else:
    qset = ss.quiz_map[level]
    c0, c1, c2, c3 = st.columns([1.3, 1, 1, 1.3])
    if c0.button(t("new_set"), use_container_width=True):
        vocab = HSK_VOCAB[level]
        ss.quiz_map[level] = [build_one_local_q(it, vocab) for it in random.sample(vocab, len(vocab))]
        ss.answers_map[level] = {}
        ss.submitted_map[level] = False
        st.rerun()
    if c3.button(t("back_lesson"), use_container_width=True):
        ss.view = "lesson"
        st.rerun()

    st.divider()
    if not qset:
        st.info("No quiz yet — click 'Start Quiz' in Lesson mode first.")
    else:
        for i, q in enumerate(qset, start=1):
            st.markdown(f"**Q{i}. {q['q']}**")
            labels = [f"{k}. {txt}" for k, txt in q["opts"]]
            picked = st.radio(f"Answer_{level}_{i}", labels, key=f"{level}_q{i}", disabled=ss.submitted_map[level])
            if picked:
                ss.answers_map[level][i] = picked.split(".")[0]

        if not ss.submitted_map[level] and st.button(t("submit"), type="primary"):
            ss.submitted_map[level] = True
            st.rerun()

        if ss.submitted_map[level]:
            st.divider()
            show_results(level)
