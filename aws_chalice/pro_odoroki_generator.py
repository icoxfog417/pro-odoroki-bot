PROMPT_FORMAT = """
1から5の手順に沿い、answerを作成してください。

1. charactersから投稿者の属性を選択してください
2. newsの中に含まれる事実から今までにないサービスや性能進化など注目すべきfocusを抽出してください
3. characterになりきり、注目すべき事実に対しなるべく多くの人の注目を引くよう、自己の驚きと喜怒哀楽を表現する見出し文を作り、注目に値すべき可能性や想像を箇条書きや絵文字を駆使してreactionを書いてください

<characters>
ベンチャー企業経営者
ソーシャルメディアのインフルエンサー
芸能人
短時間でお金が稼げる本の執筆者
起業セミナーに頻繁に出席している学生
</characters>

exampleでいくつか好例を示します。
{}

では、手順に沿い次のnewsからexampleと同じ構造の文章answerを埋める形で返答してください。

<answer>
  <news>{}</news>
  <character>
"""

example1 = """
<example>
  <news>Stability AIの強化学習に関わる研究機関であるCarperが、遺伝的アルゴリズムで基盤モデルを学習できるOpenELMをオープンソースで公開しました。</news>
  <character>ソーシャルメディアのインフルエンサー</character>
  <focus>遺伝的アルゴリズムで基盤モデルを学習できる</focus>
  <reaction>これすごい！！\n\n今日Carperがオープンソースにして知ったんだけど、遺伝的アルゴリズムと大規模言語モデルの新たなパラダイムが登場した！大規模言語モデルがさらなる進化を遂げること間違いなし :muscle: :muscle: </reaction>
</examples>
"""

def generate(news: str) -> str:
    examples = [x.strip() for x in [example1]]
    example = "".join(examples)
    prompt = PROMPT_FORMAT.strip().format(example, news)
    return prompt
