import streamlit as st
import random

# =============== Page Setup ===============
st.set_page_config(page_title="HanyuMate — HSK Vocab Trainer", page_icon="🎓", layout="centered")

# =============== UI Language Toggle (Thai/English for UI only) ===============
ui_en = st.toggle("Switch UI to English", value=False)  # False=Thai UI, True=English UI

TXT = {
    "title_th": "HanyuMate — สอนคำศัพท์จีน + พินอิน + แบบทดสอบ (HSK1–3)",
    "title_en": "HanyuMate — Chinese Vocab + Pinyin + Quiz (HSK1–3)",
    "mode_label_th": "โหมด",
    "mode_label_en": "Mode",
    "lesson_tab_th": "โหมดเรียนศัพท์",
    "lesson_tab_en": "Lesson",
    "quiz_tab_th": "โหมดแบบทดสอบ",
    "quiz_tab_en": "Quiz",
    "level_label_th": "เลือกระดับ HSK",
    "level_label_en": "Pick HSK level",
    "learn_header_th": "เรียนคำศัพท์ (จีน + พินอิน + ความหมาย)",
    "learn_header_en": "Learn Vocab (Chinese + Pinyin + Meaning)",
    "vocab_th": "คำศัพท์",
    "vocab_en": "Vocab",
    "pinyin_th": "พินอิน",
    "pinyin_en": "Pinyin",
    "meaning_th": "ความหมาย",
    "meaning_en": "Meaning",
    "next_th": "ถัดไป",
    "next_en": "Next",
    "start_quiz_th": "เริ่มทำแบบทดสอบจากระดับนี้",
    "start_quiz_en": "Start Quiz for this level",
    "no_vocab_th": "ยังไม่มีคลังคำศัพท์ของระดับนี้",
    "no_vocab_en": "No vocab entries for this level",
    "gen_quiz_smart_th": "เริ่มชุดใหม่ (เหลือ {rem} คำ; จะรีเซ็ตอัตโนมัติถ้าเหลือน้อยกว่า {n})",
    "gen_quiz_smart_en": "New set (remaining {rem}; auto-reset if less than {n})",
    "no_quiz_th": "ยังไม่มีชุดข้อสอบ — กดปุ่มด้านบนเพื่อเริ่มชุดใหม่",
    "no_quiz_en": "No quiz generated yet — click the button above to start",
    "submit_th": "ส่งคำตอบ",
    "submit_en": "Submit",
    "explain_th": "คำอธิบาย",
    "explain_en": "Explanation",
    "your_ans_th": "คำตอบของคุณ",
    "your_ans_en": "Your answer",
    "correct_th": "เฉลยที่ถูก",
    "correct_en": "Correct",
    "review_th": "ทบทวนคำศัพท์",
    "review_en": "Review",
    "score_th": "คะแนน",
    "score_en": "Score",
    "bank_info_th": "📦 คลังคำระดับ {lvl}: ทั้งหมด {tot} คำ • ยังไม่ถูกใช้ {rem} คำ • ชุดหนึ่งมี {n} ข้อ",
    "bank_info_en": "📦 {lvl} bank: total {tot} • unused {rem} • {n} questions per set",
    "auto_reset_note_th": "↺ เหลือคำไม่พอ จึงรีเซ็ตคลังสุ่มให้อัตโนมัติ",
    "auto_reset_note_en": "↺ Not enough unused items; auto-reset the pool",
}

def t(key, **kw):
    s = TXT[f"{key}_{'en' if ui_en else 'th'}"]
    return s.format(**kw) if kw else s

st.title(t("title"))

# =============== Vocab Bank (HSK1–3) ===============
HSK_VOCAB = {
    "HSK1": [
        {"word":"我", "pinyin":"wǒ", "meaning_th":"ฉัน/ผม", "meaning_en":"I; me"},
        {"word":"你", "pinyin":"nǐ", "meaning_th":"คุณ/เธอ", "meaning_en":"you"},
        {"word":"他", "pinyin":"tā", "meaning_th":"เขา (ผู้ชาย)", "meaning_en":"he"},
        {"word":"她", "pinyin":"tā", "meaning_th":"เธอ (ผู้หญิง)", "meaning_en":"she"},
        {"word":"我们", "pinyin":"wǒ men", "meaning_th":"พวกเรา", "meaning_en":"we; us"},
        {"word":"喜欢", "pinyin":"xǐ huan", "meaning_th":"ชอบ", "meaning_en":"to like"},
        {"word":"喝", "pinyin":"hē", "meaning_th":"ดื่ม", "meaning_en":"to drink"},
        {"word":"吃", "pinyin":"chī", "meaning_th":"กิน", "meaning_en":"to eat"},
        {"word":"看", "pinyin":"kàn", "meaning_th":"ดู/อ่าน", "meaning_en":"to watch/read"},
        {"word":"书", "pinyin":"shū", "meaning_th":"หนังสือ", "meaning_en":"book"},
        {"word":"天气", "pinyin":"tiān qì", "meaning_th":"สภาพอากาศ", "meaning_en":"weather"},
        {"word":"学校", "pinyin":"xué xiào", "meaning_th":"โรงเรียน", "meaning_en":"school"},
    ],
    "HSK2": [
        {"word":"颜色", "pinyin":"yán sè", "meaning_th":"สี", "meaning_en":"color"},
        {"word":"机场", "pinyin":"jī chǎng", "meaning_th":"สนามบิน", "meaning_en":"airport"},
        {"word":"旅游", "pinyin":"lǚ yóu", "meaning_th":"ท่องเที่ยว", "meaning_en":"to travel"},
        {"word":"鱼", "pinyin":"yú", "meaning_th":"ปลา", "meaning_en":"fish"},
        {"word":"牛奶", "pinyin":"niú nǎi", "meaning_th":"นมวัว", "meaning_en":"milk"},
        {"word":"地图", "pinyin":"dì tú", "meaning_th":"แผนที่", "meaning_en":"map"},
        {"word":"面条", "pinyin":"miàn tiáo", "meaning_th":"บะหมี่/ก๋วยเตี๋ยว", "meaning_en":"noodles"},
        {"word":"旁边", "pinyin":"páng biān", "meaning_th":"ข้างๆ", "meaning_en":"beside; nearby"},
        {"word":"准备", "pinyin":"zhǔn bèi", "meaning_th":"เตรียม", "meaning_en":"to prepare"},
        {"word":"帮助", "pinyin":"bāng zhù", "meaning_th":"ช่วยเหลือ", "meaning_en":"to help"},
        {"word":"眼睛", "pinyin":"yǎn jing", "meaning_th":"ดวงตา", "meaning_en":"eyes"},
        {"word":"面包", "pinyin":"miàn bāo", "meaning_th":"ขนมปัง", "meaning_en":"bread"},
    ],
    "HSK3": [
        {"word":"环境", "pinyin":"huán jìng", "meaning_th":"สิ่งแวดล้อม", "meaning_en":"environment"},
        {"word":"认真", "pinyin":"rèn zhēn", "meaning_th":"ตั้งใจ/จริงจัง", "meaning_en":"serious; earnest"},
        {"word":"解决", "pinyin":"jiě jué", "meaning_th":"แก้ปัญหา", "meaning_en":"to solve"},
        {"word":"盘子", "pinyin":"pán zi", "meaning_th":"จาน", "meaning_en":"plate"},
        {"word":"电梯", "pinyin":"diàn tī", "meaning_th":"ลิฟต์", "meaning_en":"elevator"},
        {"word":"变化", "pinyin":"biàn huà", "meaning_th":"การเปลี่ยนแปลง", "meaning_en":"change"},
        {"word":"提高", "pinyin":"tí gāo", "meaning_th":"ยกระดับ/พัฒนา", "meaning_en":"to improve"},
        {"word":"照顾", "pinyin":"zhào gù", "meaning_th":"ดูแล", "meaning_en":"to take care of"},
        {"word":"决定", "pinyin":"jué dìng", "meaning_th":"ตัดสินใจ", "meaning_en":"to decide"},
        {"word":"文化", "pinyin":"wén huà", "meaning_th":"วัฒนธรรม", "meaning_en":"culture"},
        {"word":"历史", "pinyin":"lì shǐ", "meaning_th":"ประวัติศาสตร์", "meaning_en":"history"},
        {"word":"锻炼", "pinyin":"duàn liàn", "meaning_th":"ออกกำลังกาย/ฝึกฝน", "meaning_en":"to exercise"},
    ],
}
LEVELS = ["HSK1", "HSK2", "HSK3"]
N_QUESTIONS = 6

# =============== Session State ===============
ss = st.session_state
ss.setdefault("level", "HSK1")
ss.setdefault("lesson_idx", 0)
ss.setdefault("used_ids", {lvl: set() for lvl in LEVELS})
ss.setdefault("quiz", [])
ss.setdefault("answers", {})
ss.setdefault("submitted", False)
ss.setdefault("active_view", "lesson")  # "lesson" / "quiz"

def mean_key(): 
    return "meaning_en" if ui_en else "meaning_th"

# =============== Helpers ===============
def pick_unique(level, n=N_QUESTIONS):
    bank = HSK_VOCAB[level]
    used = ss.used_ids[level]
    available = [i for i in range(len(bank)) if i not in used]
    if len(available) < n:
        return None
    chosen = random.sample(available, n)
    used.update(chosen)
    return chosen

def mcq_meaning(level, idx):
    bank = HSK_VOCAB[level]; item = bank[idx]
    correct = item[mean_key()]
    others = [i for i in range(len(bank)) if i != idx]
    distract = random.sample(others, 3)
    opts_text = [correct] + [bank[i][mean_key()] for i in distract]
    random.shuffle(opts_text)
    letters = ["A","B","C","D"]
    corr_letter = letters[opts_text.index(correct)]
    options = list(zip(letters, opts_text))
    explain = f"{item['word']} ({item['pinyin']}) → {item[mean_key()]}"
    return {"q": f"{item['word']} — {t('meaning')}", "opts": options, "correct": corr_letter,
            "explain": explain, "word": item['word'], "pinyin": item['pinyin']}

def mcq_pinyin(level, idx):
    bank = HSK_VOCAB[level]; item = bank[idx]
    correct = item["pinyin"]
    others = [i for i in range(len(bank)) if i != idx]
    distract = random.sample(others, 3)
    opts_text = [correct] + [bank[i]["pinyin"] for i in distract]
    random.shuffle(opts_text)
    letters = ["A","B","C","D"]
    corr_letter = letters[opts_text.index(correct)]
    options = list(zip(letters, opts_text))
    explain = f"{item['word']} → Pinyin: {item['pinyin']}"
    return {"q": f"{item['word']} — {t('pinyin')}", "opts": options, "correct": corr_letter,
            "explain": explain, "word": item['word'], "pinyin": item['pinyin']}

def gen_quiz(level, n=N_QUESTIONS):
    bank = HSK_VOCAB[level]
    used = ss.used_ids[level]
    remaining = max(0, len(bank) - len(used))
    if remaining < n:
        used.clear()
        st.caption(t("auto_reset_note"))
    chosen = pick_unique(level, n)
    if not chosen:
        chosen = random.sample(range(len(bank)), n)
    items = []
    for i, idx in enumerate(chosen):
        items.append(mcq_meaning(level, idx) if i % 2 == 0 else mcq_pinyin(level, idx))
    ss.quiz = items
    ss.answers = {}
    ss.submitted = False

def show_result():
    correct = 0
    for i, q in enumerate(ss.quiz, start=1):
        user = ss.answers.get(i)
        opt_map = {k: v for k, v in q["opts"]}
        if user == q["correct"]:
            st.success(f"Q{i} ✅ {q['word']} ({q['pinyin']}) | {t('your_ans')}: {user}. {opt_map[user]}")
            st.caption(f"• {t('explain')}: {q['explain']}")
            correct += 1
        else:
            st.error(f"Q{i} ❌ {q['word']} ({q['pinyin']}) | {t('your_ans')}: {user or '-'} "
                     f"| {t('correct')}: {q['correct']}. {opt_map[q['correct']]}")
            st.caption(f"• {t('explain')}: {q['explain']}  • {t('review')}: {opt_map[q['correct']]}")
    st.info(f"🏆 {t('score')}: {correct}/{len(ss.quiz)}")

# =============== Header: mode + level ===============
col1, col2 = st.columns([1,1])
with col1:
    view = st.radio(t("mode_label"), ["lesson", "quiz"],
                    format_func=lambda x: t("lesson_tab") if x == "lesson" else t("quiz_tab"),
                    horizontal=True, key="active_view")
with col2:
    ss.level = st.radio(t("level_label"), ["HSK1", "HSK2", "HSK3"], index=["HSK1","HSK2","HSK3"].index(ss.level),
                        horizontal=True)

# =============== Views ===============
if ss.active_view == "lesson":
    st.subheader(t("learn_header"))
    bank = HSK_VOCAB[ss.level]
    if not bank:
        st.warning(t("no_vocab"))
    else:
        i = ss.lesson_idx % len(bank)
        entry = bank[i]
        st.markdown(f"### {t('vocab')}: **{entry['word']}**")
        st.write(f"• {t('pinyin')}: {entry['pinyin']}")
        st.write(f"• {t('meaning')}: {entry[mean_key()]}")
        c1, c2 = st.columns(2)
        if c1.button(t("next"), use_container_width=True):
            ss.lesson_idx = (ss.lesson_idx + 1) % len(bank)
        if c2.button(t("start_quiz"), use_container_width=True):
            gen_quiz(ss.level, N_QUESTIONS)
            ss.active_view = "quiz"
            st.rerun()

else:
    bank = HSK_VOCAB[ss.level]
    used = ss.used_ids[ss.level]
    remaining = max(0, len(bank) - len(used))
    st.caption(t("bank_info", lvl=ss.level, tot=len(bank), rem=remaining, n=N_QUESTIONS))

    label = t("gen_quiz_smart", rem=remaining, n=N_QUESTIONS)
    if st.button(label, use_container_width=True):
        gen_quiz(ss.level, N_QUESTIONS)

    st.divider()
    if not ss.quiz:
        st.info(t("no_quiz"))
    else:
        for i, q in enumerate(ss.quiz, start=1):
            st.markdown(f"**Q{i}. {q['q']}**")
            labels = [f"{k}. {txt}" for k, txt in q["opts"]]
            picked = st.radio(f"Ans{i}", labels, key=f"q{i}", disabled=ss.submitted)
            ss.answers[i] = picked.split(".")[0]

        if not ss.submitted and st.button(t("submit"), type="primary", use_container_width=True):
            ss.submitted = True
            st.rerun()

        if ss.submitted:
            st.divider()
            show_result()
