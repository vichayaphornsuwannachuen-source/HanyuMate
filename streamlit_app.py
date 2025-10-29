import os, json, streamlit as st
from typing import List, Dict, Any

st.set_page_config(page_title="HanyuMate — AI Chinese Quiz & Tutor", page_icon="🎓", layout="centered")
st.title("HanyuMate — AI Chinese Quiz & Tutor")
st.caption("Paste notes ➜ Generate 5 MCQs ➜ Answer ➜ Grade with feedback (ZH + pinyin + EN)")

if "questions" not in st.session_state:
    st.session_state.questions = []

def generate_quiz():
    # ตัวอย่างคำถามจำลอง (offline demo)
    return [
        {"id":1,"question_zh":"他___学生。","options":["A 是","B 在","C 有","D 做"],"answer":"A",
         "explain_en":"Use 是 for identity.","explain_pinyin":"tā shì xuéshēng"},
        {"id":2,"question_zh":"“谢谢” 的拼音是？","options":["A xièxie","B xiéxie","C xìexie","D xièxiè"],"answer":"A",
         "explain_en":"Tone 4 + light tone.","explain_pinyin":"xièxie"},
        {"id":3,"question_zh":"今天天气很__。","options":["A 好","B 吗","C 呢","D 的"],"answer":"A",
         "explain_en":"Adjective complement.","explain_pinyin":"hǎo"},
        {"id":4,"question_zh":"我想___咖啡。","options":["A 喝","B 吃","C 看","D 来"],"answer":"A",
         "explain_en":"Verb-object collocation.","explain_pinyin":"hē kāfēi"},
        {"id":5,"question_zh":"“我们”的英文是？","options":["A we","B you","C they","D he"],"answer":"A",
         "explain_en":"Pronoun mapping.","explain_pinyin":"wǒmen"},
    ]

notes = st.text_area("Paste lecture notes / vocab list / short text (ZH/EN/TH):",
                     placeholder="例如: 我是学生。谢谢！今天天气很好。喝咖啡。‘我们’")

if st.button("Generate Quiz"):
    st.session_state.questions = generate_quiz()

if st.session_state.questions:
    st.subheader("Quiz (5 MCQs)")
    answers = {}
    for q in st.session_state.questions:
        selected = st.radio(f"Q{q['id']}: {q['question_zh']}",
                            options=["A","B","C","D"], key=f"sel_{q['id']}", horizontal=True)
        answers[q["id"]] = selected

    if st.button("Grade"):
        correct = 0
        for q in st.session_state.questions:
            sel = answers[q["id"]]
            ok = sel == q["answer"]
            if ok: correct += 1
            st.write(f"Q{q['id']} — Your answer: {sel} | Correct: {q['answer']}")
            st.write(f"Feedback: {q['explain_en']} | Pinyin: {q['explain_pinyin']}")
        st.success(f"Score: {correct}/5")
        st.caption("Note: Offline demo mode (no API).")
