import streamlit as st
import random

# =============== Page Setup ===============
st.set_page_config(page_title="HanyuMate — HSK Vocabulary Trainer", page_icon="🎓", layout="centered")

# =============== UI Language Toggle ===============
ui_en = st.toggle("Switch UI to English", value=True)

# =============== Core Prompt Section (NEW) ===============
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

# =============== Text Labels ===============
TXT = {
    "title_en": "HanyuMate — Chinese Vocabulary + Pinyin + Quiz (HSK1–3)",
    "title_th": "HanyuMate — สอนคำศัพท์จีน + พินอิน + แบบทดสอบ (HSK1–3)",
    "mode_label_en": "Mode",
    "lesson_tab_en": "Lesson",
    "quiz_tab_en": "Quiz",
    "level_label_en": "Pick HSK level",
    "learn_header_en": "Learn Vocabulary (Chinese + Pinyin + Meaning)",
    "vocab_en": "Vocab",
    "pinyin_en": "Pinyin",
    "meaning_en": "Meaning",
    "next_en": "Next",
    "start_quiz_en": "Start Quiz for this level",
    "submit_en": "Submit",
    "explain_en": "Explanation",
    "your_ans_en": "Your answer",
    "correct_en": "Correct",
    "score_en": "Score",
    "review_en": "Review",
}

def t(key):
    return TXT[f"{key}_en"]

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
        {"word": "看", "pinyin": "kàn", "meaning_en": "to watch/read"},
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

# =============== Quiz Generator ===============
def generate_quiz(level):
    vocab = HSK_VOCAB[level]
    items = random.sample(vocab, N_QUESTIONS)
    quiz = []
    for i, item in enumerate(items):
        correct = item["meaning_en"]
        distractors = random.sample([v["meaning_en"] for v in vocab if v != item], 3)
        opts = [correct] + distractors
        random.shuffle(opts)
        letters = ["A", "B", "C", "D"]
        correct_letter = letters[opts.index(correct)]
        quiz.append({
            "q": f"{item['word']} — Meaning",
            "opts": list(zip(letters, opts)),
            "correct": correct_letter,
            "explain": f"{item['word']} ({item['pinyin']}) → {item['meaning_en']}"
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
    st.info(f"🏆 Score: {correct}/{len(ss.quiz)}")

# =============== Interface ===============
view = st.radio("Mode", ["lesson", "quiz"], format_func=lambda x: "Lesson" if x == "lesson" else "Quiz")
ss.level = st.radio("Pick HSK level", LEVELS, index=0)

if view == "lesson":
    st.subheader("Learn Vocabulary (Chinese + Pinyin + Meaning)")
    vocab = HSK_VOCAB[ss.level]
    entry = vocab[ss.lesson_idx % len(vocab)]
    st.markdown(f"### {entry['word']}")
    st.write(f"• Pinyin: {entry['pinyin']}")
    st.write(f"• Meaning: {entry['meaning_en']}")
    if st.button("Next"):
        ss.lesson_idx += 1
    if st.button("Start Quiz"):
        ss.quiz = generate_quiz(ss.level)
        ss.submitted = False
        st.rerun()

else:
    if not ss.quiz:
        st.warning("No quiz yet — start from the Lesson tab first.")
    else:
        for i, q in enumerate(ss.quiz, start=1):
            st.markdown(f"**Q{i}. {q['q']}**")
            choices = [f"{k}. {txt}" for k, txt in q["opts"]]
            picked = st.radio(f"Answer {i}", choices, key=f"q{i}", disabled=ss.submitted)
            ss.answers[i] = picked.split(".")[0]

        if not ss.submitted and st.button("Submit", type="primary"):
            ss.submitted = True
        if ss.submitted:
            st.divider()
            show_results()
