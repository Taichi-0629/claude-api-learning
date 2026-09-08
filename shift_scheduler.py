import anthropic

client = anthropic.Anthropic()

staff_requests = {
    "田中": ["月", "火", "木"],
    "佐藤": ["水", "木", "金", "土"],
    "鈴木": ["月", "水", "金", "土", "日"],
}

required_staff_per_day = {
    "月": 1, "火": 1, "水": 2, "木": 2, "金": 2, "土": 2, "日": 1,
}

system_prompt = """あなたは小売店の店長を支援するシフト調整アシスタントです。
各スタッフの希望勤務曜日と、各曜日に必要な人数を渡すので、以下を行ってください。

1. 各曜日の勤務者を割り当てたシフト表を作成する
2. 必要人数を満たせなかった曜日があれば、その理由と対策案(例:追加募集、他曜日からの振替相談)を明記する
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

for block in response.content:
    if block.type == "text":
        print(block.text)

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=4096,
    system=system_prompt,
    messages=[{"role": "user", "content": user_prompt}]
)

print(f"[デバッグ] stop_reason: {response.stop_reason}")

for block in response.content:
    if block.type == "text":
        print(block.text)