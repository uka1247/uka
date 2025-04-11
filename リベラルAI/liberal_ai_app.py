
import streamlit as st
import openai
import re
import random
import csv
import os
from datetime import datetime
import streamlit.components.v1 as components
import gspread
from google.oauth2 import service_account

# 🔑 OpenAI APIキーを設定（環境変数から）
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

# 🌐 ページ設定
st.set_page_config(page_title="リベラルAI", layout="centered")

# 💅 カスタムCSSでおしゃれに
st.markdown("""
    <style>
        body {
            background-color: #f9f9f9;
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
        .agree {
            border-left: 6px solid #51A3FF;
        }
        .disagree {
            border-left: 6px solid #FF6B6B;
        }
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
st.markdown('<div class="main-title">🧠 リベラルAI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">あなたの意見に対して賛否を中立的に提示する対話AI</div>', unsafe_allow_html=True)

# トピック例の表示
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
    "マスコミによる情報統制は撤廃すべき？",
    "動物実験は倫理的に許される？"
]

random_topics = random.sample(topics, 4)

cards_html = "<div style='display: flex; justify-content: center; gap: 20px; flex-wrap: nowrap;'>"
for t in random_topics:
    cards_html += f"""
    <div onclick="navigator.clipboard.writeText('{t}')" style='
        width: 200px;
        min-height: 100px;
        padding: 16px;
        background-color: white;
        border-radius: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        font-size: 1em;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.4em;
        cursor: pointer;
        transition: 0.2s;
    ' onmouseover="this.style.backgroundColor='#f4f4f4'" onmouseout="this.style.backgroundColor='white'">
        {t}
    </div>
    """
cards_html += "</div>"
components.html(cards_html, height=180)

# 入力欄
user_input = st.text_area("💬 あなたの意見をご自由に入力してください", height=150)

# 分析実行
if st.button("✨ 分析する") and user_input.strip() != "":
    with st.spinner("AIが分析中です..."):

        messages = [
            {"role": "system", "content": "あなたはユーザーの意見に対して、賛成と反対の両方の視点を提示し、最後に中立的かつ時事的な補足を添えるAIです。"},
            {"role": "user", "content": f"""
以下はユーザーの意見です：
「{user_input}」

この意見に対して、以下の形式で出力してください：

🔵 賛成の立場：
簡潔に賛成意見を2〜7文で述べてください。

🔴 視点をずらした立場：
簡潔に反対意見を2〜7文で述べてください。

最後に、最近の社会的な文脈や報道、世論動向などを反映した、中立的な補足を2~5文だけ添えてください。
語り口は穏やかで、読者に考える余地を残すようにしてください。
補足の冒頭には「補足になりますが、」などの定型句は使わず、自然な語り出しにしてください。
"""}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        result = response.choices[0].message.content

        # 出力の分解（正規表現）
        st.markdown("### 🔍 AIによる2つの視点と補足")

        agree_match = re.search(r"🔵 賛成の立場：\s*(.*?)(?=🔴|$)", result, re.DOTALL)
        disagree_match = re.search(r"🔴.*?立場：\s*(.*?)(?=\n\n|$)", result, re.DOTALL)
        extra_match = re.split(r"🔴.*?立場：.*?\n\n", result, flags=re.DOTALL)

        if agree_match:
            st.markdown(f'<div class="box agree"><strong>🔵 賛成の立場：</strong><br>{agree_match.group(1).strip()}</div>', unsafe_allow_html=True)

        if disagree_match:
            st.markdown(f'<div class="box disagree"><strong>🔴 反対の立場：</strong><br>{disagree_match.group(1).strip()}</div>', unsafe_allow_html=True)

        if len(extra_match) > 1:
            st.markdown(f'<div class="box extra">{extra_match[1].strip()}</div>', unsafe_allow_html=True)

        if not (agree_match or disagree_match):
            st.warning("⚠️ 結果のフォーマットが想定と異なります。以下の内容をご確認ください。")
            st.text(result)


       

# Google Sheets の設定
SHEET_ID = "1wheYg5RCqy6iSeujXUPQbOZWAjSx_BRTpFRK5rOrUTo"
WORKSHEET_NAME = "ログ"  # シート名が "ログ" であることを確認

# 認証してスプレッドシートにアクセス
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(credentials)
worksheet = gc.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# 所要時間の計測(例として処理前後で time を使う)
import time
start_time = time.time()

# ... ここで OpenAI API 処理などを実施 ...

end_time = time.time()
elapsed_time = round(end_time - start_time, 2)

# スプレッドシートに追記
worksheet.append_row([
    now,
    user_input.strip(),
    agree_match.group(1).strip() if agree_match else "",
    disagree_match.group(1).strip() if disagree_match else "",
    extra_match[1].strip() if len(extra_match) > 1 else "",
    f"{elapsed_time}秒"
])
