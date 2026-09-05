import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

# 仮の在庫データ(本来はDBやAPIから取得する部分)
inventory_data = {
    "シャンプー": 42,
    "洗剤": 5,
    "歯ブラシ": 120,
}

@beta_tool
def check_inventory(item_name: str) -> str:
    """指定した商品の在庫数を確認する。

    Args:
        item_name: 確認したい商品名(例:シャンプー)
    """
    stock = inventory_data.get(item_name)
    if stock is None:
        return f"{item_name} は在庫データに存在しません。"
    return f"{item_name} の在庫数は {stock} 個です。"

print("在庫照会ボット起動(終了するには 'exit')")

messages = []
while True:
    user_input = input("あなた: ")
    if user_input.lower() == "exit":
        break

    messages.append({"role": "user", "content": user_input})

    runner = client.beta.messages.tool_runner(
        model="claude-sonnet-5",
        max_tokens=1024,
        tools=[check_inventory],
        messages=messages,
    )

    last_message = None
    for message in runner:
        last_message = message

    reply_text = ""
    for block in last_message.content:
        if block.type == "text":
            reply_text += block.text

    print(f"Claude: {reply_text}")
    messages.append({"role": "assistant", "content": last_message.content})