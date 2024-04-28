# Tact File Downloader

東海国立大学機構の学習支援システム TACT から講義資料などのファイルを一括でダウンロードするためのツールです。

## Requirements

-   [rye](https://rye-up.com) (macOS でのみ動作確認済み。他の OS でも同様に動作するはずです。)

## Installation

1. このリポジトリをクローンしてください。
    ```
    git clone https://github.com/tanashou/tact-file-downloader.git
    ```

## Setup

1. `rye`を[こちら](https://rye-up.com/guide/installation/)のインストール方法に従ってインストールしてください。

1. プロジェクトのディレクトリに移動した後に次のコマンドを実行してください。各種依存パッケージなどがインストールされます。

    ```
    rye sync
    ```

1. TACT のログインに必要なユーザー名やパスワードを環境変数として登録してください。それぞれの環境変数名は次のようにしてください。
   | 変数名 | 値 |
   | ------------ | ---------------- |
   | TACT_USERNAME | TACTのユーザー名 |
   | TACT_PASSWORD | TACTのパスワード |

## TODO

-   ワンタイムパスワードの自動取得。入力する手間を省く。
-   ファイルをダウンロードしたい講義の選択。お気に入りの講義のみを取得するなどしたい。
