# Discord Bot Launcher

Discord botのzipファイルをドラッグアンドドロップして、tokenを入力するだけでbotを稼働させられるGUIプログラムです。https://github.com/akiii2024/easy_bot_createrと一緒に使うことを想定しています

## 🚀 クイックスタート（推奨）

### 1. 実行ファイルをダウンロード
[Releases](https://github.com/your-username/DiscordBotLauncher/releases) から最新の `BotLauncher.exe` をダウンロードしてください。

### 2. 実行
ダウンロードした `BotLauncher.exe` をダブルクリックして起動します。

### 3. Botを起動
1. Discord botのzipファイルをウィンドウにドラッグアンドドロップ
2. Discord Bot Tokenを入力
3. 「Botを起動」ボタンをクリック

**これだけでDiscord botが起動します！**

## 📋 機能

- **🎯 ワンクリック起動**: zipファイルをドラッグ&ドロップするだけ
- **🔐 Token検証**: Tokenの形式を事前にチェック
- **⚙️ 自動環境構築**: 
  - zipファイルを自動解凍
  - 仮想環境を自動作成
  - 依存関係を自動インストール
- **🔑 環境変数管理**: .env.exampleを基に.envファイルを自動生成
- **📊 リアルタイムログ**: botの出力をGUI上で確認
- **🎮 簡単制御**: ボタン一つでbotの起動/停止
- **❌ エラー詳細表示**: 問題を分かりやすく説明

## 📦 Botのzipファイル要件

Discord botのzipファイルには以下のファイルが含まれている必要があります：

### 必須ファイル
- `main.py` - botのメインファイル（エントリーポイント）

### 推奨ファイル
- `requirements.txt` - 必要な依存関係のリスト
- `.env.example` - 環境変数のテンプレート

### 例：zipファイルの構造
```
my-discord-bot.zip
├── main.py
├── requirements.txt
├── .env.example
├── config.py
└── cogs/
    ├── __init__.py
    └── general.py
```

## 🔧 使用方法

### 基本的な使い方

1. **Botファイルの準備**
   - Discord botのソースコードをzipファイルにまとめる
   - `main.py`がエントリーポイントになっていることを確認

2. **Tokenの取得**
   - [Discord Developer Portal](https://discord.com/developers/applications) でBotを作成
   - Bot Tokenをコピー

3. **Botの起動**
   - `BotLauncher.exe`を起動
   - zipファイルをドラッグ&ドロップ
   - Tokenを入力
   - 「Botを起動」をクリック

### 追加のAPIキー・トークン

Botが外部APIを使用する場合：

1. zipファイル内の`.env.example`を確認
2. 必要なAPIキーやトークンを入力欄に入力
3. Botを起動

## 🛠️ トラブルシューティング

### よくある問題

#### Tokenエラー（401 Unauthorized）
- **原因**: Tokenが間違っている、または無効
- **解決方法**:
  1. Discord Developer Portalで正しいTokenをコピー
  2. Tokenに余分な空白や改行がないか確認
  3. 必要に応じて新しいTokenを生成

#### main.pyが見つからない
- **原因**: zipファイル内にmain.pyが含まれていない
- **解決方法**: zipファイル内にmain.pyがあることを確認

#### 依存関係のインストールエラー
- **原因**: requirements.txtの内容に問題がある
- **解決方法**: requirements.txtの内容を確認し、修正

#### 権限エラー
- **原因**: ファイルアクセス権限の問題
- **解決方法**: プログラムを管理者権限で実行

### エラーログの確認

エラーが発生した場合、`BotLauncher.exe`と同じフォルダに`error_log.txt`が作成されます。このファイルを確認して詳細なエラー情報を確認できます。

## 🔒 セキュリティ

- **Tokenの管理**: Tokenは安全に管理し、他人と共有しないでください
- **環境変数**: 機密情報は環境変数として管理されます
- **一時ファイル**: botは一時ディレクトリで実行され、停止時に自動クリーンアップされます

## 🖥️ 対応環境

- **OS**: Windows 10
- **Python**: 3.12
- 上記の環境で動作確認しています。

## 👨‍💻 開発者向け情報

### ソースコードから実行

Python環境で直接実行する場合：

```bash
# 依存関係をインストール
pip install -r requirements.txt

# プログラムを起動
python bot_launcher.py
```

### exeファイルのビルド

```bash
# ビルドスクリプトを実行
python build_exe.py
```

ビルドされたファイルは`dist/BotLauncher.exe`に出力されます。

### 必要な依存関係

- Python 3.8以上
- tkinterdnd2==0.3.0
- PyInstaller（exe化時）


## 📞 サポート

問題が発生した場合や質問がある場合は、以下の方法でお問い合わせください：

- **Discord**: [aki_2024]
- **Twitter**: [@aki_2024]

---

**注意**: このソフトウェアはDiscordの利用規約に従って使用してください。Botの使用に関する責任は利用者にあります。

---

*このREADMEはAIによって生成されました。* 
