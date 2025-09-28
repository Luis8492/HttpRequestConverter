# HttpRequestConverter

`http_request_tool_converter.py` は、Burp Suite などで取得した HTTP リクエストの生データを、セキュリティ検査ツールである **wfuzz** および **sqlmap** のコマンドに変換するシンプルなスクリプトです。ヘッダーやボディを自動的に取り込み、実行可能なテンプレートを出力することで、手作業によるコマンド作成の手間を減らします。

## 主な機能

- HTTP リクエストファイルを解析し、メソッド・パス・ヘッダー・ボディを抽出
- `X-Forwarded-Proto` ヘッダーの有無からスキーム (http/https) を自動判定
- wfuzz 向けの `-X` や `-H` オプションを自動組み立て
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

## 使い方

1. Burp Suite やブラウザの開発者ツールから HTTP リクエストを **生の形式で保存** します。
2. 保存したファイルをスクリプトに渡し、ターゲットツール (`wfuzz` または `sqlmap`) を指定します。

```bash
python3 http_request_tool_converter.py --tool wfuzz request.txt
python3 http_request_tool_converter.py --tool sqlmap request.txt
```

実行すると、指定したツールのサンプルコマンドが出力されます。必要に応じて、攻撃ポイントに `FUZZ` もしくは `*` を挿入してから使用してください。

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

## トラブルシューティング

- **`[!] Error: ...` と表示される**: 入力ファイルのフォーマットが正しいか確認してください。少なくとも 1 行目に `METHOD PATH HTTP/VERSION` の形式が必要です。
- **https URL に変換されない**: リクエストに `X-Forwarded-Proto: https` ヘッダーを含めると、自動的に https が選択されます。
- **生成されたコマンドがそのまま実行できない**: ツールによってはパラメータをエスケープする必要がある場合があります。出力結果を参考に調整してください。

## ライセンス

本リポジトリのライセンスが未指定の場合、利用時はリポジトリ作者に確認してください。

