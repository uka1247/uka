import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="リベラルAI", layout="centered")

st.title("🧠 リベラルAI")
st.write("あなたの意見に対して、AIが賛否と補足を提示します。")

# セッションログ初期化
if "logs" not in st.session_state:
    st.session_state["logs"] = []

# ユーザー入力
user_input = st.text_area("💬 あなたの意見を入力してください")

# ✅ ログ一覧チェック（常に上部に表示）
if st.session_state["logs"]:
    st.markdown("#### 🛠 開発者用ツール")
    if st.checkbox("🕵️ ログ一覧を表示する（クリックで展開）"):
        df = pd.DataFrame(st.session_state["logs"])
        st.dataframe(df)

# 分析ボタン
if st.button("✨ 分析する") and user_input.strip():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 簡易AI応答（ここに OpenAI 呼び出しが入る予定）
    agree = "再生可能エネルギーは持続可能な社会を実現する鍵です。"
    disagree = "技術的・経済的に再生可能エネルギーへの全面転換は課題が多いです。"
    extra = "近年では日本政府もGX（グリーントランスフォーメーション）を掲げて議論が進んでいます。"

    st.markdown("### 🔍 AIによる分析結果")
    st.success(f"🔵 賛成の立場：{agree}")
    st.error(f"🔴 反対の立場：{disagree}")
    st.info(f"{extra}")

    # ✅ セッションログへ保存
    st.session_state["logs"].append({
        "timestamp": now,
        "user_input": user_input.strip(),
        "agree": agree,
        "disagree": disagree,
        "extra": extra
    })

# ✅ ダウンロードボタン（ログCSV）
if st.session_state["logs"]:
    df = pd.DataFrame(st.session_state["logs"])
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 ログをCSVでダウンロード", data=csv, file_name="liberal_ai_log.csv", mime="text/csv")