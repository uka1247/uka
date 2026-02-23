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

# =========================
# 🌍 言語設定
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "JA"

# テキスト辞書
T = {
    "JA": {
        "eyebrow": "// Perspective Analysis Engine",
        "subtext": "あなたの意見に対して、賛否を中立的に提示する対話AI",
        "lang_btn": "🌐 EN",
        "topic_label": "// 話題の例（クリックでコピー）",
        "input_label": "// あなたの意見を入力",
        "input_placeholder": "例：AIはもっと規制されるべきだと思う。",
        "analyze_btn": "分析する →",
        "spinner": "AIが多角的な視点から分析中です...",
        "output_header": "### // Analysis Output",
        "card_agree": "▸ 賛成の立場 / Pro",
        "card_disagree": "▸ 視点をずらした立場 / Counter",
        "card_extra": "▸ 関連する補足情報 / Context",
        "warn_agree": "⚠️ 賛成の立場の抽出に失敗しました。",
        "warn_disagree": "⚠️ 視点をずらした立場の抽出に失敗しました。",
        "warn_extra": "⚠️ 補足の生成に失敗しました。",
        "ref_header": "#### 📚 参考情報源",
        "no_citations": "（今回の補足では、Web検索による引用URLが取得できませんでした）",
        "topics": [
            "ベーシックインカムは導入すべきだと思う？", "死刑制度は倫理に反してる？", "大学の無償化には賛成？反対？",
            "原発は必要だと思う？", "同性婚はあり？", "AIに規制は必要？", "選挙権年齢は18歳のままでいい？",
            "公共交通は無料にすべき？", "移民の受け入れ", "SNSでの発言に匿名性は必要か？",
            "マイナンバーカードの義務化に賛成？", "日本は防衛力を強化すべきか？", "コンビニの24時間営業は必要？",
            "給食の無償化は全国で実施した方がいい？", "週休3日制は導入すべき？", "選挙はオンライン投票を導入すべき？",
            "ジェンダー教育は義務教育に含めた方がいいのか", "カジノは合法化でOK？", "動物実験は倫理的に許される？",
            "最近のトランプ政権について", "消費税撤廃", "政治家の裏金問題", "マスコミによる情報統制は撤廃すべき？"
        ],
        "system_main": (
            "あなたはユーザーの意見に対して、賛成と反対（視点ずらし）の両方の視点を提示するAIです。"
            "反対意見は多様な立場の一例を示すこと。極端な否定や扇情的な表現は避け、論理的で建設的に。"
            "ここでは補足は書かないでください。"
        ),
        "user_main_tmpl": lambda opinion: f"""
以下はユーザーの意見です：
「{opinion}」

この意見に対して、以下の形式で"必ず"出力してください（補足は出力しない）：

🔵 賛成の立場：
簡潔に賛成意見を2〜7文で述べてください。

🔴 視点をずらした立場：
簡潔に反対意見を2〜7文で述べてください。反対意見は多様な立場の一例を示すこと。極端な否定や扇情的な表現は避け、論理的で建設的に提示してください。
""",
        "prefixes": [
            "補足になりますが、",
            "ちなみに、",
            "念のため付け加えると、",
            "ここで一つだけ補足すると、",
            "話題を広げる意味で補足すると、",
        ],
        "extra_prompt_tmpl": lambda opinion, prefix: f"""
以下はユーザーの意見です：
「{opinion}」

この意見に関連する最近の社会的文脈・報道・統計・政策などの情報を踏まえつつ、
中立的な「補足」を2〜5文で作成してください。

制約：
- 冒頭は必ず「{prefix}」で始める
- 語り口は穏やかで、読者に考える余地を残す
- 断定しすぎず、必要に応じて「〜とされる」「〜との指摘がある」などで調整する
- 極端に扇情的な言い回しは避ける
- できるだけ公的機関・主要メディア・学術/統計など信頼性の高い情報に基づく
- 出力は"補足文のみ"（見出し・箇条書き・前置き不要）
""",
        "agree_pattern": r"🔵\s*賛成の立場：\s*(.*?)(?=🔴|$)",
        "disagree_pattern": r"🔴\s*視点をずらした立場：\s*(.*?)(?=$)",
    },
    "EN": {
        "eyebrow": "// Perspective Analysis Engine",
        "subtext": "An AI that neutrally presents both sides of your opinion",
        "lang_btn": "🌐 JA",
        "topic_label": "// Sample topics (click to copy)",
        "input_label": "// Enter your opinion",
        "input_placeholder": "e.g. AI should be more strictly regulated.",
        "analyze_btn": "Analyze →",
        "spinner": "AI is analyzing multiple perspectives...",
        "output_header": "### // Analysis Output",
        "card_agree": "▸ Pro / Supporting View",
        "card_disagree": "▸ Counter / Alternative View",
        "card_extra": "▸ Contextual Supplement",
        "warn_agree": "⚠️ Failed to extract the supporting view.",
        "warn_disagree": "⚠️ Failed to extract the counter view.",
        "warn_extra": "⚠️ Failed to generate the supplement.",
        "ref_header": "#### 📚 References",
        "no_citations": "(No URL citations were retrieved from web search for this supplement.)",
        "topics": [
            "Should basic income be introduced?", "Is the death penalty unethical?", "Should university tuition be free?",
            "Are nuclear power plants necessary?", "Should same-sex marriage be legalized?", "Should AI be regulated?",
            "Is the voting age of 18 appropriate?", "Should public transit be free?", "Open immigration policy",
            "Should anonymity be protected on social media?", "Should national IDs be mandatory?",
            "Should defense spending increase?", "Are 24-hour convenience stores necessary?",
            "Should school meals be free nationwide?", "Should a 4-day work week be adopted?",
            "Should online voting be introduced?", "Should gender education be compulsory?",
            "Should casinos be legalized?", "Is animal testing ethically acceptable?",
            "Trump administration recent policies", "Abolishing consumption tax",
            "Political corruption and slush funds", "Should media censorship be lifted?",
        ],
        "system_main": (
            "You are an AI that presents both supporting and opposing (alternative) perspectives on the user's opinion. "
            "The counter view should represent one of many diverse positions. Avoid extremist or inflammatory language; be logical and constructive. "
            "Do not include any supplementary notes here."
        ),
        "user_main_tmpl": lambda opinion: f"""
The following is the user's opinion:
"{opinion}"

Please respond EXACTLY in the following format (no supplementary notes):

🔵 Supporting View:
State 2-7 sentences in favor of this opinion concisely.

🔴 Alternative / Counter View:
State 2-7 sentences representing a different perspective. Represent one of many diverse positions. Avoid extreme negation or inflammatory language; present it logically and constructively.
""",
        "prefixes": [
            "As a supplement, ",
            "Interestingly, ",
            "Worth adding that ",
            "For additional context, ",
            "Broadening the perspective, ",
        ],
        "extra_prompt_tmpl": lambda opinion, prefix: f"""
The following is the user's opinion:
"{opinion}"

Based on recent social context, news, statistics, or policies related to this topic,
write a neutral 2-5 sentence supplement.

Constraints:
- Start with exactly: "{prefix}"
- Keep the tone calm and leave room for the reader to think
- Avoid over-asserting; use hedging language like "it is said that" or "some argue that"
- Avoid sensationalist language
- Base information on reliable sources: government bodies, major media, academic/statistical sources
- Output the supplement text ONLY (no headers, bullets, or preamble)
""",
        "agree_pattern": r"🔵\s*Supporting View:\s*(.*?)(?=🔴|$)",
        "disagree_pattern": r"🔴\s*Alternative\s*/\s*Counter View:\s*(.*?)(?=$)",
    }
}

# =========================
# 💅 カスタムCSS
# =========================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400;500&family=Noto+Sans+JP:wght@300;400;500;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Noto Sans JP', sans-serif;
            color: #F1F5F9;
        }

        .stApp {
            background-color: #0A0C10;
            background-image:
                radial-gradient(ellipse 80% 50% at 20% -10%, rgba(14, 165, 233, 0.12) 0%, transparent 60%),
                radial-gradient(ellipse 60% 40% at 85% 110%, rgba(99, 102, 241, 0.10) 0%, transparent 55%),
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
        }

        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 4rem !important;
            max-width: 780px !important;
        }

        /* ─── ヘッダー ─── */
        .header-wrap {
            position: relative;
            margin-bottom: 2.5rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        .eyebrow {
            font-family: 'DM Mono', monospace;
            font-size: 0.72em;
            letter-spacing: 0.25em;
            color: #0EA5E9;
            text-transform: uppercase;
            margin-bottom: 0.6em;
        }
        .main-title {
            font-family: 'Syne', sans-serif;
            font-size: 3.8em;
            font-weight: 800;
            line-height: 1.0;
            letter-spacing: -0.03em;
            color: #F1F5F9;
            margin-bottom: 0.25em;
        }
        .main-title .accent {
            background: linear-gradient(90deg, #0EA5E9 0%, #6366F1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtext {
            font-size: 0.95em;
            color: #94A3B8;
            font-weight: 300;
            letter-spacing: 0.01em;
            margin-top: 0.5em;
        }
        .header-rule {
            position: absolute;
            bottom: -1px;
            left: 0;
            width: 60px;
            height: 2px;
            background: linear-gradient(90deg, #0EA5E9, #6366F1);
        }

        /* ─── セクションラベル ─── */
        .section-label {
            font-family: 'DM Mono', monospace;
            font-size: 0.7em;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            color: #64748B;
            margin-bottom: 0.8em;
        }

        /* ─── 結果カード ─── */
        .box {
            position: relative;
            border-radius: 4px;
            padding: 28px 30px;
            margin: 18px 0;
            line-height: 1.8;
            font-size: 0.97em;
            font-weight: 400;
            color: #F1F5F9;
            overflow: hidden;
            transition: transform 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94), box-shadow 0.25s ease;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }
        .box::before {
            content: '';
            position: absolute;
            inset: 0;
            background: rgba(255,255,255,0.02);
            pointer-events: none;
        }
        .box:hover { transform: translateX(6px); }

        .agree {
            background: rgba(14, 165, 233, 0.05);
            border-left: 3px solid #0EA5E9;
            border-top: 1px solid rgba(14,165,233,0.15);
            border-right: 1px solid rgba(14,165,233,0.06);
            border-bottom: 1px solid rgba(14,165,233,0.06);
            box-shadow: 0 0 40px rgba(14, 165, 233, 0.04), inset 0 1px 0 rgba(255,255,255,0.03);
        }
        .agree:hover { box-shadow: 0 0 60px rgba(14, 165, 233, 0.10); }

        .disagree {
            background: rgba(244, 63, 94, 0.05);
            border-left: 3px solid #F43F5E;
            border-top: 1px solid rgba(244,63,94,0.15);
            border-right: 1px solid rgba(244,63,94,0.06);
            border-bottom: 1px solid rgba(244,63,94,0.06);
            box-shadow: 0 0 40px rgba(244, 63, 94, 0.04), inset 0 1px 0 rgba(255,255,255,0.03);
        }
        .disagree:hover { box-shadow: 0 0 60px rgba(244, 63, 94, 0.10); }

        .extra {
            background: rgba(99, 102, 241, 0.05);
            border-left: 3px solid #6366F1;
            border-top: 1px solid rgba(99,102,241,0.15);
            border-right: 1px solid rgba(99,102,241,0.06);
            border-bottom: 1px solid rgba(99,102,241,0.06);
            box-shadow: 0 0 40px rgba(99, 102, 241, 0.04), inset 0 1px 0 rgba(255,255,255,0.03);
        }
        .extra:hover { box-shadow: 0 0 60px rgba(99, 102, 241, 0.10); }

        .card-label {
            font-family: 'DM Mono', monospace;
            font-size: 0.7em;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            display: block;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .agree .card-label   { color: #38BDF8; }
        .disagree .card-label { color: #FB7185; }
        .extra .card-label   { color: #818CF8; }

        /* ─── テキストエリア ─── */
        div[data-baseweb="textarea"] > div {
            background-color: rgba(15, 23, 42, 0.8) !important;
            border-radius: 4px !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            color: #F1F5F9 !important;
            transition: all 0.3s ease;
            font-family: 'Noto Sans JP', sans-serif !important;
        }
        div[data-baseweb="textarea"] > div:focus-within {
            border-color: rgba(14, 165, 233, 0.5) !important;
            box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.08) !important;
        }
        textarea {
            color: #F1F5F9 !important;
            font-size: 0.95em !important;
            line-height: 1.7 !important;
        }
        textarea::placeholder { color: #475569 !important; }

        .stTextArea label, .stTextArea label p {
            font-family: 'DM Mono', monospace !important;
            font-size: 0.72em !important;
            letter-spacing: 0.15em !important;
            text-transform: uppercase !important;
            color: #64748B !important;
        }

        /* ─── ボタン（メイン分析） ─── */
        .stButton > button {
            width: 100%;
            border-radius: 4px;
            background: linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%);
            color: #F8FAFC;
            font-family: 'DM Mono', monospace;
            font-weight: 500;
            font-size: 0.85em;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            border: none;
            padding: 15px 28px;
            margin-top: 8px;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(14, 165, 233, 0.25), 0 4px 12px rgba(99, 102, 241, 0.2);
            color: #ffffff;
            border-color: transparent;
        }

        /* ─── 言語ボタン専用（右カラム） ─── */
        [data-testid="column"]:last-child > div > div > div > div > .stButton > button {
            width: auto !important;
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            color: #94A3B8 !important;
            font-size: 0.75em !important;
            padding: 9px 16px !important;
            margin-top: 0 !important;
            letter-spacing: 0.1em !important;
            box-shadow: none !important;
        }
        [data-testid="column"]:last-child > div > div > div > div > .stButton > button:hover {
            background: rgba(14, 165, 233, 0.10) !important;
            border-color: rgba(14, 165, 233, 0.4) !important;
            color: #38BDF8 !important;
            transform: none !important;
            box-shadow: none !important;
        }

        /* ─── スピナー ─── */
        .stSpinner > div { border-color: #0EA5E9 !important; }

        /* ─── 参照 ─── */
        .stMarkdown h4 {
            font-family: 'DM Mono', monospace !important;
            font-size: 0.72em !important;
            letter-spacing: 0.2em !important;
            text-transform: uppercase !important;
            color: #64748B !important;
            margin-top: 2em !important;
        }
        .stMarkdown a {
            color: #38BDF8 !important;
            text-decoration: none !important;
            border-bottom: 1px solid rgba(56, 189, 248, 0.2) !important;
        }
        .stMarkdown a:hover { border-color: #38BDF8 !important; }
        .stCaption { color: #475569 !important; font-size: 0.78em !important; }

        .stMarkdown h3 {
            font-family: 'Syne', sans-serif !important;
            font-size: 1.2em !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em !important;
            color: #CBD5E1 !important;
            border-bottom: 1px solid rgba(255,255,255,0.07) !important;
            padding-bottom: 0.6em !important;
            margin-bottom: 1.5em !important;
        }

        .stWarning {
            background: rgba(245, 158, 11, 0.08) !important;
            border: 1px solid rgba(245, 158, 11, 0.2) !important;
            border-radius: 4px !important;
            color: #FCD34D !important;
        }
    </style>
""", unsafe_allow_html=True)

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

def parse_agree_disagree(text, lang):
    agree_match = re.search(T[lang]["agree_pattern"], text, re.DOTALL)
    disagree_match = re.search(T[lang]["disagree_pattern"], text, re.DOTALL)
    agree = agree_match.group(1).strip() if agree_match else ""
    disagree = disagree_match.group(1).strip() if disagree_match else ""
    return agree, disagree

# =========================
# 現在の言語
# =========================
lang = st.session_state.lang
t = T[lang]

# =========================
# ヘッダー + 言語切り替えボタン
# =========================
col_title, col_lang = st.columns([5, 1])

with col_title:
    st.markdown(f"""
    <div class="header-wrap">
        <div class="eyebrow">{t['eyebrow']}</div>
        <div class="main-title">Poly<span class="accent">View</span></div>
        <div class="subtext">{t['subtext']}</div>
        <div class="header-rule"></div>
    </div>
    """, unsafe_allow_html=True)

with col_lang:
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    if st.button(t["lang_btn"], key="lang_toggle"):
        st.session_state.lang = "EN" if lang == "JA" else "JA"
        st.rerun()

# =========================
# トピック例
# =========================
st.markdown(f"<div class='section-label'>{t['topic_label']}</div>", unsafe_allow_html=True)

random_topics = random.sample(t["topics"], 6)
cards_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;'>"
for topic in random_topics:
    safe_t = topic.replace("'", "\\'")
    cards_html += f"""
    <div onclick="navigator.clipboard.writeText('{safe_t}'); this.style.borderColor='#0EA5E9'; this.style.color='#38BDF8'; setTimeout(()=>{{this.style.borderColor='rgba(255,255,255,0.10)'; this.style.color='#94A3B8';}}, 800);"
    style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.10); border-radius: 3px;
    padding: 7px 14px; font-size: 0.82em; color: #94A3B8; cursor: pointer; transition: all 0.2s ease;
    display: inline-block; font-family: Noto Sans JP, sans-serif; letter-spacing: 0.02em;'
    onmouseover="this.style.borderColor='rgba(14,165,233,0.4)'; this.style.color='#CBD5E1'; this.style.background='rgba(14,165,233,0.06)';"
    onmouseout="this.style.borderColor='rgba(255,255,255,0.10)'; this.style.color='#94A3B8'; this.style.background='rgba(255,255,255,0.03)';">
        {topic}
    </div>
    """
cards_html += "</div>"
components.html(cards_html, height=110)

# =========================
# 入力欄
# =========================
user_input = st.text_area(t["input_label"], height=140, placeholder=t["input_placeholder"])

# =========================
# 実行
# =========================
if st.button(t["analyze_btn"]) and user_input.strip() != "":
    with st.spinner(t["spinner"]):

        # 1) 賛否生成
        main_resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": t["system_main"]},
                {"role": "user", "content": t["user_main_tmpl"](user_input)},
            ],
        )
        main_text = main_resp.choices[0].message.content or ""
        agree_text, disagree_text = parse_agree_disagree(main_text, lang)

        # 2) 補足（Web検索あり）
        chosen_prefix = random.choice(t["prefixes"])
        extra_resp = client.responses.create(
            model="gpt-4o",
            input=t["extra_prompt_tmpl"](user_input, chosen_prefix),
            tools=[{"type": "web_search"}],
            include=["web_search_call.action.sources"],
        )
        extra_text = (getattr(extra_resp, "output_text", "") or "").strip()
        citations = extract_url_citations(extra_resp)

        # 表示
        st.markdown(t["output_header"])

        if agree_text:
            st.markdown(
                f'<div class="box agree"><span class="card-label">{t["card_agree"]}</span>{agree_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning(t["warn_agree"])

        if disagree_text:
            st.markdown(
                f'<div class="box disagree"><span class="card-label">{t["card_disagree"]}</span>{disagree_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning(t["warn_disagree"])

        if extra_text:
            st.markdown(
                f'<div class="box extra"><span class="card-label">{t["card_extra"]}</span>{extra_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning(t["warn_extra"])

        if citations:
            st.markdown(t["ref_header"])
            for i, c in enumerate(citations, 1):
                st.markdown(f"{i}. [{c['title']}]({c['url']})")
        else:
            st.caption(t["no_citations"])
