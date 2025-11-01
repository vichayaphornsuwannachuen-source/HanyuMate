# streamlit_app.py
import os
import json
import random
import requests
import streamlit as st

# =============== Page Setup ===============
st.set_page_config(page_title="HanyuMate — HSK Vocabulary Trainer", page_icon="🎓", layout="centered")

# =============== Core Prompt (visible to show instructor) ===============
PROMPT_EN = """
Role:
You are a friendly Chinese language tutor who helps university students learn vocabulary and pronunciation.

Instruction:
When given a Chinese word and its pinyin, generate the following:
1) Show the word (Chinese), its pinyin, and Thai–English meanings.
2) Create a short multiple-choice quiz (3–4 options) that tests the meaning of this word.
3) Provide the correct answer clearly at the end.

Constraints:
- Use vocabulary only from HSK1–3 levels.
- Keep everything short and simple (CEFR A1–A2).
- Make sure the options are realistic and non-repetitive.
"""

with st.expander("🧠 Core Prompt (for future LLM connection) — Click to view"):
    st.code(PROMPT_EN, language="text")

# =============== UI Labels (English UI for presentation) ===============
TXT = {
    "title": "HanyuMate — Chinese Vocabulary + Pinyin + Quiz (HSK1–3)",
    "mode_label": "Mode",
    "lesson_tab": "Lesson",
    "quiz_tab": "Quiz",
    "level_label": "Pick HSK level",
    "learn_header": "Learn Vocabulary (Chinese + Pinyin + Meaning)",
    "vocab": "Vocab",
    "pinyin": "Pinyin",
    "meaning": "Meaning",
    "next": "Next",
    "start_quiz": "Start Quiz for this level",
    "submit": "Submit",
    "explain": "Explanation",
    "your_ans": "Your answer",
    "correct": "Correct",
    "score": "Score",
    "review": "Review",
}
def t(k): return TXT[k]

st.title(t("title"))

# =============== Vocabulary Bank (HSK1–3) ===============
HSK_VOCAB = {
    "HSK1": [
        {"word": "我", "pinyin": "wǒ", "meaning_en": "I; me"},
        {"word": "你", "pinyin": "nǐ", "meaning_en": "you"},
        {"word": "他", "pinyin": "tā", "meaning_en": "he"},
        {"word": "她", "pinyin": "tā", "meaning_en": "she"},
        {"word": "我们", "pinyin": "wǒ men", "meaning_en": "we; us"},
        {"word": "喜欢", "pinyin": "xǐ huan", "meaning_en": "to like"},
        {"word": "喝", "pinyin": "hē", "meaning_en": "to drink"},
        {"word": "吃", "pinyin": "chī", "meaning_en": "to eat"},
        {"word": "看", "pinyin": "kàn", "meaning_en": "to watch / read"},
        {"word": "书", "pinyin": "shū", "meaning_en": "book"},
    ],
    "HSK2": [
        {"word": "颜色", "pinyin": "yán sè", "meaning_en": "color"},
        {"word": "机场", "pinyin": "jī chǎng", "meaning_en": "airport"},
        {"word": "旅游", "pinyin": "lǚ yóu", "meaning_en": "to travel"},
        {"word": "鱼", "pinyin": "yú", "meaning_en": "fish"},
        {"word": "牛奶", "pinyin": "niú nǎi", "meaning_en": "milk"},
    ],
    "HSK3": [
        {"word": "环境", "pinyin": "huán jìng", "meaning_en": "environment"},
        {"word": "认真", "pinyin": "rèn zhēn", "meaning_en": "serious; earnest"},
        {"word": "解决", "pinyin": "jiě jué", "meaning_en": "to solve"},
        {"word": "盘子", "pinyin": "pán zi", "meaning_en": "plate"},
        {"word": "电梯", "pinyin": "diàn tī", "meaning_en": "elevator"},
    ]
}
LEVELS = ["HSK1", "HSK2", "HSK3"]
N_QUESTIONS = 5

# =============== Session State ===============
ss = st.session_state
if "level" not in ss: ss.level = "HSK1"
if "lesson_idx" not in ss: ss.lesson_idx = 0
if "quiz" not in ss: ss.quiz = []
if "answers" not in ss: ss.answers = {}
if "submitted" not in ss: ss.submitted = False
if "use_ai" not in ss: ss.use_ai = False  # Toggle for DeepSeek

# =============== Optional AI (DeepSeek) ===============
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = "deepseek-chat"  # or "deepseek-reasoner"

def call_deepseek_generate(word: str, pinyin: str, level: str, meanings_pool_en: list):
    """
    Ask DeepSeek to build 1 MCQ for the word.
    returns: {q, opts(list[(letter,text)]), correct(letter), explain}
    """
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
    data = json.loads(content)  # enforce JSON
    letters = ["A", "B", "C", "D"]
    opts = [(k, data["options"][k]) for k in letters]
    return {
        "q": data["question"],
        "opts": opts,
        "correct": data["correct"].strip().upper(),
        "explain": data.get("explain", f"{word} ({pinyin})")
    }

# =============== Quiz Generator (AI toggle + fallback) ===============
def generate_quiz(level: str, use_ai: bool):
    vocab = HSK_VOCAB[level]
    items = random.sample(vocab, N_QUESTIONS)

    # Use DeepSeek if toggled on and key available
    if use_ai and DEEPSEEK_API_KEY:
        meanings_pool = [v["meaning_en"] for v in vocab]
        quiz = []
        for item in items:
            try:
                q = call_deepseek_generate(item["word"], item["pinyin"], level, meanings_pool)
            except Exception:
                # Fallback to local logic on any API error
                correct = item["meaning_en"]
                distractors = random.sample([v["meaning_en"] for v in vocab if v != item], 3)
                opts = [correct] + distractors
                random.shuffle(opts)
                letters = ["A","B","C","D"]
                q = {
                    "q": f"{item['word']} — Meaning",
                    "opts": list(zip(letters, opts)),
                    "correct": letters[opts.index(correct)],
                    "explain": f"{item['word']} ({item['pinyin']}) → {correct}"
                }
            quiz.append(q)
        return quiz

    # Local (non-AI) logic
    quiz = []
    for item in items:
        correct = item["meaning_en"]
        distractors = random.sample([v["meaning_en"] for v in vocab if v != item], 3)
        opts = [correct] + distractors
        random.shuffle(opts)
        letters = ["A", "B", "C", "D"]
        quiz.append({
            "q": f"{item['word']} — Meaning",
            "opts": list(zip(letters, opts)),
            "correct": letters[opts.index(correct)],
            "explain": f"{item['word']} ({item['pinyin']}) → {correct}"
        })
    return quiz

def show_results():
    correct = 0
    for i, q in enumerate(ss.quiz, start=1):
        ans = ss.answers.get(i)
        opt_map = {k: v for k, v in q["opts"]}
        if ans == q["correct"]:
            st.success(f"Q{i} ✅ {q['explain']}")
            correct += 1
        else:
            st.error(f"Q{i} ❌ Your answer: {ans or '-'} | Correct: {q['correct']} ({opt_map[q['correct']]})")
    st.info(f"🏆 {t('score')}: {correct}/{len(ss.quiz)}")

# =============== Controls ===============
view = st.radio(t("mode_label"), ["lesson", "quiz"], format_func=lambda x: t("lesson_tab") if x == "lesson" else t("quiz_tab"))
ss.level = st.radio(t("level_label"), LEVELS, index=0)
ss.use_ai = st.toggle("Use AI (DeepSeek) to generate quiz", value=ss.use_ai, help="If off, uses built-in logic.")
if ss.use_ai and not DEEPSEEK_API_KEY:
    st.warning("DeepSeek API key not found. Set environment variable DEEPSEEK_API_KEY or turn off the AI toggle.")

# =============== Views ===============
if view == "lesson":
    st.subheader(t("learn_header"))
    vocab = HSK_VOCAB[ss.level]
    entry = vocab[ss.lesson_idx % len(vocab)]
    st.markdown(f"### {entry['word']}")
    st.write(f"• {t('pinyin')}: {entry['pinyin']}")
    st.write(f"• {t('meaning')}: {entry['meaning_en']}")
    c1, c2 = st.columns(2)
    if c1.button(t("next"), use_container_width=True):
        ss.lesson_idx += 1
    if c2.button(t("start_quiz"), use_container_width=True):
        ss.quiz = generate_quiz(ss.level, ss.use_ai)
        ss.submitted = False
        st.rerun()

else:
    if not ss.quiz:
        st.info("No quiz yet — click Start Quiz from the Lesson tab.")
    else:
        for i, q in enumerate(ss.quiz, start=1):
            st.markdown(f"**Q{i}. {q['q']}**")
            labels = [f"{k}. {txt}" for k, txt in q["opts"]]
            picked = st.radio(f"Answer {i}", labels, key=f"q{i}", disabled=ss.submitted)
            ss.answers[i] = picked.split(".")[0] if picked else None

        colA, colB = st.columns([1,1])
        if not ss.submitted and colA.button(t("submit"), type="primary", use_container_width=True):
            ss.submitted = True
        if ss.submitted:
            st.divider()
            show_results()
