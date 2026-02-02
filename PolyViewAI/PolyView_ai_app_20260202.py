
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
st.markdown('<div class="subtext">あなたの意見に対して賛否を中立的に提示し、補足はエビデンス付きで表示する対話AI</div>', unsafe_allow_html=True)

# =========================
# トピック例
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

cards_html = "<div style='display: flex; justify-content: center; gap: 20px; flex-wrap: nowrap;'>"
for t in random_topics:
    safe_t = t.replace("'", "\\'")
    cards_html += f"""
    <div onclick="navigator.clipboard.writeText('{safe_t}')" style='
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

# =========================
# Utility
# =========================
def _get(obj, key, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def extract_url_citations(resp):
    """
    Responses APIの戻りから url_citation（タイトル・URL）を抽出。
    SDKのオブジェクト/辞書どちらでも動くようにしてある。
    """
    citations = []
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
                        citations.append({"title": title, "url": url})

    # URLで重複排除
    seen = set()
    uniq = []
    for c in citations:
        if c["url"] not in seen:
            uniq.append(c)
            seen.add(c["url"])
    return uniq

def parse_agree_disagree(text):
    agree_match = re.search(r"🔵\s*賛成の立場：\s*(.*?)(?=🔴|$)", text, re.DOTALL)
    disagree_match = re.search(r"🔴\s*視点をずらした立場：\s*(.*?)(?=$)", text, re.DOTALL)
    agree = agree_match.group(1).strip() if agree_match else ""
    disagree = disagree_match.group(1).strip() if disagree_match else ""
    return agree, disagree

# =========================
# 入力欄
# =========================
user_input = st.text_area("💬 あなたの意見をご自由に入力してください", height=150)

# =========================
# 実行
# =========================
if st.button("✨ 分析する") and user_input.strip() != "":
    with st.spinner("AIが分析中です..."):

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

        main_resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_main},
                {"role": "user", "content": user_main},
            ],
        )
        main_text = main_resp.choices[0].message.content or ""
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
- できるだけ公的機関・主要メディア・学術/統計など信頼性の高い情報に基づく
- 出力は“補足文のみ”（見出し・箇条書き・前置き不要）
"""

        # ※必要ならドメイン制限も可能（例）：
        # tools=[{"type": "web_search", "filters": {"allowed_domains": ["www.nhk.or.jp", "www.reuters.com"]}}]
        extra_resp = client.responses.create(
            model="gpt-4o",
            input=extra_prompt,
            tools=[{"type": "web_search"}],
            include=["web_search_call.action.sources"],
        )

        extra_text = (getattr(extra_resp, "output_text", "") or "").strip()
        citations = extract_url_citations(extra_resp)

        # =========================
        # 表示
        # =========================
        st.markdown("### 🔍 AIによる2つの視点と補足")

        if agree_text:
            st.markdown(
                f'<div class="box agree"><strong>🔵 賛成の立場：</strong><br>{agree_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 賛成の立場の抽出に失敗しました。")

        if disagree_text:
            st.markdown(
                f'<div class="box disagree"><strong>🔴 視点をずらした立場：</strong><br>{disagree_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 視点をずらした立場の抽出に失敗しました。")

        if extra_text:
            st.markdown(
                f'<div class="box extra">{extra_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 補足の生成に失敗しました。")

        # --- 補足の情報源（エビデンス）表示 ---
        if citations:
            st.markdown("#### 参考情報源")
            for i, c in enumerate(citations, 1):
                st.markdown(f"{i}. [{c['title']}]({c['url']})")
        else:
            st.caption("（今回の補足では、Web検索による引用URLが取得できませんでした）")

            
