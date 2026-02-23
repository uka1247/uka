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

# 💅 カスタムCSS（ダークエディトリアル × サイバー分析センター）
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400;500&family=Noto+Sans+JP:wght@300;400;500;700&display=swap');

        /* ─── ベースリセット ─── */
        html, body, [class*="css"] {
            font-family: 'Noto Sans JP', sans-serif;
            color: #F1F5F9;
        }

        /* ─── 背景：深いチャコール＋ノイズ感 ─── */
        .stApp {
            background-color: #0A0C10;
            background-image:
                radial-gradient(ellipse 80% 50% at 20% -10%, rgba(14, 165, 233, 0.12) 0%, transparent 60%),
                radial-gradient(ellipse 60% 40% at 85% 110%, rgba(99, 102, 241, 0.10) 0%, transparent 55%),
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
        }

        /* ─── メインコンテナ ─── */
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 4rem !important;
            max-width: 780px !important;
        }

        /* ─── ヘッダーセクション ─── */
        .header-wrap {
            position: relative;
            margin-bottom: 3rem;
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
            transition: transform 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94),
                        box-shadow 0.25s ease;
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
        .box:hover {
            transform: translateX(6px);
        }

        /* 賛成 */
        .agree {
            background: rgba(14, 165, 233, 0.05);
            border-left: 3px solid #0EA5E9;
            border-top: 1px solid rgba(14,165,233,0.15);
            border-right: 1px solid rgba(14,165,233,0.06);
            border-bottom: 1px solid rgba(14,165,233,0.06);
            box-shadow: 0 0 40px rgba(14, 165, 233, 0.04), inset 0 1px 0 rgba(255,255,255,0.03);
        }
        .agree:hover {
            box-shadow: 0 0 60px rgba(14, 165, 233, 0.10);
        }

        /* 反対 */
        .disagree {
            background: rgba(244, 63, 94, 0.05);
            border-left: 3px solid #F43F5E;
            border-top: 1px solid rgba(244,63,94,0.15);
            border-right: 1px solid rgba(244,63,94,0.06);
            border-bottom: 1px solid rgba(244,63,94,0.06);
            box-shadow: 0 0 40px rgba(244, 63, 94, 0.04), inset 0 1px 0 rgba(255,255,255,0.03);
        }
        .disagree:hover {
            box-shadow: 0 0 60px rgba(244, 63, 94, 0.10);
        }

        /* 補足 */
        .extra {
            background: rgba(99, 102, 241, 0.05);
            border-left: 3px solid #6366F1;
            border-top: 1px solid rgba(99,102,241,0.15);
            border-right: 1px solid rgba(99,102,241,0.06);
            border-bottom: 1px solid rgba(99,102,241,0.06);
            box-shadow: 0 0 40px rgba(99, 102, 241, 0.04), inset 0 1px 0 rgba(255,255,255,0.03);
        }
        .extra:hover {
            box-shadow: 0 0 60px rgba(99, 102, 241, 0.10);
        }

        /* カードラベル */
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
        textarea::placeholder {
            color: #475569 !important;
        }

        /* ─── ラベル ─── */
        .stTextArea label, .stTextArea label p {
            font-family: 'DM Mono', monospace !important;
            font-size: 0.72em !important;
            letter-spacing: 0.15em !important;
            text-transform: uppercase !important;
            color: #64748B !important;
        }

        /* ─── ボタン ─── */
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
            position: relative;
            overflow: hidden;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(14, 165, 233, 0.25), 0 4px 12px rgba(99, 102, 241, 0.2);
            color: #ffffff;
            border-color: transparent;
        }

        /* ─── スピナー ─── */
        .stSpinner > div {
            border-color: #0EA5E9 !important;
        }

        /* ─── 参考情報源 ─── */
        .stMarkdown h4 {
            font-family: 'DM Mono', monospace !important;
            font-size: 0.72em !important;
            letter-spacing: 0.2em !important;
            text-transform: uppercase !important;
            color: #475569 !important;
            margin-top: 2em !important;
        }
        .stMarkdown a {
            color: #38BDF8 !important;
            text-decoration: none !important;
            border-bottom: 1px solid rgba(56, 189, 248, 0.2) !important;
            transition: border-color 0.2s;
        }
        .stMarkdown a:hover {
            border-color: #38BDF8 !important;
        }

        /* ─── キャプション ─── */
        .stCaption {
            color: #334155 !important;
            font-size: 0.78em !important;
        }

        /* ─── 区切り線 ─── */
        hr {
            border-color: rgba(255,255,255,0.05) !important;
            margin: 2.5rem 0 !important;
        }

        /* ─── 結果ヘッダー ─── */
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

        /* ─── Warning ─── */
        .stWarning {
            background: rgba(245, 158, 11, 0.08) !important;
            border: 1px solid rgba(245, 158, 11, 0.2) !important;
            border-radius: 4px !important;
            color: #FCD34D !important;
        }
    </style>
""", unsafe_allow_html=True)


# =========================
# ヘッダー
# =========================
st.markdown("""
<div class="header-wrap">
    <div class="eyebrow">// Perspective Analysis Engine</div>
    <div class="main-title">Poly<span class="accent">View</span></div>
    <div class="subtext">あなたの意見に対して、賛否を中立的に提示する対話AI</div>
    <div class="header-rule"></div>
</div>
""", unsafe_allow_html=True)

# =========================
# トピック例（チップススタイル）
# =========================
st.markdown("<div class='section-label'>// 話題の例（クリックでコピー）</div>", unsafe_allow_html=True)

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

cards_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;'>"
for t in random_topics:
    safe_t = t.replace("'", "\\'")
    cards_html += f"""
    <div onclick="navigator.clipboard.writeText('{safe_t}'); this.style.borderColor='#0EA5E9'; this.style.color='#38BDF8'; setTimeout(()=>{{this.style.borderColor='rgba(255,255,255,0.10)'; this.style.color='#94A3B8';}}, 800);" style='
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 3px;
        padding: 7px 14px;
        font-size: 0.82em;
        color: #94A3B8;
        cursor: pointer;
        transition: all 0.2s ease;
        display: inline-block;
        font-family: Noto Sans JP, sans-serif;
        letter-spacing: 0.02em;
    ' onmouseover="this.style.borderColor='rgba(14,165,233,0.4)'; this.style.color='#CBD5E1'; this.style.background='rgba(14,165,233,0.06)';" 
      onmouseout="this.style.borderColor='rgba(255,255,255,0.10)'; this.style.color='#94A3B8'; this.style.background='rgba(255,255,255,0.03)';">
        {t}
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
user_input = st.text_area("// あなたの意見を入力", height=140, placeholder="例：AIはもっと規制されるべきだと思う。")

# =========================
# 実行
# =========================
if st.button("Analyze →") and user_input.strip() != "":
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
        st.markdown("### // Analysis Output")

        if agree_text:
            st.markdown(
                f'<div class="box agree"><span class="card-label">▸ 賛成の立場 / Pro</span>{agree_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 賛成の立場の抽出に失敗しました。")

        if disagree_text:
            st.markdown(
                f'<div class="box disagree"><span class="card-label">▸ 視点をずらした立場 / Counter</span>{disagree_text}</div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ 視点をずらした立場の抽出に失敗しました。")

        if extra_text:
            st.markdown(
                f'<div class="box extra"><span class="card-label">▸ 関連する補足情報 / Context</span>{extra_text}</div>',
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
