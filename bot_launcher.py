import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import zipfile
import os
import subprocess
import threading
import shutil
import tempfile
import sys
import re
from pathlib import Path
from multiprocessing import freeze_support
import importlib.util
import io
from contextlib import redirect_stdout, redirect_stderr

# tkinterdnd2を安全にインポート
try:
    import tkinterdnd2 as dnd
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    dnd = None
    print("警告: tkinterdnd2が利用できません。ドラッグアンドドロップ機能は無効になります。")


class BotLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Bot Launcher")
        self.root.geometry("800x700")  # 高さを少し増やす
        
        # tkinterdnd2の利用可能性をチェック
        self.dnd_available = DND_AVAILABLE and dnd is not None
        
        # tkinterのsplitlistメソッドを準備
        if hasattr(root, 'tk') and not hasattr(root.tk, 'splitlist'):
            root.tk.splitlist = lambda data: data.split() if isinstance(data, str) else data
        
        # bot実行用の変数
        self.bot_process = None
        self.bot_thread = None  # 内蔵実行用のスレッド
        self.bot_dir = None
        self.is_running = False
        self.env_vars = {}  # 追加の環境変数を保存
        self.use_embedded_python = True  # 内蔵Pythonを使用するかどうか
        
        self.setup_ui()
        
    def setup_ui(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ドラッグアンドドロップエリア
        self.drop_frame = ttk.LabelFrame(main_frame, text="Botファイル（.zip）をドロップ", padding="20")
        self.drop_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.drop_label = ttk.Label(self.drop_frame, text="ここにzipファイルをドラッグアンドドロップ", 
                                   background="lightgray", anchor="center")
        self.drop_label.pack(fill=tk.BOTH, expand=True, ipadx=50, ipady=30)
        
        # ドロップ機能の設定
        if self.dnd_available:
            try:
                self.drop_label.drop_target_register(dnd.DND_FILES)
                self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
                print("ドラッグアンドドロップ機能を有効化しました")
            except Exception as e:
                print(f"ドラッグアンドドロップ機能の設定に失敗: {e}")
                self.dnd_available = False
                self.drop_label.config(text="ドラッグアンドドロップ機能は利用できません\nファイル選択ボタンを使用してください", 
                                     background="lightyellow")
                # ファイル選択ボタンを追加
                select_button = ttk.Button(self.drop_frame, text="ファイルを選択", command=self.select_file)
                select_button.pack(pady=10)
        else:
            # ドラッグアンドドロップが利用できない場合
            self.drop_label.config(text="ドラッグアンドドロップ機能は利用できません\nファイル選択ボタンを使用してください", 
                                 background="lightyellow")
            # ファイル選択ボタンを追加
            select_button = ttk.Button(self.drop_frame, text="ファイルを選択", command=self.select_file)
            select_button.pack(pady=10)
        
        # ファイル情報表示
        self.file_label = ttk.Label(main_frame, text="ファイル: 未選択")
        self.file_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Token入力エリア
        token_frame = ttk.Frame(main_frame)
        token_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(token_frame, text="Discord Bot Token:").pack(side=tk.LEFT)
        self.token_entry = ttk.Entry(token_frame, width=50, show="*")
        self.token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Token検証ボタン
        self.verify_button = ttk.Button(token_frame, text="Token検証", command=self.verify_token)
        self.verify_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Tokenステータス表示
        self.token_status = ttk.Label(main_frame, text="", foreground="gray")
        self.token_status.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # 追加の環境変数エリア
        self.env_frame = ttk.LabelFrame(main_frame, text="追加のAPIキー・トークン", padding="5")
        self.env_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 環境変数入力用のキャンバスとスクロールバー
        self.env_canvas = tk.Canvas(self.env_frame, height=100)
        self.env_scrollbar = ttk.Scrollbar(self.env_frame, orient="vertical", command=self.env_canvas.yview)
        self.env_scrollable_frame = ttk.Frame(self.env_canvas)
        
        self.env_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.env_canvas.configure(scrollregion=self.env_canvas.bbox("all"))
        )
        
        self.env_canvas.create_window((0, 0), window=self.env_scrollable_frame, anchor="nw")
        self.env_canvas.configure(yscrollcommand=self.env_scrollbar.set)
        
        self.env_canvas.pack(side="left", fill="both", expand=True)
        self.env_scrollbar.pack(side="right", fill="y")
        
        # 環境変数エントリを格納するリスト
        self.env_entries = {}
        
        # ボタンエリア
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Botを起動", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Botを停止", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # ステータス表示
        self.status_label = ttk.Label(main_frame, text="ステータス: 待機中", foreground="gray")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)
        
        # ログ表示エリア
        log_frame = ttk.LabelFrame(main_frame, text="ログ", padding="5")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # グリッドの重み設定
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if file_path.lower().endswith('.zip'):
                self.selected_zip = file_path
                self.file_label.config(text=f"ファイル: {os.path.basename(file_path)}")
                self.log_message(f"ファイルを選択しました: {os.path.basename(file_path)}")
                self.drop_label.config(text="✓ ファイルが選択されました", background="lightgreen")
                
                # 一時的に解凍して.env.exampleを確認
                self.check_env_example(file_path)
            else:
                messagebox.showerror("エラー", "zipファイルを選択してください")
                
    def check_env_example(self, zip_path):
        """zipファイル内の.env.exampleを確認して必要な環境変数を特定"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # .env.exampleファイルを探す
                env_example_files = [f for f in zip_ref.namelist() if f.endswith('.env.example')]
                
                if env_example_files:
                    # 最初に見つかった.env.exampleを読み込み
                    with zip_ref.open(env_example_files[0]) as f:
                        content = f.read().decode('utf-8')
                    
                    # 環境変数を解析
                    self.parse_env_example(content)
                else:
                    # .env.exampleが見つからない場合、環境変数エリアをクリア
                    self.clear_env_entries()
                    
        except Exception as e:
            self.log_message(f".env.exampleの確認中にエラーが発生しました: {str(e)}")
            self.clear_env_entries()
            
    def parse_env_example(self, content):
        """環境変数ファイルの内容を解析してUIを更新"""
        # 既存のエントリをクリア
        self.clear_env_entries()
        
        lines = content.split('\n')
        env_vars = []
        
        for line in lines:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                key = line.split('=')[0].strip()
                value = line.split('=', 1)[1].strip()
                
                # Discord Token以外の環境変数を対象とする
                if not any(token_key in key.upper() for token_key in ['DISCORD_TOKEN', 'TOKEN']):
                    env_vars.append((key, value))
        
        # UIに環境変数エントリを追加
        if env_vars:
            self.log_message(f"追加の環境変数が見つかりました: {len(env_vars)}個")
            for i, (key, default_value) in enumerate(env_vars):
                self.add_env_entry(key, default_value)
        else:
            self.log_message("追加の環境変数は見つかりませんでした")
            
    def clear_env_entries(self):
        """環境変数エントリをクリア"""
        for widget in self.env_scrollable_frame.winfo_children():
            widget.destroy()
        self.env_entries.clear()
        
    def add_env_entry(self, key, default_value):
        """環境変数エントリを追加"""
        frame = ttk.Frame(self.env_scrollable_frame)
        frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text=f"{key}:").pack(side=tk.LEFT)
        entry = ttk.Entry(frame, width=40, show="*" if "KEY" in key.upper() or "TOKEN" in key.upper() else "")
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # プレースホルダーを設定
        if default_value and default_value != "YOUR_" + key:
            entry.insert(0, default_value)
        
        self.env_entries[key] = entry
        
    def get_env_vars(self):
        """入力された環境変数を取得"""
        env_vars = {}
        for key, entry in self.env_entries.items():
            value = entry.get().strip()
            if value:
                env_vars[key] = value
        return env_vars
        
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def validate_token_format(self, token):
        """Tokenの形式を検証"""
        # 英数字のみの判定
        pattern = r'^[A-Za-z0-9_.]+$'
        return bool(re.match(pattern, token))
        
    def verify_token(self):
        """Tokenの形式を検証"""
        token = self.token_entry.get().strip()
        
        if not token:
            self.token_status.config(text="Tokenが入力されていません", foreground="red")
            return
            
        if not self.validate_token_format(token):
            self.token_status.config(text="Tokenの形式が正しくありません", foreground="red")
            messagebox.showwarning("Token形式エラー", 
                                 "Discord Bot Tokenの形式が正しくありません。\n"
                                 "正しい形式: 数字.英数字.英数字\n"
                                 "例: 1234567890.ABCDEFGHIJKLMNOPQRSTUVWXYZ.abcdef")
            return
            
        self.token_status.config(text="✓ Token形式は正しいです（実際の有効性は起動時に確認されます）", foreground="green")
        
    def extract_zip(self, zip_path):
        """zipファイルを一時ディレクトリに解凍"""
        temp_dir = tempfile.mkdtemp(prefix="discord_bot_")
        self.log_message(f"一時ディレクトリを作成: {temp_dir}")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            self.log_message("zipファイルを解凍しました")
            return temp_dir
        except Exception as e:
            self.log_message(f"解凍エラー: {str(e)}")
            shutil.rmtree(temp_dir)
            return None
            
    def create_env_file(self, bot_dir, token):
        """環境変数ファイルを作成"""
        env_path = os.path.join(bot_dir, '.env')
        env_example_path = os.path.join(bot_dir, '.env.example')
        
        # 追加の環境変数を取得
        additional_env_vars = self.get_env_vars()
        
        # .env.exampleが存在する場合、それをベースに作成
        if os.path.exists(env_example_path):
            with open(env_example_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # TOKEN行を探して置換
            lines = content.split('\n')
            new_lines = []
            token_found = False
            
            for line in lines:
                if 'TOKEN' in line and '=' in line:
                    key = line.split('=')[0].strip()
                    new_lines.append(f"{key}={token}")
                    token_found = True
                else:
                    new_lines.append(line)
            
            if not token_found:
                new_lines.append(f"DISCORD_TOKEN={token}")
                
            # 追加の環境変数を追加
            for key, value in additional_env_vars.items():
                new_lines.append(f"{key}={value}")
                
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
        else:
            # .env.exampleがない場合、シンプルな.envを作成
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(f"DISCORD_TOKEN={token}\n")
                f.write(f"TOKEN={token}\n")  # 両方の形式に対応
                
                # 追加の環境変数を追加
                for key, value in additional_env_vars.items():
                    f.write(f"{key}={value}\n")
                
        self.log_message(".envファイルを作成しました")
        if additional_env_vars:
            self.log_message(f"追加の環境変数を設定しました: {', '.join(additional_env_vars.keys())}")
        
    def get_python_executable(self):
        """適切なPython実行ファイルパスを取得"""
        # exe環境の場合
        if getattr(sys, 'frozen', False):
            # システムのPythonを探す
            if os.name == 'nt':  # Windows
                # システムPATHからpython.exeを探す
                for path in os.environ.get('PATH', '').split(os.pathsep):
                    python_exe = os.path.join(path, 'python.exe')
                    if os.path.exists(python_exe) and not python_exe == sys.executable:
                        return python_exe
                
                # よくあるPythonのインストール場所を確認
                common_paths = [
                    r"C:\Python39\python.exe",
                    r"C:\Python38\python.exe",
                    r"C:\Python37\python.exe",
                    r"C:\Python310\python.exe",
                    r"C:\Python311\python.exe",
                    r"C:\Python312\python.exe",
                    os.path.expanduser(r"~\AppData\Local\Programs\Python\Python39\python.exe"),
                    os.path.expanduser(r"~\AppData\Local\Programs\Python\Python310\python.exe"),
                    os.path.expanduser(r"~\AppData\Local\Programs\Python\Python311\python.exe"),
                    os.path.expanduser(r"~\AppData\Local\Programs\Python\Python312\python.exe"),
                ]
                
                for python_path in common_paths:
                    if os.path.exists(python_path):
                        return python_path
                
                # Pythonが見つからない場合はエラー
                return None
            else:
                # Linux/Mac
                return shutil.which('python3') or shutil.which('python')
        else:
            # 通常の環境
            return sys.executable
    
    def install_requirements(self, bot_dir):
        """requirements.txtから依存関係をインストール"""
        req_path = os.path.join(bot_dir, 'requirements.txt')
        
        # システムのPythonを取得
        system_python = self.get_python_executable()
        if not system_python:
            self.log_message("エラー: システムにPythonがインストールされていません")
            self.log_message("Pythonをインストールしてから再度実行してください")
            return None
            
        if os.path.exists(req_path):
            self.log_message("依存関係をインストール中...")
            try:
                # 仮想環境を作成
                venv_path = os.path.join(bot_dir, 'venv')
                subprocess.run([system_python, '-m', 'venv', venv_path], check=True)
                
                # 仮想環境のpythonとpipのパスを取得
                if os.name == 'nt':  # Windows
                    python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
                    pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
                else:  # Linux/Mac
                    python_path = os.path.join(venv_path, 'bin', 'python')
                    pip_path = os.path.join(venv_path, 'bin', 'pip')
                
                # pipをアップグレード
                subprocess.run([python_path, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                             capture_output=True, text=True)
                
                # 依存関係をインストール
                result = subprocess.run([pip_path, 'install', '-r', req_path], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log_message("依存関係のインストールが完了しました")
                    return python_path
                else:
                    self.log_message(f"インストールエラー: {result.stderr}")
                    return None
            except Exception as e:
                self.log_message(f"インストールエラー: {str(e)}")
                return None
        else:
            self.log_message("requirements.txtが見つかりません")
            # exe環境でもシステムのPythonを返す
            return system_python
            
    def start_bot(self):
        if not hasattr(self, 'selected_zip'):
            messagebox.showerror("エラー", "zipファイルを選択してください")
            return
            
        token = self.token_entry.get().strip()
        if not token:
            messagebox.showerror("エラー", "Tokenを入力してください")
            return
            
        # Token形式を再検証
        if not self.validate_token_format(token):
            messagebox.showerror("エラー", "Tokenの形式が正しくありません")
            return
            
        # 追加の環境変数の必須チェック
        additional_env_vars = self.get_env_vars()
        missing_vars = []
        
        for key, entry in self.env_entries.items():
            value = entry.get().strip()
            if not value:
                missing_vars.append(key)
        
        if missing_vars:
            missing_list = "\n• ".join(missing_vars)
            messagebox.showerror("エラー", 
                               f"以下の環境変数が入力されていません：\n\n• {missing_list}\n\n"
                               "これらの値はBotの動作に必要です。")
            return
            
        # UIを更新
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="ステータス: 起動中...", foreground="orange")
        
        # 別スレッドでbotを起動
        thread = threading.Thread(target=self._run_bot, args=(token,))
        thread.daemon = True
        thread.start()
        
    def _run_bot(self, token):
        try:
            # zipを解凍
            self.bot_dir = self.extract_zip(self.selected_zip)
            if not self.bot_dir:
                self.root.after(0, self._bot_failed, "zipファイルの解凍に失敗しました")
                return
                
            # main.pyを探す
            main_py_path = os.path.join(self.bot_dir, 'main.py')
            if not os.path.exists(main_py_path):
                # サブディレクトリも探す
                for root, dirs, files in os.walk(self.bot_dir):
                    if 'main.py' in files:
                        main_py_path = os.path.join(root, 'main.py')
                        self.bot_dir = root
                        break
                        
            if not os.path.exists(main_py_path):
                self.root.after(0, self._bot_failed, "main.pyが見つかりません")
                return
                
            # .envファイルを作成
            self.create_env_file(self.bot_dir, token)
            
            # exe環境で内蔵Pythonを使用
            if getattr(sys, 'frozen', False) and self.use_embedded_python:
                self.log_message("内蔵Python環境でBotを実行します...")
                self._run_bot_embedded(main_py_path)
                return
            
            # 通常の外部Python実行
            python_path = self.install_requirements(self.bot_dir)
            if not python_path:
                self.root.after(0, self._bot_failed, "Pythonがインストールされていません。\nPythonをインストールしてから再度実行してください。")
                return
                
            # botを起動
            self.log_message("Botを起動中...")
            self.log_message(f"使用するPython: {python_path}")
            self.is_running = True
            
            # 環境変数を設定
            env = os.environ.copy()
            env['PYTHONPATH'] = self.bot_dir
            
            # PyInstallerでexe化されているかを検出
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # exe環境の場合、PYTHONDONTWRITEBYTECODEを設定
                env['PYTHONDONTWRITEBYTECODE'] = '1'
                # multiprocessingの初期化を無効化
                env['MULTIPROCESSING_FORKING_DISABLE'] = '1'
            
            # botプロセスを開始
            # Windows exe環境での新しいウィンドウ表示を防ぐ
            startupinfo = None
            creationflags = 0
            
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                # exe環境の場合、CREATE_NO_WINDOWとDETACHED_PROCESSを組み合わせる
                if getattr(sys, 'frozen', False):
                    creationflags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                else:
                    creationflags = subprocess.CREATE_NO_WINDOW
            
            self.bot_process = subprocess.Popen(
                [python_path, 'main.py'],
                cwd=self.bot_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            self.root.after(0, self._bot_started)
            
            # 出力を監視
            for line in iter(self.bot_process.stdout.readline, ''):
                if not self.is_running:
                    break
                if line:
                    self.root.after(0, self.log_message, line.strip())
                    
            self.bot_process.wait()
            
        except Exception as e:
            self.root.after(0, self._bot_failed, str(e))
        finally:
            self.is_running = False
            self.root.after(0, self._bot_stopped)
            
    def _bot_started(self):
        self.status_label.config(text="ステータス: 実行中", foreground="green")
        self.log_message("Botが起動しました")
        
    def _bot_failed(self, error):
        self.status_label.config(text="ステータス: エラー", foreground="red")
        self.log_message(f"エラー: {error}")
        
        # Token関連のエラーの場合、詳細な説明を表示
        if "401 Unauthorized" in error or "Improper token" in error:
            self.log_message("Tokenが無効です。以下を確認してください：")
            self.log_message("1. Tokenが正しくコピーされているか")
            self.log_message("2. Botが正しく作成されているか")
            self.log_message("3. Tokenが有効期限切れになっていないか")
            self.log_message("4. Botに適切な権限が付与されているか")
            messagebox.showerror("Tokenエラー", 
                               "Discord Bot Tokenが無効です。\n\n"
                               "確認事項：\n"
                               "• Tokenが正しくコピーされているか\n"
                               "• Botが正しく作成されているか\n"
                               "• Tokenが有効期限切れになっていないか\n"
                               "• Botに適切な権限が付与されているか\n\n"
                               "Discord Developer Portalで新しいTokenを生成してください。")
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
    def _bot_stopped(self):
        self.status_label.config(text="ステータス: 停止", foreground="gray")
        self.log_message("Botが停止しました")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # 一時ディレクトリをクリーンアップ
        if self.bot_dir and os.path.exists(self.bot_dir):
            try:
                shutil.rmtree(self.bot_dir)
                self.log_message("一時ファイルを削除しました")
            except:
                pass
                
    def _run_bot_embedded(self, main_py_path):
        """内蔵Python環境でBotを実行"""
        import asyncio
        
        try:
            # 必要なモジュールをインストール
            self._install_embedded_requirements()
            
            # main.pyの内容を読み込む
            with open(main_py_path, 'r', encoding='utf-8') as f:
                bot_code = f.read()
            
            # 環境変数を設定
            os.chdir(self.bot_dir)
            sys.path.insert(0, self.bot_dir)
            
            # .envファイルから環境変数を読み込む
            env_path = os.path.join(self.bot_dir, '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            
            self.log_message("Botを起動中...")
            self.is_running = True
            self.root.after(0, self._bot_started)
            
            # 標準出力・エラー出力をリダイレクト
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            def log_output():
                # バッファから出力を読み取ってログに表示
                stdout_content = stdout_buffer.getvalue()
                stderr_content = stderr_buffer.getvalue()
                
                if stdout_content:
                    for line in stdout_content.splitlines():
                        if line.strip():
                            self.root.after(0, self.log_message, line)
                    stdout_buffer.truncate(0)
                    stdout_buffer.seek(0)
                
                if stderr_content:
                    for line in stderr_content.splitlines():
                        if line.strip():
                            # ログレベルを判定
                            if '[INFO' in line:
                                self.root.after(0, self.log_message, line)
                            elif '[WARNING' in line or '[WARN' in line:
                                self.root.after(0, self.log_message, f"[警告] {line}")
                            elif '[ERROR' in line or '[CRITICAL' in line:
                                self.root.after(0, self.log_message, f"[エラー] {line}")
                            else:
                                self.root.after(0, self.log_message, line)
                    stderr_buffer.truncate(0)
                    stderr_buffer.seek(0)
                
                # 実行中なら定期的にチェック
                if self.is_running:
                    self.root.after(100, log_output)
            
            # 出力監視を開始
            self.root.after(100, log_output)
            
            # Windows環境でのイベントループポリシー設定
            if os.name == 'nt':
                # スレッドで実行する前にポリシーを設定
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            # 現在のスレッド用の新しいイベントループを作成
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            
            # 停止チェック用のタスクを作成
            async def check_stop():
                while self.is_running:
                    await asyncio.sleep(0.1)
                # 停止が要求された場合、すべてのタスクをキャンセル
                tasks = [task for task in asyncio.all_tasks() if not task.done()]
                for task in tasks:
                    task.cancel()
                # ループを停止
                new_loop.stop()
            
            # Botコードを実行
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                # グローバル名前空間を準備
                bot_globals = {
                    '__name__': '__main__',
                    '__file__': main_py_path,
                    '__doc__': None,
                    '__package__': None
                }
                
                try:
                    # 停止チェックタスクをスケジュール
                    new_loop.create_task(check_stop())
                    
                    # コードを実行（bot.run()が呼ばれる想定）
                    exec(bot_code, bot_globals)
                except SystemExit:
                    # bot.run()が正常終了した場合
                    pass
                except Exception as e:
                    self.log_message(f"実行エラー: {str(e)}")
                    import traceback
                    self.log_message(traceback.format_exc())
                finally:
                    # イベントループのクリーンアップ
                    try:
                        # 残りのタスクをキャンセル
                        pending_tasks = [task for task in asyncio.all_tasks(new_loop) if not task.done()]
                        if pending_tasks:
                            for task in pending_tasks:
                                task.cancel()
                            # キャンセルされたタスクの完了を待つ
                            try:
                                new_loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
                            except:
                                pass
                        
                        if not new_loop.is_closed():
                            new_loop.close()
                    except:
                        pass
            
        except Exception as e:
            error_msg = f"内蔵実行エラー: {str(e)}"
            self.root.after(0, self._bot_failed, error_msg)
            import traceback
            self.log_message(f"詳細: {traceback.format_exc()}")
        finally:
            self.is_running = False
            self.root.after(0, self._bot_stopped)
    
    def _install_embedded_requirements(self):
        """内蔵環境用の依存関係チェック"""
        req_path = os.path.join(self.bot_dir, 'requirements.txt')
        if os.path.exists(req_path):
            self.log_message("依存関係を確認中...")
            
            # 内蔵されている主要パッケージのリスト
            embedded_packages = {
                'discord': 'discord.py',
                'discord.py': 'discord.py',
                'py-cord': 'discord.py (Py-Cord)',
                'aiohttp': 'aiohttp',
                'python-dotenv': 'python-dotenv',
                'dotenv': 'python-dotenv',
                'requests': 'requests',
                'asyncio': 'asyncio',
                'websockets': 'websockets',
            }
            
            try:
                # requirements.txtを読み込み
                with open(req_path, 'r', encoding='utf-8') as f:
                    requirements = f.read().splitlines()
                
                # パッケージの利用可能性をチェック
                for req in requirements:
                    req = req.strip()
                    if req and not req.startswith('#'):
                        # バージョン指定を除去
                        package_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
                        
                        # 内蔵パッケージかチェック
                        if package_name.lower() in embedded_packages:
                            try:
                                # パッケージのインポートを試行
                                if package_name.lower() in ['discord', 'discord.py', 'py-cord']:
                                    import discord
                                elif package_name.lower() in ['python-dotenv', 'dotenv']:
                                    import dotenv
                                else:
                                    __import__(package_name.lower().replace('-', '_'))
                                self.log_message(f"✓ {embedded_packages[package_name.lower()]} - 利用可能")
                            except ImportError:
                                self.log_message(f"✗ {package_name} - 内蔵されていません（基本機能で代替）")
                        else:
                            self.log_message(f"- {package_name} - 外部パッケージ（スキップ）")
                            
            except Exception as e:
                self.log_message(f"依存関係の確認中にエラー: {str(e)}")
            
            self.log_message("内蔵パッケージでBotを実行します...")
    
    def stop_bot(self):
        if self.is_running:
            self.log_message("Botを停止中...")
            self.is_running = False
            
            # 外部プロセスの場合
            if self.bot_process:
                # プロセスを終了
                if os.name == 'nt':  # Windows
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.bot_process.pid)], 
                                 capture_output=True)
                else:  # Linux/Mac
                    self.bot_process.terminate()
            
            # 内蔵実行の場合、より安全な停止処理
            if getattr(sys, 'frozen', False) and self.use_embedded_python:
                try:
                    import asyncio
                    # 現在実行中のループを安全に取得
                    try:
                        loop = asyncio.get_running_loop()
                        # 実行中のタスクをキャンセル
                        tasks = asyncio.all_tasks(loop)
                        for task in tasks:
                            if not task.done():
                                task.cancel()
                        self.log_message(f"{len(tasks)}個のタスクをキャンセルしました")
                    except RuntimeError:
                        # 実行中のループがない場合（正常な状態）
                        self.log_message("アクティブなイベントループはありません")
                except Exception as e:
                    # エラーが発生しても停止処理は続行
                    self.log_message(f"停止処理中の警告: {str(e)}")
                    
            self.status_label.config(text="ステータス: 停止中...", foreground="orange")

    def select_file(self):
        """ファイル選択ダイアログを表示"""
        file_path = filedialog.askopenfilename(
            title="Botファイル（.zip）を選択",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_zip = file_path
            self.file_label.config(text=f"ファイル: {os.path.basename(file_path)}")
            self.log_message(f"ファイルを選択しました: {os.path.basename(file_path)}")
            self.drop_label.config(text="✓ ファイルが選択されました", background="lightgreen")
            
            # 一時的に解凍して.env.exampleを確認
            self.check_env_example(file_path)
                

def main():
    try:
        # デバッグ情報を出力
        print("Bot Launcher を起動中...")
        print(f"Python バージョン: {sys.version}")
        print(f"実行パス: {sys.executable}")
        print(f"作業ディレクトリ: {os.getcwd()}")
        
        # tkinterdnd2の初期化を試行
        root = None
        if DND_AVAILABLE and dnd is not None:
            try:
                root = dnd.Tk()
                print("tkinterdnd2 の初期化に成功しました")
            except (RuntimeError, OSError) as e:
                print(f"tkinterdnd2 の初期化に失敗: {e}")
                root = None
        
        # フォールバック: 通常のtkinterを使用
        if root is None:
            import tkinter as tk
            root = tk.Tk()
            print("通常のtkinterを使用します")
        
        app = BotLauncher(root)
        root.mainloop()
        
    except Exception as e:
        # エラーをファイルに出力（PyInstaller環境ではコンソールが見えない場合がある）
        try:
            with open("error_log.txt", "w", encoding="utf-8") as f:
                f.write(f"起動エラー: {str(e)}\n")
                f.write(f"Python バージョン: {sys.version}\n")
                f.write(f"実行パス: {sys.executable}\n")
                import traceback
                f.write(f"詳細:\n{traceback.format_exc()}\n")
        except:
            pass
        
        # 可能であればエラーダイアログを表示
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # メインウィンドウを非表示
            messagebox.showerror("起動エラー", 
                               f"アプリケーションの起動に失敗しました。\n\n"
                               f"エラー: {str(e)}\n\n"
                               f"error_log.txtファイルを確認してください。")
        except:
            pass
        
        print(f"起動エラー: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Windows exe環境でのmultiprocessing問題を回避
    freeze_support()
    main() 