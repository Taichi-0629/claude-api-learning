import os
import streamlit as st
import anthropic

try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    api_key = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

st.title("シフト調整アシスタント")
st.write("スタッフの希望勤務曜日を入力すると、Claudeがシフト案を作成します。")

days = ["月", "火", "水", "木", "金", "土", "日"]

st.subheader("スタッフの希望勤務曜日")

staff_requests = {}
for i in range(1, 4):
    col1, col2 = st.columns([1, 3])
    with col1:
        name = st.text_input(f"スタッフ{i}の名前", value=f"スタッフ{i}", key=f"name_{i}")
    with col2:
        selected_days = st.multiselect(f"{name}の希望曜日", days, key=f"days_{i}")
    if name and selected_days:
        staff_requests[name] = selected_days

st.subheader("曜日ごとの必要人数")

required_staff_per_day = {}
cols = st.columns(7)
for i, day in enumerate(days):
    with cols[i]:
        required_staff_per_day[day] = st.number_input(day, min_value=0, max_value=10, value=1, key=f"req_{day}")

if st.button("シフト案を作成"):
    if not staff_requests:
        st.warning("スタッフの希望を1人以上入力してください。")
    else:
        with st.spinner("Claudeがシフト案を考えています..."):
            system_prompt = """あなたは小売店の店長を支援するシフト調整アシスタントです。
各スタッフの希望勤務曜日と、各曜日に必要な人数を渡すので、以下を行ってください。

1. 各曜日の勤務者を割り当てたシフト表を作成する
2. 必要人数を満たせなかった曜日があれば、その理由と対策案を明記する
3. 出力は「曜日ごとの勤務者一覧」と「調整が必要な箇所」の2セクションに分けて、簡潔にまとめる
"""
            user_prompt = f"""
スタッフの希望勤務曜日:
{staff_requests}

各曜日の必要人数:
{required_staff_per_day}

上記をもとにシフト案を作成してください。
"""
            response = client.messages.create(
                model="claude-sonnet-5",
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            result_text = ""
            for block in response.content:
                if block.type == "text":
                    result_text += block.text

        st.subheader("シフト案")
        st.markdown(result_text)