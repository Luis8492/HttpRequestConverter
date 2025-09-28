# HttpRequestConverter

`http_request_tool_converter.py` は、Burp Suite などで取得した HTTP リクエストの生データを、セキュリティ検査ツールのコマンドに変換するシンプルなスクリプトです。ヘッダーやボディを自動的に取り込み、実行可能なテンプレートを出力することで、手作業によるコマンド作成の手間を減らします。変換ロジックはモジュールとして分離されており、wfuzz や sqlmap などのツールごとに独立したビルダーを追加できる構造になっています。

## 主な機能

- HTTP リクエストファイルを解析し、メソッド・パス・ヘッダー・ボディを抽出
- `X-Forwarded-Proto` ヘッダーの有無からスキーム (http/https) を自動判定
- wfuzz 向けの `-X` や `-H` オプションを自動組み立て
- ffuf 向けに `-w` `-H` `-d` などのテンプレートを生成
- curl 向けに `-X` や `-H`, `--data-raw` を組み合わせたリクエスト例を出力
- sqlmap 向けにメソッド指定、リクエストボディ、主要ヘッダー (`User-Agent`, `Cookie`, `Referer`, `Host`) などを適切に配置
- 追加ヘッダーも `--headers` オプションでまとめて反映
- 生成後の調整ポイント（FUZZ や `*` の挿入箇所）をメッセージで案内

## 必要要件

- Python 3.8 以上
- 追加の外部ライブラリは不要（標準ライブラリのみを使用）

wfuzz および sqlmap の実行には各ツールのインストールが別途必要です。

## セットアップ

```bash
git clone https://github.com/<your-account>/HttpRequestConverter.git
cd HttpRequestConverter
python3 --version  # Python 3.8 以上であることを確認
```

## プロジェクト構成

```
.
├── http_request_tool_converter.py  # CLI エントリポイント
└── tool_builders/
    ├── __init__.py                # レジストリと共有データクラス
    ├── sqlmap.py                  # sqlmap 用コマンドビルダー
    └── wfuzz.py                   # wfuzz 用コマンドビルダー
```

`tool_builders` パッケージは、対象ツールごとの「ビルダー」モジュールを登録する仕組みを提供します。CLI から `--tool` で指定できる値は、レジストリに登録されたビルダーに応じて自動的に増減します。

## 使い方

1. Burp Suite やブラウザの開発者ツールから HTTP リクエストを **生の形式で保存** します。
2. 保存したファイルをスクリプトに渡し、`--tool` オプションで変換先を指定します。

```bash
# 例: wfuzz 形式に変換
python3 http_request_tool_converter.py --tool wfuzz request.txt

# 例: ffuf 形式に変換
python3 http_request_tool_converter.py --tool ffuf request.txt

# 例: curl コマンドに変換
python3 http_request_tool_converter.py --tool curl request.txt

# 例: sqlmap 形式に変換
python3 http_request_tool_converter.py --tool sqlmap request.txt
```

実行すると、指定したツールのサンプルコマンドが出力されます。必要に応じて、攻撃ポイントに `FUZZ` や `*` を挿入してから使用してください。

## HTTP リクエストファイルの例

```
POST /search HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Cookie: session=abcd
Content-Type: application/x-www-form-urlencoded

query=test
```

上記リクエストを `request.txt` として保存し、wfuzz 用に変換した場合の出力例:

```
===== wfuzz コマンド =====
wfuzz -c -w /usr/share/seclists/Fuzzing/special-chars.txt -u "http://example.com/search" -X POST -d "query=test" -H "User-Agent: Mozilla/5.0" -H "Cookie: session=abcd" -H "Content-Type: application/x-www-form-urlencoded"
👉 Replace value with 'FUZZ' to test injection points.
```

sqlmap を指定した場合の出力例:

```
===== sqlmap コマンド =====
sqlmap -u "http://example.com/search" --method=POST --data="query=test" -A "Mozilla/5.0" --cookie="session=abcd" --headers="Content-Type: application/x-www-form-urlencoded" --level=5 --risk=3
👉 Insert '*' at desired injection point (e.g., TrackingId=abc*).
```

## ツールビルダーの拡張

モジュール化された構成により、新しいツール向けのコマンドテンプレートを簡単に追加できます。

1. `tool_builders/` ディレクトリに `<tool_name>.py` を作成します。
2. `ToolTemplate` と `registry` をインポートし、`build(method, url, headers, body)`
   関数を実装して `registry.register("<tool_name>", build)` を呼び出します。
3. 新しいモジュールを追加した状態でスクリプトを実行すると、`--tool <tool_name>` が選択肢に加わります。

実装例は既存の `wfuzz.py` や `sqlmap.py` を参照してください。`ToolTemplate` には表示タイトル・生成コマンド・補足メッセージを渡せます。

## トラブルシューティング

- **`[!] Error: ...` と表示される**: 入力ファイルのフォーマットが正しいか確認してください。少なくとも 1 行目に `METHOD PATH HTTP/VERSION` の形式が必要です。
- **https URL に変換されない**: リクエストに `X-Forwarded-Proto: https` ヘッダーを含めると、自動的に https が選択されます。
- **生成されたコマンドがそのまま実行できない**: ツールによってはパラメータをエスケープする必要がある場合があります。出力結果を参考に調整してください。

## ライセンス

本リポジトリのライセンスが未指定の場合、利用時はリポジトリ作者に確認してください。

