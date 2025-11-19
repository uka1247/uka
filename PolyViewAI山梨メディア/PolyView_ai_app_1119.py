import streamlit as st
import openai
import re
import random
import csv
import os
from datetime import datetime
import streamlit.components.v1 as components

# 🔑 OpenAI APIキー設定
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)


# 🌐 ページ設定
st.set_page_config(page_title="PolyView AI", layout="centered")

# ==============================
# 🌄 背景画像（bg.png）
# ==============================
image_path = "bg.png"

background_css = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: url("{image_path}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

[data-testid="stAppViewContainer"]::before {{
  content: "";
  position: fixed;
  inset: 0;
  background: rgba(255, 255, 255, 0.6);
  z-index: -1;
}}

body {{
  font-family: 'Helvetica Neue', sans-serif;
}}

.main-title {{
  font-size: 2.5em;
  font-weight: bold;
  color: #2C3E50;
  margin-bottom: 0.2em;
}}
.subtext {{
  font-size: 1.1em;
  color: #7F8C8D;
  margin-bottom: 2em;
}}

.box {{
  background-color: #ffffff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0px 4px 12px rgba(0,0,0,0.06);
  margin-top: 20px;
}}

.agree {{ border-left: 6px solid #51A3FF; }}
.disagree {{ border-left: 6px solid #FF6B6B; }}
.extra {{
  border-left: 6px solid #BDC3C7;
  color: #4a4a4a;
}}

.stTextArea textarea {{
  background-color: #ffffff !important;
  border-radius: 8px !important;
}}

.topic-caption {{
  color:#7f8c8d;
  font-size:0.95em;
  margin-bottom:0.5em;
}}
</style>
"""
st.markdown(background_css, unsafe_allow_html=True)

# ==============================
# ✔ キーワードカードの大きさを固定
# ==============================
button_css = """
<style>
div.stButton > button {
    width: 180px !important;
    height: 90px !important;
    white-space: normal !important;
    line-height: 1.2em;
    padding: 8px 10px;
    border-radius: 14px !important;
    font-size: 0.9em !important;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
}
</style>
"""
st.markdown(button_css, unsafe_allow_html=True)

# ==============================
# ✔ 分析ボタンを小さくする CSS（前回と同じサイズ）
# ==============================
if st.button("✨ 分析する"):
    ...


st.markdown(small_button_css, unsafe_allow_html=True)

# ==============================
# ヘッダー
# ==============================
st.markdown('<div class="main-title">PolyView AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">あなたの意見に対して賛否を中立的に提示する対話AI</div>', unsafe_allow_html=True)

# ==============================
# 40個のキーワード
# ==============================
topics = [
    # 既存23
    "ベーシックインカムは導入すべきだと思う？",
    "死刑制度は倫理に反してる？",
    "大学の無償化には賛成？反対？",
    "原発は必要だと思う？",
    "同性婚はあり？",
    "AIに規制は必要？",
    "選挙権年齢は18歳のままでいい？",
    "公共交通は無料にすべき？",
    "夫婦別姓案",
    "SNSでの発言に匿名性は必要か？",
    "マイナンバーカードの義務化に賛成？",
    "日本は防衛力を強化すべきか？",
    "コンビニの24時間営業は必要？",
    "給食の無償化は全国で実施した方がいい？",
    "週休3日制は導入すべき？",
    "選挙はオンライン投票を導入すべき？",
    "ジェンダー教育義務化について",
    "カジノ合法化はOK？",
    "動物実験は倫理的に許される？",
    "最近の日本政治について",
    "消費税撤廃",
    "政治家の裏金問題",
    "マスコミによる情報統制は撤廃すべき？",
    # 追加17
    "少子化対策はどこまで国が介入すべき？",
    "学校でスマホを全面禁止すべき？",
    "副業は全ての会社で解禁すべき？",
    "働き方の多様化はもっと進むべき？",
    "過疎地域の公共サービス維持は税金でどこまで支える？",
    "AI自動運転は全面解禁していい？",
    "インフルエンサー広告規制は必要？",
    "外食産業の値上げは受け入れるべき？",
    "日本の難民受け入れは拡大すべき？",
    "防犯カメラ増設はプライバシー侵害？",
    "食品ロス罰則は必要？",
    "ペット生体販売は禁止すべき？",
    "高齢者の運転免許更新はもっと厳しくすべき？",
    "生成AIを学校教育にどこまで導入する？",
    "災害時SNS情報は規制すべき？",
    "電車内マナーは罰金制にすべき？",
    "観光地のオーバーツーリズムは規制すべき？"
]

random_topics = random.sample(topics, 4)

if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = ""

# ==============================
# キーワードカード（ボタン固定サイズ）
# ==============================
st.markdown('<div class="topic-caption">🔎 最近の気になるワード</div>', unsafe_allow_html=True)

cols = st.columns(4)
for i, t in enumerate(random_topics):
    with cols[i]:
        if st.button(t, key=f"topic_{i}"):
            st.session_state.selected_topic = t

# ==============================
# 入力欄（プレースホルダーにキーワード反映）
# ==============================
user_input = st.text_area(
    "💬 あなたの意見をご自由に入力してください",
    height=150,
    placeholder=st.session_state.get("selected_topic", "")
)

# ==============================
# AI 分析
# ==============================
if st.button("✨ 分析する") and user_input.strip():
    with st.spinner("AIが分析中です..."):

        messages = [
            {
                "role": "system",
                "content": (
                    "ユーザーの意見に対して賛成・反対の両方の視点を提示し、"
                    "最後に中立的な補足を添えるAIです。"
                )
            },
            {
                "role": "user",
                "content": f"""
以下はユーザーの意見です：
「{user_input}」

🔵 賛成の立場：
（2〜7文）

🔴 視点をずらした立場：
（2〜7文）

最後に最近の社会背景を踏まえた中立的補足を書いてください。
"""
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        result = response.choices[0].message.content

        # 解析
        agree = re.search(r"🔵.*?立場：\s*(.*?)(?=🔴|$)", result, re.DOTALL)
        disagree = re.search(r"🔴.*?立場：\s*(.*)", result, re.DOTALL)

        st.markdown("### 🔍 AIによる2つの視点と補足")

        if agree:
            st.markdown(
                f'<div class="box agree"><strong>🔵 賛成の立場：</strong><br>{agree.group(1).strip()}</div>',
                unsafe_allow_html=True
            )

        if disagree:
            parts = disagree.group(1).strip().split("\n\n", 1)
            disagree_text = parts[0]
            extra_text = parts[1] if len(parts) > 1 else ""

            st.markdown(
                f'<div class="box disagree"><strong>🔴 視点をずらした立場：</strong><br>{disagree_text}</div>',
                unsafe_allow_html=True
            )

            if extra_text:
                st.markdown(f'<div class="box extra">{extra_text}</div>', unsafe_allow_html=True)

        # ログ保存
        log_path = "liberal_ai_log.csv"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_exists = os.path.isfile(log_path)

        with open(log_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["timestamp", "user_input", "agree", "disagree", "extra"])
            writer.writerow([
                now,
                user_input.strip(),
                agree.group(1).strip() if agree else "",
                disagree_text,
                extra_text
            ])
