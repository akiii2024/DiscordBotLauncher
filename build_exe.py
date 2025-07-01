#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Launcher のexe化スクリプト
"""

import os
import sys
import subprocess
import shutil

def build_with_spec():
    """specファイルを使用してビルド（推奨）"""
    print("specファイルを使用してビルド中...")
    cmd = [sys.executable, "-m", "PyInstaller", "BotLauncher.spec"]
    subprocess.run(cmd, check=True)

def build_with_command():
    """コマンドラインオプションを使用してビルド"""
    # tkinterdnd2のパッケージ情報を取得
    try:
        import tkinterdnd2
        tkinterdnd2_path = os.path.dirname(tkinterdnd2.__file__)
        print(f"tkinterdnd2のパス: {tkinterdnd2_path}")
    except ImportError:
        print("tkinterdnd2が見つかりません")
        return False
    
    print("コマンドラインオプションを使用してビルド中...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # 単一ファイルにまとめる
        "--windowed",  # コンソールウィンドウを非表示
        "--name=BotLauncher",  # 実行ファイル名
        f"--additional-hooks-dir={os.getcwd()}",  # hookディレクトリを指定
        "--hidden-import=tkinterdnd2",  # tkinterdnd2を明示的にインポート
        "--hidden-import=tkinterdnd2.tkdnd",
        "--hidden-import=tkinterdnd2.TkinterDnD",
        "--hidden-import=multiprocessing",  # multiprocessingを明示的にインポート
        "--hidden-import=multiprocessing.spawn",
        "--hidden-import=multiprocessing.freeze_support",
        f"--add-data={tkinterdnd2_path};tkinterdnd2",  # tkinterdnd2のデータを追加
        "bot_launcher.py"
    ]
    subprocess.run(cmd, check=True)
    return True

def main():
    print("Bot Launcher のexe化を開始します...")
    
    # 必要なパッケージをインストール
    print("必要なパッケージをインストール中...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "tkinterdnd2"], check=True)
    
    # Discord bot関連の基本パッケージもインストール（exe内に含めるため）
    print("Discord bot関連パッケージをインストール中...")
    packages = [
        "discord.py",
        "py-cord",  # Py-Cordを使用している場合
        "python-dotenv",
        "aiohttp",
        "requests"
    ]
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"  - {package} をインストールしました")
        except:
            print(f"  - {package} のインストールに失敗しました（スキップ）")
    
    # 既存のビルドファイルをクリーンアップ
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # ビルド方法を選択
    build_method = input("ビルド方法を選択してください (1: specファイル [推奨], 2: コマンドライン): ").strip()
    
    try:
        if build_method == "1" or build_method == "":
            # specファイルが存在するかチェック
            if os.path.exists("BotLauncher.spec"):
                build_with_spec()
            else:
                print("BotLauncher.specが見つかりません。コマンドライン方式を使用します。")
                if not build_with_command():
                    return 1
        elif build_method == "2":
            if not build_with_command():
                return 1
        else:
            print("無効な選択です。specファイルを使用します。")
            if os.path.exists("BotLauncher.spec"):
                build_with_spec()
            else:
                print("BotLauncher.specが見つかりません。コマンドライン方式を使用します。")
                if not build_with_command():
                    return 1
        
        print("ビルドが完了しました！")
        print("実行ファイルは dist/BotLauncher.exe にあります。")
        
        # エラーログファイルの場所を表示
        print("\n注意: エラーが発生した場合は、実行ファイルと同じフォルダに error_log.txt が作成されます。")
        
        # tkinterdnd2の問題に関する追加情報
        print("\ntkinterdnd2に関する注意:")
        print("- exe化後にドラッグアンドドロップが動作しない場合、ファイル選択ボタンを使用してください")
        print("- Windows Defenderなどのセキュリティソフトウェアがexeファイルをブロックする可能性があります")
        
    except subprocess.CalledProcessError as e:
        print(f"ビルドに失敗しました: {e}")
        print("\nトラブルシューティング:")
        print("1. 仮想環境を使用している場合は、仮想環境を有効化してから実行してください")
        print("2. tkinterdnd2のバージョンが古い可能性があります: pip install --upgrade tkinterdnd2")
        print("3. PyInstallerのバージョンを更新してください: pip install --upgrade pyinstaller")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 