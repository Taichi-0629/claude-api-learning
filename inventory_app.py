import streamlit as st
import anthropic
from anthropic import beta_tool
import json
import os

DATA_FILE = "inventory_data.json"

# 飲食店向けのデモ用初期データ（肉豆腐・肉うどんのお店を想定した食材）
DEFAULT_INVENTORY = {
    "牛肉（こま切れ）": 8,
    "豆腐": 12,
    "うどん（ゆで麺）": 30,
    "長ねぎ": 6,
    "卵": 40,
    "かつお節": 3,
    "生ビール樽": 2,
}


def load_inventory():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return dict(DEFAULT_INVENTORY)


def save_inventory():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(inventory_data, f, ensure_ascii=False, indent=2)


inventory_data = load_inventory()


def update_stock(item_name: str, change: int) -> str:
    """在庫数を増減する。新しい品目は追加のときだけ登録できる。"""
    item_name = item_name.strip()
    if not item_name:
        return "品目名を入力してください。"
    if change == 0:
        return "数量は1以上を指定してください。"
    current = inventory_data.get(item_name)
    if current is None:
        if change < 0:
            return f"{item_name} は在庫データにないため、減らせません。"
        inventory_data[item_name] = change
        save_inventory()
        return f"{item_name} を新しく登録し、{change}個にしました。"
    if current + change < 0:
        return f"{item_name} の在庫は{current}個のため、{-change}個は減らせません。"
    inventory_data[item_name] = current + change
    save_inventory()
    verb = "追加し" if change > 0 else "減らし"
    return f"{item_name} を{abs(change)}個{verb}ました。現在の在庫数は{inventory_data[item_name]}個です。"


# ---- AIに相談するときに使うツール ----

@beta_tool
def check_inventory(item_name: str) -> str:
    """指定した品目の在庫数を確認する。

    Args:
        item_name: 確認したい品目名(例:豆腐)
    """
    stock = inventory_data.get(item_name)
    if stock is None:
        return f"{item_name} は在庫データに存在しません。"
    return f"{item_name} の在庫数は {stock} 個です。"


@beta_tool
def list_low_stock(threshold: int = 10) -> str:
    """在庫が指定数以下の品目を一覧表示する。

    Args:
        threshold: この数以下の品目を「少ない」とみなす基準値(デフォルト10)
    """
    low_items = {name: qty for name, qty in inventory_data.items() if qty <= threshold}
    if not low_items:
        return f"在庫数が{threshold}個以下の品目はありません。"
    lines = [f"{name}: {qty}個" for name, qty in low_items.items()]
    return "在庫が少ない品目:\n" + "\n".join(lines)


@beta_tool
def restock(item_name: str, quantity: int) -> str:
    """品目が入荷した際に在庫数を増やす。

    Args:
        item_name: 入荷した品目名
        quantity: 入荷した数量(1以上の整数)
    """
    if quantity <= 0:
        return f"入荷数量は1以上を指定してください(指定値: {quantity})。"
    return update_stock(item_name, quantity)


def get_client():
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


# ---- 画面 ----

st.title("在庫管理アシスタント")
st.write("仕入れや使った分を、品目と数量を選ぶだけで記録できます。（飲食店向けのデモです）")

# 1. 品目と数量で在庫を増減する
st.subheader("在庫を増やす・減らす")
with st.form("update_form", clear_on_submit=True):
    item = st.selectbox(
        "品目（一覧から選ぶ。文字を打つと絞り込めます）",
        options=sorted(inventory_data.keys()),
        index=None,
        placeholder="例：豆腐",
    )
    new_item = st.text_input("一覧にない品目を新しく登録する場合は、ここに品目名を入力", placeholder="例：キャベツ")
    action = st.radio("どちらにしますか", ["追加（仕入れ）", "減らす（使った・廃棄）"], horizontal=True)
    qty = st.number_input("数量", min_value=1, value=1, step=1)
    submitted = st.form_submit_button("反映する")


def check_new_item(name: str):
    """新しい品目名を確かめる。問題があれば理由の文を返す。"""
    if name in inventory_data:
        return None
    similar = [existing for existing in inventory_data if existing.startswith(name)]
    if similar:
        return f"「{name}」は、すでにある「{similar[0]}」の書きかけかもしれません。一覧から選ぶか、品目名を最後まで入力してください。"
    return None


if submitted:
    new_item = new_item.strip()
    if item and new_item:
        st.warning("一覧から選ぶか、新しい品目名を入力するか、どちらか1つにしてください。")
    elif not item and not new_item:
        st.warning("品目を一覧から選ぶか、新しい品目名を入力してください。")
    elif new_item and check_new_item(new_item):
        st.warning(check_new_item(new_item))
    else:
        target = item or new_item
        change = int(qty) if action.startswith("追加") else -int(qty)
        result = update_stock(target, change)
        st.session_state.last_result = result
        st.rerun()

if "last_result" in st.session_state:
    st.info(st.session_state.last_result)

# 2. 在庫一覧
st.subheader("今の在庫")
threshold = st.number_input("この数以下を「少ない」として表示", min_value=0, value=5, step=1)
rows = [
    {"品目": name, "在庫数": qty_, "状態": "少ない" if qty_ <= threshold else ""}
    for name, qty_ in sorted(inventory_data.items())
]
st.table(rows)

if st.button("デモの在庫を初期の状態に戻す"):
    inventory_data.clear()
    inventory_data.update(DEFAULT_INVENTORY)
    save_inventory()
    st.session_state.pop("last_result", None)
    st.rerun()

st.caption("※ このデモの在庫データは、開いた人どうしで共有されます。実際のお店の情報は入力しないでください。")

# 3. AIに相談する（任意）
with st.expander("AIに在庫のことを聞く（任意）"):
    st.write("「在庫が少ないものは？」「豆腐の在庫は？」のように、文章で聞くこともできます。")
    client = get_client()
    if client is None:
        st.write("（AIの設定がないため、この機能は使えません）")
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            with st.chat_message(role):
                if isinstance(content, str):
                    st.write(content)
                else:
                    for block in content:
                        if getattr(block, "type", None) == "text":
                            st.write(block.text)

        user_input = st.chat_input("例：在庫が少ないものは？")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            runner = client.beta.messages.tool_runner(
                model="claude-sonnet-5",
                max_tokens=1024,
                tools=[check_inventory, list_low_stock, restock],
                messages=st.session_state.messages,
            )
            last_message = None
            for message in runner:
                last_message = message
            st.session_state.messages.append({"role": "assistant", "content": last_message.content})
            st.rerun()
