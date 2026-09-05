from mcp.server import MCPServer
import json
import os

mcp = MCPServer("inventory-server")

DATA_FILE = "inventory_data.json"

def load_inventory():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "シャンプー": 42,
        "洗剤": 5,
        "歯ブラシ": 120,
    }

def save_inventory():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(inventory_data, f, ensure_ascii=False, indent=2)

inventory_data = load_inventory()

@mcp.tool()
def check_inventory(item_name: str) -> str:
    """指定した商品の在庫数を確認する。

    Args:
        item_name: 確認したい商品名(例:シャンプー)
    """
    stock = inventory_data.get(item_name)
    if stock is None:
        return f"{item_name} は在庫データに存在しません。"
    return f"{item_name} の在庫数は {stock} 個です。"

@mcp.tool()
def list_low_stock(threshold: int = 10) -> str:
    """在庫が指定数以下の商品を一覧表示する。

    Args:
        threshold: この数以下の商品を「少ない」とみなす基準値(デフォルト10)
    """
    low_items = {name: qty for name, qty in inventory_data.items() if qty <= threshold}
    if not low_items:
        return f"在庫数が{threshold}個以下の商品はありません。"
    lines = [f"{name}: {qty}個" for name, qty in low_items.items()]
    return "在庫が少ない商品:\n" + "\n".join(lines)

@mcp.tool()
def restock(item_name: str, quantity: int) -> str:
    """商品が入荷した際に在庫数を増やす。

    Args:
        item_name: 入荷した商品名
        quantity: 入荷した数量(1以上の整数)
    """
    if item_name not in inventory_data:
        return f"{item_name} は在庫データに存在しません。先に商品を登録してください。"
    if quantity <= 0:
        return f"入荷数量は1以上を指定してください(指定値: {quantity})。"
    inventory_data[item_name] += quantity
    save_inventory()
    return f"{item_name} を{quantity}個入荷しました。現在の在庫数は{inventory_data[item_name]}個です。"

if __name__ == "__main__":
    mcp.run(transport="stdio")