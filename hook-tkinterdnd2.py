# PyInstaller hook for tkinterdnd2
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs
import os

# tkinterdnd2のデータファイルを収集
datas = collect_data_files('tkinterdnd2')

# tkinterdnd2のサブモジュールを収集
hiddenimports = collect_submodules('tkinterdnd2')

# 動的ライブラリを収集
binaries = collect_dynamic_libs('tkinterdnd2')

# 追加の隠れたインポート
hiddenimports += [
    'tkinterdnd2.tkdnd',
    'tkinterdnd2.TkinterDnD',
]

# tkinterdnd2の特定ファイルを強制的に含める
try:
    import tkinterdnd2
    tkinterdnd2_path = os.path.dirname(tkinterdnd2.__file__)
    
    # 必要なファイルを手動で追加
    for root, dirs, files in os.walk(tkinterdnd2_path):
        for file in files:
            if file.endswith(('.dll', '.so', '.dylib', '.tcl', '.tk')):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, tkinterdnd2_path)
                dest_path = os.path.join('tkinterdnd2', rel_path)
                datas.append((src_path, os.path.dirname(dest_path)))
                
except ImportError:
    pass 