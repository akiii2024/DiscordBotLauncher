#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アイコンファイルを作成するスクリプト
"""

from PIL import Image, ImageDraw
import os

def create_simple_icon():
    """シンプルなアイコンを作成"""
    # 32x32のアイコンを作成
    size = 32
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 円形の背景（青色）
    draw.ellipse([2, 2, size-2, size-2], fill=(59, 89, 152, 255))
    
    # 中央に「B」の文字を描画（白色）
    draw.text((size//2-4, size//2-6), "B", fill=(255, 255, 255, 255))
    
    # 複数のサイズでアイコンを作成
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for s in sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        images.append(resized)
    
    # ICOファイルとして保存
    images[0].save('icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
    print(f"アイコンファイル 'icon.ico' を作成しました")
    print(f"サイズ: {os.path.getsize('icon.ico')} bytes")

if __name__ == "__main__":
    try:
        create_simple_icon()
    except ImportError:
        print("PILライブラリが必要です。以下のコマンドでインストールしてください:")
        print("pip install Pillow")
    except Exception as e:
        print(f"エラーが発生しました: {e}") 