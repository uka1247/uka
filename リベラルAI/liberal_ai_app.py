import streamlit as st
import openai
import os
import re
import csv
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="リベラルAI", layout="centered")

st.markdown("<h1 style='text-align: center;'>🧠 リベラルAI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>あなたの意見に対して賛否を中立的に提示するAI</p>", unsafe_allow_html=True)

user_input = st.text_area("💬 あなたの意見をご自由に入力してください", height=150)

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

最後に、最近の社会的な文脈や報道、世論動向などを反映した、中立的な補足を3文だけ添えてください。
語り口は穏やかで、読者に考える余地を残すようにしてください。
補足の冒頭には「補足になりますが、」などの定型句は使ってもいいし、自然な語り出しをランダムにしてください。
"""}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )

        result = response.choices[0].message.content

        st.markdown("### 🔍 AIによる2つの視点と補足")

        agree_match = re.search(r"🔵 賛成の立場：\s*(.*?)(?:\n|🔴|$)", result, re.DOTALL)
        disagree_match = re.search(r"🔴 視点をずらした立場：\s*(.*?)(?:\n|$)", result, re.DOTALL)
        extra_match = re.split(r"🔴 視点をずらした立場：.*?\n", result, flags=re.DOTALL)

        if agree_match:
            st.markdown(f'<div style="border-left: 6px solid #51A3FF; padding-left: 1rem;"><strong>🔵 賛成の立場：</strong><br>{agree_match.group(1).strip()}</div>', unsafe_allow_html=True)

        if disagree_match:
            st.markdown(f'<div style="border-left: 6px solid #FF6B6B; padding-left: 1rem;"><strong>🔴 反対の立場：</strong><br>{disagree_match.group(1).strip()}</div>', unsafe_allow_html=True)

        if len(extra_match) > 1:
            st.markdown(f'<div style="border-left: 6px solid #BDC3C7; padding-left: 1rem; color: #4a4a4a;">{extra_match[1].strip()}</div>', unsafe_allow_html=True)

        if not (agree_match or disagree_match):
            st.warning("⚠️ 結果のフォーマットが想定と異なります。以下の内容をご確認ください。")
            st.text(result)

        # ✅ ログをCSVに保存（Streamlit Cloudでは消えるので実験用）
        log_path = "liberal_ai_log.csv"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(log_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if file.tell() == 0:
                    writer.writerow(["timestamp", "user_input", "agree", "disagree", "extra"])
                writer.writerow([
                    now,
                    user_input.strip(),
                    agree_match.group(1).strip() if agree_match else "",
                    disagree_match.group(1).strip() if disagree_match else "",
                    extra_match[1].strip() if len(extra_match) > 1 else ""
                ])
        except Exception as e:
            st.warning(f"⚠️ ログ保存に失敗しました: {e}")
