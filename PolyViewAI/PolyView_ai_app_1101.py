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

# 🎥 背景動画を埋め込み
video_path = "20251101_1641_New Video_storyboard_01k8z5tmc8ewvbkcm4s8m6fhe9.mp4"

background_video_html = f"""
<video autoplay muted loop playsinline id="bgvideo" style="
  position: fixed;
  right: 0;
  bottom: 0;
  min-width: 100%;
  min-height: 100%;
  z-index: -1;
  object-fit: cover;
  opacity: 0.8;
">
  <source src="{video_path}" type="video/mp4">
</video>
"""
st.markdown(background_video_html, unsafe_allow_html=True)

# 💅 背景オーバーレイで文字を見やすく
st.markdown("""
<style>
[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed;
  inset: 0;
  background: rgba(255, 255, 255, 0.6); /* 半透明の白フィルター */
  z-index: -1;
}
body {
  font-family: 'Helvetica Neue', sans-serif;
}
.main-title {
  font-size: 2.5em;
  font-weight: bold;
  color: #2C3E50;
  margin-bottom: 0.2em;
}
.subtext {
  font-size: 1.1em;
  color: #7F8C8D;
  margin-bottom: 2em;
}
.box {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0px 4px 12px rgba(0,0,0,0.06);
  margin-top: 20px;
}
.agree { border-left: 6px solid #51A3FF; }
.disagree { border-left: 6px solid #FF6B6B; }
.extra {
  border-left: 6px solid #BDC3C7;
  font-style: normal;
  color: #4a4a4a;
}
.stTextArea textarea {
  background-color: #ffffff !important;
  border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown('<div class="main-title">🧠 PolyView AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">あなたの意見に対して賛否を中立的に提示する対話AI</div>', unsafe_allow_html=True)

# トピックカード
st.markdown("<div style='color:#7f8c8d; font-size:0.95em; margin-bottom:0.5em;'>🔎 最近の気になるワード</div>", unsafe_allow_html=True)
topics = [
    "ベーシックインカムは導入すべきだと思う？",
    "死刑制度は倫理に反してる？",
    "大学の無償化には賛成？反対？",
    "原発は必要だと思う？",
    "同性婚はあり？",
    "AIに規制は必要？",
    "選挙権年齢は18歳のままでいい？",
    "公共交通は無料にすべき？",
    "移民の受け入れ",
    "SNSでの発言に匿名性は必要か？",
    "マイナンバーカードの義務化に賛成？",
    "日本は防衛力を強化すべきか？",
    "コンビニの24時間営業は必要？",
    "給食の無償化は全国で実施した方がいい？",
    "週休3日制は導入すべき？",
    "選挙はオンライン投票を導入すべき？",
    "ジェンダー教育は義務教育に含めた方がいいのか",
    "カジノは合法化でOK？",
    "動物実験は倫理的に許される？",
    "最近のトランプ政権について",
    "消費税撤廃",
    "政治家の裏金問題",
    "マスコミによる情報統制は撤廃すべき？"
]
random_topics = random.sample(topics, 4)

cards_html = "<div style='display:flex;justify-content:center;gap:20px;flex-wrap:nowrap;'>"
for t in random_topics:
    cards_html += f"""
    <div onclick="navigator.clipboard.writeText('{t}')" style='
        width:200px;min-height:100px;padding:16px;background-color:white;
        border-radius:16px;box-shadow:0 2px 6px rgba(0,0,0,0.1);
        font-size:1em;text-align:center;display:flex;align-items:center;justify-content:center;
        line-height:1.4em;cursor:pointer;transition:0.2s;'
        onmouseover="this.style.backgroundColor='#f4f4f4'"
        onmouseout="this.style.backgroundColor='white'">{t}</div>"""
cards_html += "</div>"
components.html(cards_html, height=180)

# 入力欄
user_input = st.text_area("💬 あなたの意見をご自由に入力してください", height=150)

# 分析処理
if st.button("✨ 分析する") and user_input.strip() != "":
    with st.spinner("AIが分析中です..."):

        messages = [
            {"role": "system", "content": 
             "あなたはユーザーの意見に対して、賛成と反対の両方の視点を提示し、最後に中立的な補足を添えるAIです。"},
            {"role": "user", "content": f"""
以下はユーザーの意見です：
「{user_input}」

この意見に対して、以下の形式で出力してください：

🔵 賛成の立場：
（2〜7文）

🔴 視点をずらした立場：
（2〜7文）

最後に、最近の社会的文脈や報道を踏まえた中立的な補足を添えてください。
"""}
        ]

        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        result = response.choices[0].message.content

        # 出力整形
        agree_match = re.search(r"🔵 賛成の立場：\s*(.*?)(?=🔴|$)", result, re.DOTALL)
        disagree_match = re.search(r"🔴.*?立場：\s*(.*?)(?=\n\n|$)", result, re.DOTALL)
        extra_match = re.split(r"🔴.*?立場：.*?\n\n", result, flags=re.DOTALL)

        st.markdown("### 🔍 AIによる2つの視点と補足")
        if agree_match:
            st.markdown(f'<div class="box agree"><strong>🔵 賛成の立場：</strong><br>{agree_match.group(1).strip()}</div>', unsafe_allow_html=True)
        if disagree_match:
            st.markdown(f'<div class="box disagree"><strong>🔴 視点をずらした立場：</strong><br>{disagree_match.group(1).strip()}</div>', unsafe_allow_html=True)
        if len(extra_match) > 1:
            st.markdown(f'<div class="box extra">{extra_match[1].strip()}</div>', unsafe_allow_html=True)

        # ログ保存
        log_path = "liberal_ai_log.csv"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_exists = os.path.isfile(log_path)
        with open(log_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["timestamp", "user_input", "agree", "disagree", "extra"])
            writer.writerow([
                now,
                user_input.strip(),
                agree_match.group(1).strip() if agree_match else "",
                disagree_match.group(1).strip() if disagree_match else "",
                extra_match[1].strip() if len(extra_match) > 1 else ""
            ])

# フッター
st.markdown("---")
st.link_button("📮 アンケートにご協力ください", "https://docs.google.com/forms/d/e/1FAIpQLScrL1sMeQCvd0VSvC0c2SfmgS5ePKX6B1hTgjAEUKo3cGjTuQ/viewform")
