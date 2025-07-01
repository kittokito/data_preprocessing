#!/usr/bin/env python3
"""
JSONLファイルをtitleに基づいてマージするスクリプト

同一のファイル名（block_より前の部分）を持つエントリを、
block_の後の数字順にソートしてマージします。
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
import sys
import os

# スクリプトのディレクトリを取得してパスに追加
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

try:
    from config import MERGE_JSONL_BY_TITLE_CONFIG
except ImportError:
    print("エラー: config.pyから設定を読み込めませんでした。")
    sys.exit(1)


def extract_base_name_and_block_num(title: str) -> Tuple[str, int]:
    """
    titleからベース名とblock番号を抽出
    
    Args:
        title: "00-9930_積層機_ｻｰﾎﾞ_block_1" のような形式
        
    Returns:
        (base_name, block_num): ("00-9930_積層機_ｻｰﾎﾞ", 1)
    """
    # block_で分割して、最後の部分から数字を抽出
    parts = title.split('_block_')
    if len(parts) != 2:
        # block_が含まれていない場合は、そのまま返す
        return title, 0
    
    base_name = parts[0]
    block_part = parts[1]
    
    # 数字部分を抽出（数字以外の文字が含まれている場合も考慮）
    match = re.search(r'(\d+)', block_part)
    if match:
        block_num = int(match.group(1))
    else:
        block_num = 0
    
    return base_name, block_num


def merge_jsonl_by_title(input_file: Path, output_file: Path, text_delimiter: str = ";") -> None:
    """
    JSONLファイルをtitleに基づいてマージ
    
    Args:
        input_file: 入力JSONLファイルのパス
        output_file: 出力JSONLファイルのパス
        text_delimiter: テキスト結合時の区切り文字
    """
    # データを読み込み、ベース名でグループ化
    grouped_data = defaultdict(list)
    
    # 入力ファイル名（拡張子なし）を取得
    input_filename = input_file.stem
    
    print(f"入力ファイルを読み込み中: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                data = json.loads(line)
                title = data.get('title', '')
                text = data.get('text', '')
                
                base_name, block_num = extract_base_name_and_block_num(title)
                grouped_data[base_name].append({
                    'text': text,
                    'block_num': block_num,
                    'original_title': title
                })
                
            except json.JSONDecodeError as e:
                print(f"警告: 行 {line_num} でJSONデコードエラー: {e}")
                continue
    
    print(f"グループ化完了: {len(grouped_data)} 個のベース名")
    
    # 各グループをblock番号順にソートしてマージ
    merged_results = []
    
    for base_name, entries in grouped_data.items():
        # block番号順にソート
        entries.sort(key=lambda x: x['block_num'])
        
        # テキストを指定された区切り文字で結合
        # 先頭のテキストにもdelimiterを付ける（ただし\nは除く）
        delimiter_without_newline = text_delimiter.replace('\n', '')
        texts = [entry['text'] for entry in entries]
        if texts:
            # 最初のテキストの前にもdelimiterを付ける
            merged_text = delimiter_without_newline + text_delimiter.join(texts)
        else:
            merged_text = ""
        
        merged_results.append({
            'base_name': base_name,
            'merged_text': merged_text,
            'block_count': len(entries),
            'block_nums': [entry['block_num'] for entry in entries]
        })
    
    # ベース名順にソート
    merged_results.sort(key=lambda x: x['base_name'])
    
    # 出力ファイルに書き込み
    print(f"出力ファイルに書き込み中: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, result in enumerate(merged_results):
            new_entry = {
                'id': f"{input_filename}-{idx}",  # 入力ファイル名+連番
                'title': result['base_name'],
                'text': result['merged_text']
            }
            
            f.write(json.dumps(new_entry, ensure_ascii=False) + '\n')
    
    print(f"マージ完了:")
    print(f"  - 入力エントリ数: {sum(len(entries) for entries in grouped_data.values())}")
    print(f"  - 出力エントリ数: {len(merged_results)}")
    print(f"  - マージされたグループ（最大10個表示）:")
    
    # 最大10個のサンプルを表示
    sample_results = merged_results[:10]
    for result in sample_results:
        print(f"    {result['base_name']}: {result['block_count']} blocks (block_{result['block_nums']})")
    
    if len(merged_results) > 10:
        print(f"    ... 他 {len(merged_results) - 10} 個のグループ")


def main():
    """
    config.pyの設定を使用してJSONLファイルをマージ
    """
    # config.pyから設定を読み込み
    input_file = Path(MERGE_JSONL_BY_TITLE_CONFIG['input_file'])
    output_file = Path(MERGE_JSONL_BY_TITLE_CONFIG['output_file'])
    text_delimiter = MERGE_JSONL_BY_TITLE_CONFIG['text_delimiter']
    
    print(f"config.pyの設定を使用:")
    print(f"  入力ファイル: {input_file}")
    print(f"  出力ファイル: {output_file}")
    print(f"  区切り文字: '{text_delimiter}'")
    print()
    
    # 入力ファイルの存在確認
    if not input_file.exists():
        print(f"エラー: 入力ファイルが見つかりません: {input_file}")
        return 1
    
    # 出力ディレクトリの作成
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        merge_jsonl_by_title(input_file, output_file, text_delimiter)
        print(f"\n✅ マージが正常に完了しました: {output_file}")
        return 0
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
