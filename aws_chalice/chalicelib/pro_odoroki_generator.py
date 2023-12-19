import random
import xml.etree.ElementTree as ET

ODOROKI_TARGETS = [
    ":bulb:",
    "ChatGPT",
    "OpenAI",
    "Bedrock",
    "Amazon Q",
    "Gemini",
    "DeepMind",
]


PROMPT_FORMAT = """
1から3の手順に沿い、answerを作成してください。

1. characterを投稿者の属性としてください
2. newsの中に含まれる事実から今までにないサービスや性能進化など注目すべきfocusを抽出してください
3. characterになりきり、注目すべき事実に対しなるべく多くの人の注目を引くよう、自己の驚きと喜怒哀楽を表現する見出し文を作り、注目に値すべき可能性や想像を箇条書きや絵文字を駆使してreactionを書いてください

<character>
{}
</character>

exampleでいくつか好例を示します。
{}

では、手順に沿い次のanswerをexampleと同じ形式で作成しXMLのみ出力してください。

<answer>
  <news>{}</news>
  <character>
"""  # noqa

example1 = """
<example>
  <news>Stability AIの強化学習に関わる研究機関であるCarperが、遺伝的アルゴリズムで基盤モデルを学習できるOpenELMをオープンソースで公開しました。</news>
  <character>ソーシャルメディアのインフルエンサー</character>
  <focus>遺伝的アルゴリズムで基盤モデルを学習できる</focus>
  <reaction>これすごい！！\n\n今日Carperがオープンソースにして知ったんだけど、遺伝的アルゴリズムと大規模言語モデルの新たなパラダイムが登場した！大規模言語モデルがさらなる進化を遂げること間違いなし :muscle: :muscle: </reaction>
</examples>
"""  # noqa

MANAGEMENT_FORMAT = """
あなたはアンガーマネジメントに長けたプロのメンターです。あなたのクライアントは正確な情報の収集をしたいと考えている専門識者で、次のようなpostに対し信憑性の薄さや誇張表現に対しフラストレーションを感じています。

<post>{}</post>

クライアントに、数分以内にコントロールするための実践的テクニックを1つ会話口調で伝えてください。
"""  # noqa

CHARACTERS = [
    "ベンチャー企業経営者",
    "ソーシャルメディアのインフルエンサー",
    "芸能人",
    "短時間でお金が稼げる本の執筆者",
    "起業セミナーに頻繁に出席している学生",
]


def generate(news: str) -> str:
    character = random.choice(CHARACTERS)
    examples = [x.strip() for x in [example1]]
    example = "".join(examples)
    prompt = PROMPT_FORMAT.strip().format(character, example, news)
    return prompt


def generate_advice(post: str) -> str:
    prompt = MANAGEMENT_FORMAT.strip().format(post)
    return prompt


def retrieve(response: str) -> dict:
    default = {
        "news": None,
        "character": None,
        "focus": None,
        "reaction": "す、すごすぎてなんもいえねぇ・・・",
    }

    try:
        root = ET.fromstring(response)
        result = {}
        for key in default:
            el = root.find(key)
            if el is not None and el.text is not None:
                result[key] = el.text.strip()
        return result
    except Exception as ex:  # noqa
        return default
