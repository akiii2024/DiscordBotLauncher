# Discord Bot Launcher

Discord botのzipファイルをドラッグアンドドロップして、tokenを入力するだけでbotを稼働させられるGUIプログラムです。

## 必要条件

- Python 3.8以上
- tkinterdnd2ライブラリ

## インストール

1. 必要な依存関係をインストール：
```bash
pip install -r requirements.txt
```

## 使い方

1. プログラムを起動：
```bash
python bot_launcher.py
```

2. 起動したGUIウィンドウにDiscord botのzipファイルをドラッグアンドドロップ

3. Discord Bot Tokenを入力（「Token検証」ボタンで形式を事前確認可能）

4. 「Botを起動」ボタンをクリック

## 機能

- **ドラッグアンドドロップ対応**: zipファイルを簡単に読み込み
- **Token検証機能**: Tokenの形式を事前にチェック
- **自動環境構築**: 
  - zipファイルを一時ディレクトリに解凍
  - 仮想環境を自動作成
  - requirements.txtから依存関係を自動インストール
- **Token管理**: .env.exampleを基に.envファイルを自動生成
- **リアルタイムログ表示**: botの出力をGUI上で確認可能
- **簡単な起動/停止**: ボタン一つでbotの制御が可能
- **エラー詳細表示**: Tokenエラーなどの問題を分かりやすく説明

## zipファイルの要件

Discord botのzipファイルには以下のファイルが含まれている必要があります：

- `main.py` - botのメインファイル
- `requirements.txt` - 必要な依存関係のリスト
- `.env.example` - 環境変数のテンプレート（オプション）

## トラブルシューティング

### Tokenエラー（401 Unauthorized）が発生する場合

1. **Tokenの確認**
   - Discord Developer Portalで正しいTokenをコピーしているか確認
   - Tokenに余分な空白や改行が含まれていないか確認

2. **Botの設定確認**
   - Botが正しく作成されているか確認
   - Botに適切な権限が付与されているか確認
   - Botがサーバーに招待されているか確認

3. **Tokenの再生成**
   - Discord Developer Portalで新しいTokenを生成
   - 古いTokenは無効になるため、新しいTokenを使用

4. **Botの権限設定**
   - Botに必要な権限（Send Messages, Read Message History等）が付与されているか確認
   - Botの権限がサーバーで有効になっているか確認

### その他のよくある問題

- **main.pyが見つからない**: zipファイル内にmain.pyが含まれているか確認
- **依存関係のインストールエラー**: requirements.txtの内容を確認
- **権限エラー**: プログラムを管理者権限で実行してみる

## 注意事項

- botは一時ディレクトリで実行され、停止時に自動的にクリーンアップされます
- 各botごとに独立した仮想環境が作成されます
- Windows、macOS、Linuxに対応しています
- Tokenは安全に管理し、他人と共有しないでください 