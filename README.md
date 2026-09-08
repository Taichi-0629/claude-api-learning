# Claude API Learning



Claude API(Anthropic API)を基礎から学びながら、実務を想定したミニプロジェクトを作成した学習記録です。



## 学習の流れ



| ファイル | 内容 |

|---|---|

| `hello.py` | Claude APIへの最初のリクエスト(基本的な使い方) |

| `chatbot.py` | 会話履歴を保持するチャットボット(複数ターンの対話) |

| `inventory\_bot.py` | Tool Use(Function Calling)を使い、在庫データを参照して回答するチャットボット |

| `inventory\_mcp\_server.py` | 上記のツールをMCP(Model Context Protocol)サーバーとして独立させ、外部クライアントから呼び出せる形に発展させたもの |

| `shift_scheduler.py` | プロンプト設計のみで、スタッフの希望シフトと必要人数から調整案を生成するアプリ(Tool Useを使わない生成・推論タスクの例) |



## inventory\_mcp\_server.py の機能



小売業務を想定した在庫管理MCPサーバーです。



\- `check\_inventory`:商品名を指定して在庫数を確認

\- `list\_low\_stock`:在庫が少ない商品を一覧表示

\- `restock`:入荷処理(不正な数量入力はエラーとして弾く)

\- 在庫データはJSONファイルに永続化し、サーバー再起動後も保持



\[MCP Inspector](https://github.com/modelcontextprotocol/inspector)を使い、実際にツール呼び出しが正しく動作することを確認済みです。

## shift_scheduler.py の機能

小売店のシフト調整を想定したミニアプリです。

- 各スタッフの希望勤務曜日と、曜日ごとの必要人数を入力
- Claudeが制約を踏まえてシフト案を生成
- 希望が競合する箇所は、理由と代替案(交代提案など)まで提示

Tool Useではなく、プロンプト設計だけで複雑な制約条件を扱う例として、`inventory_mcp_server.py`とは異なるアプローチを示しています。



## 使用技術



\- Python

\- Anthropic SDK (`anthropic`)

\- Model Context Protocol (`mcp`)



## 今後の展望



小売業界での実務経験を活かし、業務課題を解決するAIエージェント・MCPサーバーの開発案件獲得を目指しています。

