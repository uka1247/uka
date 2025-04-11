
import streamlit as st
from datetime import datetime
import re
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 設定
SHEET_ID = 'あなたのスプレッドシートID'
WORKSHEET_NAME = 'Sheet1'

# Google Sheets 認証
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(credentials)
worksheet = gc.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# Streamlit インターフェース
st.title("リベラルAI")

user_input = st.text_area("意見を入力してください")

if st.button("送信"):
    if user_input:
        # 意見抽出
        agree_match = re.search(r'【賛成】(.*?)【', user_input)
        disagree_match = re.search(r'【反対】(.*?)【', user_input)
        extra_match = re.findall(r'【.*?】(.*)', user_input)

        # 現在時刻の取得（修正箇所）
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # スプレッドシートに書き込み
        worksheet.append_row([
            now,
            user_input.strip(),
            agree_match.group(1).strip() if agree_match else "",
            disagree_match.group(1).strip() if disagree_match else "",
            extra_match[1].strip() if len(extra_match) > 1 else ""
        ])

        st.success("スプレッドシートに保存しました！")
    else:
        st.warning("テキストを入力してください。")
