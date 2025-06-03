#!/usr/bin/env python3
"""
2つのJSONLファイルを結合するスクリプト

使用方法:
    python scripts/merge_jsonl.py

設定:
    config.pyのMERGE_JSONL_CONFIGで設定を変更可能
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.config import MERGE_JSONL_CONFIG


def load_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    """JSONLファイルを読み込んでリストとして返す"""
    entries = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                entry = json.loads(line)
                # 必須フィールドの確認
                if not all(key in entry for key in ['id', 'title', 'text']):
                    print(f"警告: {file_path} の {line_num} 行目に必須フィールドが不足しています")
                    continue
                entries.append(entry)
            except json.JSONDecodeError as e:
                print(f"エラー: {file_path} の {line_num} 行目のJSON解析に失敗しました: {e}")
                continue
    
    return entries


def merge_jsonl_files(file1_path: Path, file2_path: Path, output_path: Path) -> None:
    """2つのJSONLファイルを結合してIDでソートし、出力する"""
    
    print(f"ファイル1を読み込み中: {file1_path}")
    entries1 = load_jsonl(file1_path)
    print(f"  - {len(entries1)} エントリを読み込みました")
    
    print(f"ファイル2を読み込み中: {file2_path}")
    entries2 = load_jsonl(file2_path)
    print(f"  - {len(entries2)} エントリを読み込みました")
    
    # エントリを結合
    all_entries = entries1 + entries2
    print(f"\n合計 {len(all_entries)} エントリ")
    
    # IDの重複チェック
    id_counts = {}
    for entry in all_entries:
        entry_id = entry['id']
        id_counts[entry_id] = id_counts.get(entry_id, 0) + 1
    
    duplicates = {id_: count for id_, count in id_counts.items() if count > 1}
    if duplicates:
        print(f"\n警告: 重複するIDが見つかりました:")
        for id_, count in duplicates.items():
            print(f"  - ID '{id_}': {count} 回")
    
    # IDでソート
    try:
        # 数値としてソートを試みる
        all_entries.sort(key=lambda x: int(x['id']))
        print("\nIDを数値としてソートしました")
    except ValueError:
        # 文字列としてソート
        all_entries.sort(key=lambda x: x['id'])
        print("\nIDを文字列としてソートしました")
    
    # 出力ディレクトリの作成
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # ファイルに書き込み
    print(f"\n結果を書き込み中: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in all_entries:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
    
    print(f"完了: {len(all_entries)} エントリを書き込みました")
    
    # 統計情報の表示
    print("\n=== 統計情報 ===")
    print(f"ファイル1のエントリ数: {len(entries1)}")
    print(f"ファイル2のエントリ数: {len(entries2)}")
    print(f"結合後のエントリ数: {len(all_entries)}")
    if duplicates:
        print(f"重複ID数: {len(duplicates)}")


def main():
    """メイン処理"""
    # 設定の読み込み
    config = MERGE_JSONL_CONFIG
    
    file1_path = Path(config['file1_path'])
    file2_path = Path(config['file2_path'])
    output_path = Path(config['output_path'])
    
    # ファイルの存在確認
    if not file1_path.exists():
        print(f"エラー: ファイル1が見つかりません: {file1_path}")
        sys.exit(1)
    
    if not file2_path.exists():
        print(f"エラー: ファイル2が見つかりません: {file2_path}")
        sys.exit(1)
    
    print("=== JSONLファイル結合スクリプト ===")
    print(f"ファイル1: {file1_path}")
    print(f"ファイル2: {file2_path}")
    print(f"出力先: {output_path}")
    print()
    
    # 結合処理の実行
    merge_jsonl_files(file1_path, file2_path, output_path)


if __name__ == "__main__":
    main()
