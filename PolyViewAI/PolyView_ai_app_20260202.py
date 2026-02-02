
import streamlit as st
import openai
import re
import random
import csv
import os
from datetime import datetime
import streamlit.components.v1 as components

# 🔑 OpenAI APIキーを設定（環境変数から）
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

# 🌐 ページ設定
st.set_page_config(page_title="PolyView AI", layout="centered")

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


# =========================
# ヘッダー
# =========================
st.markdown('<div class="main-title">🧠 PolyView AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">賛否を提示し、補足はエビデンス（参考情報源）を明示します</div>', unsafe_allow_html=True)

# =========================
# トピック例（クリックでコピー）
# =========================
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
]
random_topics = random.sample(topics, 4)

cards_html = "<div style='display:flex; justify-content:center; gap:20px; flex-wrap:nowrap;'>"
for t in random_topics:
    safe_t = t.replace("'", "\\'")
    cards_html += f"""
    <div onclick="navigator.clipboard.writeText('{safe_t}')" style='
        width: 200px; min-height: 100px; padding: 16px;
        background-color: white; border-radius: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        font-size: 1em; text-align: center;
        display: flex; align-items: center; justify-content: center;
        line-height: 1.4em; cursor: pointer; transition: 0.2s;
    ' onmouseover="this.style.backgroundColor='#f4f4f4'" onmouseout="this.style.backgroundColor='white'">
        {t}
    </div>
    """
cards_html += "</div>"
components.html(cards_html, height=180)

# =========================
# Utility
# =========================
def _get(obj, key, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def parse_agree_disagree(text: str):
    agree_match = re.search(r"🔵\s*賛成の立場：\s*(.*?)(?=🔴|$)", text, re.DOTALL)
    disagree_match = re.search(r"🔴\s*視点をずらした立場：\s*(.*?)(?=$)", text, re.DOTALL)
    agree = agree_match.group(1).strip() if agree_match else ""
    disagree = disagree_match.group(1).strip() if disagree_match else ""
    return agree, disagree

def extract_url_citations(resp):
    """
    Responses APIの戻りから url_citation（title/url）を抽出
    """
    cits = []
    output = _get(resp, "output", []) or []
    for item in output:
        if _get(item, "type") != "message":
            continue
        contents = _get(item, "content", []) or []
        for part in contents:
            if _get(part, "type") != "output_text":
                continue
            annotations = _get(part, "annotations", []) or []
            for ann in annotations:
                if _get(ann, "type") == "url_citation":
                    url = _get(ann, "url", "") or ""
                    title = _get(ann, "title", "") or "(no title)"
                    if url:
                        cits.append({"title": title, "url": url})

    # URLで重複排除
    seen = set()
    uniq = []
    for c in cits:
        if c["url"] not in seen:
            uniq.append(c)
            seen.add(c["url"])
    return uniq

def clean_extra_text(text: str) -> str:
    """
    補足枠内からリンクを消す＆「参考情報源」などの余計な部分をカット
    - Markdownリンク [text](url) -> text
    - 生URL https://... を除去
    - 「参考情報源/References/Sources」見出し以降をカット
    """
    if not text:
        return ""

    # 見出しっぽい語が出たら以降をカット
    text = re.sub(r"\n\s*(参考情報源|References|Sources).*", "", text, flags=re.IGNORECASE | re.DOTALL)

    # Markdownリンクを文字だけに
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r"\1", text)

    # 生URLを除去
    text = re.sub(r"https?://\S+", "", text)

    # 余白整形
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text

def to_safe_html(text: str) -> str:
    """
    HTML表示用：エスケープ＋改行を<br>に変換（リンク化させない）
    """
    safe = html_lib.escape(text or "")
    return safe.replace("\n", "<br>")

# =========================
# 入力欄
# =========================
user_input = st.text_area("💬 あなたの意見をご自由に入力してください", height=150)

# =========================
# 実行
# =========================
if st.button("✨ 分析する") and user_input.strip():
    with st.spinner("AIが分析中です..."):

        # ここでも毎回初期化（さらに安全）
        citations = []
        extra_text_display = ""

        # -------------------------
        # 1) 🔵🔴（通常生成：Web検索なし）
        # -------------------------
        system_main = (
            "あなたはユーザーの意見に対して、賛成と反対（視点ずらし）の両方の視点を提示するAIです。"
            "反対意見は多様な立場の一例を示すこと。極端な否定や扇情的な表現は避け、論理的で建設的に。"
            "ここでは補足は書かないでください。"
        )

        user_main = f"""
以下はユーザーの意見です：
「{user_input}」

この意見に対して、以下の形式で“必ず”出力してください（補足は出力しない）：

🔵 賛成の立場：
簡潔に賛成意見を2〜7文で述べてください。

🔴 視点をずらした立場：
簡潔に反対意見を2〜7文で述べてください。反対意見は多様な立場の一例を示すこと。極端な否定や扇情的な表現は避け、論理的で建設的に提示してください。
"""

        try:
            main_resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_main},
                    {"role": "user", "content": user_main},
                ],
            )
            main_text = main_resp.choices[0].message.content or ""
        except Exception:
            main_text = ""

        agree_text, disagree_text = parse_agree_disagree(main_text)

        # -------------------------
        # 2) 補足（Web検索あり）
        # -------------------------
        prefixes = [
            "補足になりますが、",
            "ちなみに、",
            "念のため付け加えると、",
            "ここで一つだけ補足すると、",
            "話題を広げる意味で補足すると、",
        ]
        chosen_prefix = random.choice(prefixes)

        extra_prompt = f"""
以下はユーザーの意見です：
「{user_input}」

この意見に関連する最近の社会的文脈・報道・統計・政策などの情報を踏まえつつ、
中立的な「補足」を2〜5文で作成してください。

制約：
- 冒頭は必ず「{chosen_prefix}」で始める
- 語り口は穏やかで、読者に考える余地を残す
- 断定しすぎず、必要に応じて「〜とされる」「〜との指摘がある」などで調整する
- 極端に扇情的な言い回しは避ける
- “補足文のみ”を出力（参考情報源・URL・箇条書き・見出しは出力しない）
"""

        extra_text_raw = ""
        try:
            extra_resp = client.responses.create(
                model="gpt-4o",
                input=extra_prompt,
                tools=[{"type": "web_search"}],
                include=["web_search_call.action.sources"],
            )
            extra_text_raw = (getattr(extra_resp, "output_text", "") or "").strip()
            citations = extract_url_citations(extra_resp) or []
        except Exception:
            extra_text_raw = "補足の生成時にエラーが発生しました。時間をおいて再実行してください。"
            citations = []

        # ✅ 補足枠内リンク除去（表示用）
        extra_text_display = clean_extra_text(extra_text_raw)

        # =========================
        # 表示（HTMLエスケープでリンク化も封じる）
        # =========================
        st.markdown("### 🔍 AIによる2つの視点と補足")

        if agree_text:
            st.markdown(
                f'<div class="box agree"><strong>🔵 賛成の立場：</strong><br>{to_safe_html(agree_text)}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 賛成の立場の抽出に失敗しました。")

        if disagree_text:
            st.markdown(
                f'<div class="box disagree"><strong>🔴 視点をずらした立場：</strong><br>{to_safe_html(disagree_text)}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 視点をずらした立場の抽出に失敗しました。")

        if extra_text_display:
            # ✅ 補足枠はリンク無し（テキストのみ）
            st.markdown(
                f'<div class="box extra">{to_safe_html(extra_text_display)}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 補足の生成に失敗しました。")

        # ✅ 参考情報源（ここだけで表示）
        if citations:
            st.markdown("#### 参考情報源（補足で参照）")
            for i, c in enumerate(citations, 1):
                title = (c.get("title") or "(no title)").strip()
                url = (c.get("url") or "").strip()
                if url:
                    st.markdown(f"{i}. [{title}]({url})")
        else:
            st.caption("（今回の補足では、参照URLが取得できませんでした）")

        # =========================
        # ✅ CSVログ保存（ボタン内だけで実行）
        # =========================
        log_path = "liberal_ai_log.csv"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_exists = os.path.isfile(log_path)

        # json.dumpsの安全化：必ずリストにする（NameError/型崩れ対策）
        sources_json = json.dumps(citations if isinstance(citations, list) else [], ensure_ascii=False)

        with open(log_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["timestamp", "user_input", "agree", "disagree", "extra", "sources_json"])
            writer.writerow([
                now,
                user_input.strip(),
                agree_text,
                disagree_text,
                extra_text_display,
                sources_json,
            ])

            
