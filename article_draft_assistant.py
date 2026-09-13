import streamlit as st
import anthropic
import os

try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    api_key = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

st.title("記事下書きアシスタント")
st.write("キーワードを入力すると、Web検索で最新のトレンド・上位記事の傾向を調べたうえで、記事の構成案・下書きを作成します。")

topic = st.text_input("記事のテーマ・キーワード", placeholder="例:もつ鍋 一人前 東京")

if st.button("リサーチ&下書き作成"):
    if not topic:
        st.warning("テーマを入力してください。")
    else:
        with st.spinner("Web検索とリサーチを行っています..."):
            system_prompt = """あなたはSEOと読者ニーズに詳しい編集者兼ライターです。
与えられたテーマについて、Web検索を使って以下を調べてください。

1. このテーマでよく検索されている関連キーワード・疑問
2. 上位表示されている記事がどのような構成・切り口で書かれているか

そのうえで、以下を出力してください。

## リサーチ結果
(調べて分かった検索ニーズ・上位記事の傾向を簡潔に)

## 記事構成案
(見出し単位の構成案)

## 導入文の下書き
(実際に使える形の導入文、300字程度)
"""
            response = client.messages.create(
                model="claude-sonnet-5",
                max_tokens=4096,
                system=system_prompt,
                tools=[{
                    "type": "web_search_20260209",
                    "name": "web_search",
                    "max_uses": 5
                }],
                messages=[{"role": "user", "content": f"テーマ:{topic}"}]
            )

            result_text = ""
            for block in response.content:
                if block.type == "text":
                    result_text += block.text

        st.subheader("結果")
        st.markdown(result_text)