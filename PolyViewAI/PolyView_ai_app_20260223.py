import streamlit as st
import openai
import re
import random
import os
import streamlit.components.v1 as components

# 🔑 OpenAI APIキーを設定（環境変数から）
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

# 🌐 ページ設定
st.set_page_config(page_title="PolyView AI", layout="centered", page_icon="⚖️")

# 💅 カスタムCSS（シンプルでモダンなデザイン）
st.markdown("""
    <style>
        /* ベース設定 */
        body {
            background-color: #F8F9FA;
            font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
            color: #202124;
        }
        
        /* メインタイトル：グラデーションでモダンに */
        .main-title {
            font-size: 3em;
            font-weight: 800;
            background: linear-gradient(135deg, #1A2980 0%, #26D0CE 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.1em;
            letter-spacing: -0.02em;
        }
        
        /* サブテキスト */
        .subtext {
            font-size: 1.1em;
            color: #5F6368;
            margin-bottom: 2.5em;
            font-weight: 500;
        }
        
        /* 結果表示用ボックス */
        .box {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.04);
            margin-top: 20px;
            margin-bottom: 20px;
            border: 1px solid #E8EAED;
            line-height: 1.7;
            transition: transform 0.2s ease;
        }
        .box:hover {
            transform: translateY(-2px);
        }
        
        /* 各立場のアクセントカラー */
        .agree {
            border-top: 5px solid #3B82F6; /* ブルー */
        }
        .disagree {
            border-top: 5px solid #EF4444; /* レッド */
        }
        .extra {
            border-top: 5px solid #8B5CF6; /* パープル */
            background-color: #F8FAFC;
        }
        .box strong {
            font-size: 1.1em;
            display: inline-block;
            margin-bottom: 8px;
        }

        /* Streamlitデフォルト要素の上書き */
        /* テキストエリア */
        div[data-baseweb="textarea"] > div {
            background-color: #FFFFFF;
            border-radius: 12px;
            border: 1px solid #E8EAED;
            transition: all 0.3s ease;
        }
        div[data-baseweb="textarea"] > div:focus-within {
            border-color: #3B82F6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }
        
        /* ボタン */
        .stButton > button {
            width: 100%;
            border-radius: 12px;
            background: linear-gradient(135deg, #3B82F6, #2563EB);
            color: white;
            font-weight: 600;
            font-size: 1.1em;
            border: none;
            padding: 12px 24px;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
            color: white;
            border-color: transparent;
        }
    </style>
""", unsafe_allow_html=True)


# =========================
# ヘッダー
# =========================
st.markdown('<div class="main-title">PolyView AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtext">あなたの意見に対して、賛否を中立的に提示する対話AI</div>', unsafe_allow_html=True)

# =========================
# トピック例（チップススタイル）
# =========================
st.markdown("<div style='color:#5F6368; font-size:0.95em; font-weight: 600; margin-bottom:12px;'>💡 クリックしてコピーできる話題</div>", unsafe_allow_html=True)

topics = [
    "ベーシックインカムは導入すべきだと思う？", "死刑制度は倫理に反してる？", "大学の無償化には賛成？反対？",
    "原発は必要だと思う？", "同性婚はあり？", "AIに規制は必要？", "選挙権年齢は18歳のままでいい？",
    "公共交通は無料にすべき？", "移民の受け入れ", "SNSでの発言に匿名性は必要か？", 
    "マイナンバーカードの義務化に賛成？", "日本は防衛力を強化すべきか？", "コンビニの24時間営業は必要？",
    "給食の無償化は全国で実施した方がいい？", "週休3日制は導入すべき？", "選挙はオンライン投票を導入すべき？",
    "ジェンダー教育は義務教育に含めた方がいいのか", "カジノは合法化でOK？", "動物実験は倫理的に許される？",
    "最近のトランプ政権について", "消費税撤廃", "政治家の裏金問題", "マスコミによる情報統制は撤廃すべき？"
]

# チップスデザインに変更し、表示数を6個に増量
random_topics = random.sample(topics, 6)

cards_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px;'>"
for t in random_topics:
    safe_t = t.replace("'", "\\'")
    cards_html += f"""
    <div onclick="navigator.clipboard.writeText('{safe_t}')" style='
        background-color: #FFFFFF;
        border: 1px solid #E8EAED;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 0.9em;
        color: #3C4043;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        display: inline-block;
    ' onmouseover="this.style.borderColor='#3B82F6'; this.style.color='#3B82F6'; this.style.transform='translateY(-1px)';" 
      onmouseout="this.style.borderColor='#E8EAED'; this.style.color='#3C4043'; this.style.transform='translateY(0)';">
        # {t}
    </div>
    """
cards_html += "</div>"
components.html(cards_html, height=110)

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
user_input = st.text_area("💬 あなたの意見をご自由に入力してください", height=140, placeholder="例：AIはもっと規制されるべきだと思う。")

# =========================
# 実行
# =========================
if st.button("✨ 意見を分析する") and user_input.strip() != "":
    with st.spinner("AIが多角的な視点から分析中です..."):

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
                f'<div class="box agree"><strong style="color: #2563EB;">🔵 賛成の立場</strong><br>{agree_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 賛成の立場の抽出に失敗しました。")

        if disagree_text:
            st.markdown(
                f'<div class="box disagree"><strong style="color: #DC2626;">🔴 視点をずらした立場</strong><br>{disagree_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 視点をずらした立場の抽出に失敗しました。")

        if extra_text:
            st.markdown(
                f'<div class="box extra"><strong style="color: #7C3AED;">💡 関連する補足情報</strong><br>{extra_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 補足の生成に失敗しました。")

        # --- 補足の情報源（エビデンス）表示 ---
        if citations:
            st.markdown("#### 📚 参考情報源")
            for i, c in enumerate(citations, 1):
                st.markdown(f"{i}. [{c['title']}]({c['url']})")
        else:
            st.caption("（今回の補足では、Web検索による引用URLが取得できませんでした）")