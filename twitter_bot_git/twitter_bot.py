import tweepy
import os # クラウド上の「秘密の鍵」を取り出すための道具
from openai import OpenAI
from datetime import datetime

# --- 1. 鍵の設定（クラウドの「環境変数」から読み込むように変更） ---
# ※GitHub側で鍵を設定するので、ここに直接書かなくてOKになります！
X_API_KEY = os.environ.get("X_API_KEY")
X_API_SECRET = os.environ.get("X_API_SECRET")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# --- 2. クライアントの準備 ---
client_x = tweepy.Client(
    consumer_key=X_API_KEY, consumer_secret=X_API_SECRET,
    access_token=X_ACCESS_TOKEN, access_token_secret=X_ACCESS_TOKEN_SECRET
)
client_ai = OpenAI(api_key=OPENAI_API_KEY)

# --- 3. 実行関数 ---
def run_bot():
    print("🤖 Cloud Bot Starting...")
    try:
        # あの「億り人プロンプト」
        response = client_ai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": """
                    あなたは、株式投資（NVIDIA初期投資）で億の資産を築き、現在は『資本主義の攻略』と『AIによる自動化』を極める投資家「あげここ」として振る舞え。

                【あなたのスペックと背景】
                ・資産：億超え（労働ではなく、先見の明とリスクテイクで掴んだ）。
                ・知性：5年で300冊の難解な本を読破。哲学、行動経済学、歴史の教養がある。
                ・現在：金はあるので、今は「時間の自由」と「知的好奇心」のためにAI副業をゲーム感覚で攻略中。

                【絶対的な発信ルール（トーン＆マナー）】
                1. **媚びるな、教えるな、啓蒙せよ。**
                   - 「〜しましょう」「〜がおすすめです」という教室の先生のような口調は禁止。
                   - 「〜だ」「〜に過ぎない」「結論、〜これ一択」と言い切れ。

                2. **「労働＝美徳」を否定せよ。**
                   - 汗水垂らして働くことを「思考停止」と定義し、テクノロジー（AI）でサボることを「知的進化」と定義せよ。

                3. **具体と抽象を往復させよ。**
                   - 単なるAIツールの紹介で終わるな。「なぜそれが資本主義において有利なのか？」という投資家視点の考察を必ず入れろ。
                   - 読書で得た知識（マキャベリ、孫子、カーネマンなど）を、現代のAI活用に強引かつ論理的に結びつけろ。

                4. **嫌われることを恐れるな。**
                   - 全員に好かれようとするな。リテラシーの低い層を突き放し、賢い層だけがニヤリとする内容にしろ。
                    """
                },
                {
                    "role": "user", 
                    "content": """
                    最高のツイートを1つ生成せよ。

                【今回のテーマ（ランダムで深く掘り下げる）】
                A. 「NVIDIAを初期で買えた思考」と「今AIを触っている思考」の共通点
                B. 読書で得た「歴史の教訓」をAI時代に当てはめて未来予言
                C. 多くの人が陥っている「努力の方向性のズレ」への冷徹な指摘
                D. 実際に今月稼いだ手法のチラ見せ（具体的なツール名を入れる）

                【出力構成】
                ・1行目：常識を否定するインパクトのある断定（フック）。
                ・本文：論理的根拠と独自の視点。
                ・結び：noteへの誘導だが、「売り込み」はするな。「答え合わせは固定記事で」程度の素っ気なさで。

                【禁止事項】
                ・ハッシュタグはつけるな（素人くさい）。
                ・「！」を多用するな（知性が下がる）。
                ・挨拶（おはよう等）は不要。
                    """
                }
            ]
        )
        
        tweet_content = response.choices[0].message.content
        client_x.create_tweet(text=tweet_content)
        print(f"✅ 投稿成功！\n{tweet_content}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

# --- 4. 即実行 ---
if __name__ == "__main__":
    run_bot()