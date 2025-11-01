import os
import random
import unicodedata
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# -------------------- SETUP --------------------
load_dotenv()

def get_client():
    base_url = os.getenv("LLM_BASE_URL", "").strip() or None
    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        st.error("❌ Missing API key")
        st.stop()
    return OpenAI(base_url=base_url, api_key=api_key)

# -------------------- LOAD DATA --------------------
@st.cache_data
def load_vocab():
    df = pd.read_csv("data/hsk_sample.csv")
    df["hsk_level"] = df["hsk_level"].astype(int)
    for c in ["hanzi","pinyin","thai","english"]:
        df[c] = df[c].astype(str).str.strip()
    return df

# -------------------- PROMPT TEMPLATE --------------------
PROMPT = """Role: You are a friendly Chinese tutor.
Instruction: Given a Chinese word and its pinyin, output:
1. Two short example sentences (Chinese + Pinyin + English + Thai).
2. One short memory tip about tone/meaning.
Constraints: Use only HSK1–3 vocabulary. Keep sentences short (CEFR A1–A2).
Output format:
Word: ...
Pinyin: ...
Meaning: ... (EN + TH)
Examples:
1. ...
2. ...
Memory Tip: ...
"""

def llm_generate(client, model, word, pinyin):
    messages = [
        {"role": "system", "content": "You are a helpful Chinese tutor."},
        {"role": "user", "content": f"{PROMPT}\n\nWord: {word}\nPinyin: {pinyin}"}
    ]
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=400,
    )
    return resp.choices[0].message.content

# -------------------- QUIZ FUNCTIONS --------------------
def normalize(s): return unicodedata.normalize("NFKC", s.strip().lower())

def init_state():
    st.session_state.setdefault("page", "Home")
    st.session_state.setdefault("level", 1)
    st.session_state.setdefault("quiz_active", False)
    st.session_state.setdefault("quiz_items", [])
    st.session_state.setdefault("answers", {})
    st.session_state.setdefault("quiz_pool", {})

def get_quiz_pool(df, level):
    pool = st.session_state["quiz_pool"].get(level, None)
    ids = df.index[df["hsk_level"] == level].tolist()
    if not pool or len(pool) < 5:
        st.session_state["quiz_pool"][level] = ids.copy()
        pool = ids.copy()
    return pool

def build_quiz(df, level, size=5):
    pool = get_quiz_pool(df, level)
    chosen = random.sample(pool, k=min(size, len(pool)))
    st.session_state["quiz_pool"][level] = [x for x in pool if x not in chosen]

    items = []
    for i in chosen:
        row = df.loc[i]
        correct = row["hanzi"]
        wrongs = df[df["hsk_level"] == level].sample(2)["hanzi"].tolist()
        options = [correct] + wrongs
        if random.random() < 0.1:
            options.append("ไม่มีตัวเลือกที่ถูกต้อง / None of the above")
            correct = None
        random.shuffle(options)
        items.append({
            "q": f"คำไหนตรงกับพินอิน: {row['pinyin']} (HSK{level})",
            "opts": options,
            "ans": correct,
            "ex": f"{row['hanzi']} ({row['pinyin']}) = {row['thai']} / {row['english']}"
        })
    return items

def grade_quiz(items, answers):
    score, res = 0, []
    for i, q in enumerate(items):
        choose = answers.get(i, None)
        correct = q["ans"]
        ok = (choose == correct) if correct else ("none of the above" in normalize(choose or ""))
        score += ok
        res.append((q["q"], choose, correct, ok, q["ex"]))
    return score, res

# -------------------- UI --------------------
def sidebar(df):
    st.sidebar.title("🔧 Settings")
    st.session_state["level"] = st.sidebar.selectbox("HSK Level", [1,2,3])
    if st.sidebar.button("🏠 Home"): st.session_state["page"] = "Home"
    if st.sidebar.button("📚 Lesson"): st.session_state["page"] = "Lesson"
    if st.sidebar.button("📝 Quiz"): st.session_state["page"] = "Quiz"

def page_home():
    st.title("🎓 HanyuMate — HSK1–3")
    st.write("สอนคำศัพท์จีน + พินอิน + แบบทดสอบไม่ซ้ำ พร้อมระบบตรวจอัตโนมัติ")

def page_lesson(df):
    st.header("📚 Lesson Mode")
    level = st.session_state["level"]
    row = df[df["hsk_level"] == level].sample(1).iloc[0]
    st.write(f"**{row['hanzi']}** ({row['pinyin']}) — {row['thai']} / {row['english']}")

    if st.button("✨ Generate Example", key="btn_gen"):
        try:
            client = get_client()
            result = llm_generate(client, os.getenv("LLM_MODEL"), row["hanzi"], row["pinyin"])
            st.success("✅ ตัวอย่างจาก AI")
            st.write(result)
        except Exception as e:
            st.error(e)

def page_quiz(df):
    st.header("📝 Quiz Mode")
    level = st.session_state["level"]

    if not st.session_state["quiz_active"]:
        if st.button("▶ Start Quiz"):
            st.session_state["quiz_items"] = build_quiz(df, level)
            st.session_state["answers"] = {}
            st.session_state["quiz_active"] = True
            st.rerun()
        return

    for i, q in enumerate(st.session_state["quiz_items"]):
        st.subheader(f"ข้อ {i+1}")
        st.write(q["q"])
        st.session_state["answers"][i] = st.radio(
            "เลือกคำตอบ", q["opts"], key=f"q_{i}_{level}", index=None
        )

    if st.button("✅ Submit"):
        score, res = grade_quiz(st.session_state["quiz_items"], st.session_state["answers"])
        st.success(f"คะแนน: {score}/{len(res)}")
        for q, choose, correct, ok, ex in res:
            st.write(f"**{q}**")
            st.write(f"- ตอบ: {choose}")
            st.write(f"- เฉลย: {correct or 'ไม่มีตัวเลือกที่ถูกต้อง'}")
            st.caption(f"{'✅ ถูกต้อง' if ok else '❌ ผิด'} | {ex}")
        st.session_state["quiz_active"] = False

# -------------------- MAIN --------------------
def main():
    st.set_page_config(page_title="HanyuMate", page_icon="🀄", layout="centered")
    init_state()
    df = load_vocab()
    sidebar(df)

    page = st.session_state["page"]
    if page == "Home": page_home()
    elif page == "Lesson": page_lesson(df)
    elif page == "Quiz": page_quiz(df)

if __name__ == "__main__":
    main()
