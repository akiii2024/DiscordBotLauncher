# PyInstaller hook for tkinterdnd2
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# tkinterdnd2のデータファイルを収集
datas = collect_data_files('tkinterdnd2')

# tkinterdnd2のサブモジュールを収集
hiddenimports = collect_submodules('tkinterdnd2')

# 追加の隠れたインポート
hiddenimports += [
    'tkinterdnd2.tkdnd',
    'tkinterdnd2.TkinterDnD',
] 