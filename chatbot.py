import anthropic

client = anthropic.Anthropic()

system_prompt = "あなたは親切なアシスタントです。日本語で、簡潔に answer してください。"

messages = []

print("チャットボット起動(終了するには 'exit' と入力)")

while True:
    user_input = input("あなた: ")
    if user_input.lower() == "exit":
        break

    messages.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        system=system_prompt,
        messages=messages
    )

    reply_text = ""
    for block in response.content:
        if block.type == "text":
            reply_text += block.text

    print(f"Claude: {reply_text}")

    messages.append({"role": "assistant", "content": reply_text})