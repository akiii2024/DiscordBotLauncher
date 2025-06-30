#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Launcher のexe化スクリプト
"""

import os
import sys
import subprocess
import shutil

def main():
    print("Bot Launcher のexe化を開始します...")
    
    # 必要なパッケージをインストール
    print("必要なパッケージをインストール中...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "tkinterdnd2"], check=True)
    
    # 既存のビルドファイルをクリーンアップ
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # PyInstallerでビルド
    print("PyInstallerでビルド中...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # 単一ファイルにまとめる
        "--windowed",  # コンソールウィンドウを非表示
        "--name=BotLauncher",  # 実行ファイル名
        "--add-data=hook-tkinterdnd2.py;.",  # hookファイルを追加
        "bot_launcher.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("ビルドが完了しました！")
        print("実行ファイルは dist/BotLauncher.exe にあります。")
        
        # エラーログファイルの場所を表示
        print("\n注意: エラーが発生した場合は、実行ファイルと同じフォルダに error_log.txt が作成されます。")
        
    except subprocess.CalledProcessError as e:
        print(f"ビルドに失敗しました: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 