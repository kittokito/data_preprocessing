import os
import json
import math
from tqdm import tqdm
from transformers import AutoTokenizer
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from collections import defaultdict
import random
from config import SPLIT_LONG_JSONL_CONFIG

# 環境変数で警告を回避（必要に応じて）
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 設定ファイルからモデル名を取得してトークナイザーをロード
tokenizer = AutoTokenizer.from_pretrained(SPLIT_LONG_JSONL_CONFIG["model_name"])

# 目標とするトークン長の範囲と比率
TARGET_RANGES = [
    (128, 512, 0.15),      # 15%: テスト, 小関数, 短ドキュメント
    (512, 2000, 0.25),     # 25%: 一般的な関数集合／スクリプト
    (2000, 8000, 0.40),    # 40%: 中規模ファイル・ノートブック
    (8000, 15872, 0.20)    # 20%: 大規模ライブラリ／マルチクラスファイル
]

def get_target_range(token_count):
    """トークン数がどの範囲に属するかを返す"""
    for i, (min_tok, max_tok, _) in enumerate(TARGET_RANGES):
        if min_tok <= token_count <= max_tok:
            return i
    return -1  # 範囲外

def combine_segments_with_ratio(segments, segment_token_counts, delimiter_token_count, token_limit):
    """
    セグメントを指定された比率に近づけるように結合する
    
    戻り値:
      - combined_chunks: 結合されたテキストのリスト
      - chunk_token_counts: 各チャンクのトークン数リスト
      - range_distribution: 各範囲のチャンク数
    """
    n = len(segments)
    if n == 0:
        return [], [], {}
    
    # 各範囲のチャンクを格納
    range_chunks = defaultdict(list)
    
    # 貪欲法で可能な限り目標範囲に収まるように結合
    i = 0
    while i < n:
        # 現在のセグメントから開始
        current_segments = [segments[i]]
        current_token_count = segment_token_counts[i]
        j = i + 1
        
        # 次のセグメントを追加できるか確認
        while j < n:
            next_count = current_token_count + delimiter_token_count + segment_token_counts[j]
            
            # token_limitを超えない範囲で追加
            if next_count <= token_limit:
                # どの範囲に入るか確認
                range_idx = get_target_range(next_count)
                
                # 範囲内に収まる場合は追加を検討
                if range_idx >= 0:
                    # 現在のトークン数の範囲も確認
                    current_range_idx = get_target_range(current_token_count)
                    
                    # より大きな範囲に移動できる場合、または同じ範囲内で最大化する場合は追加
                    if range_idx > current_range_idx or (range_idx == current_range_idx and next_count <= TARGET_RANGES[range_idx][1]):
                        current_segments.append(segments[j])
                        current_token_count = next_count
                        j += 1
                    else:
                        # これ以上追加すると範囲を超える場合は終了
                        break
                else:
                    # 範囲外になる場合は終了
                    break
            else:
                # token_limitを超える場合は終了
                break
        
        # 結合されたチャンクを作成
        if current_segments:
            combined_text = delimiter.join(current_segments)
            range_idx = get_target_range(current_token_count)
            
            if range_idx >= 0:
                range_chunks[range_idx].append({
                    'text': combined_text,
                    'token_count': current_token_count
                })
            else:
                # 範囲外のものも保持（128トークン未満）
                range_chunks[-1].append({
                    'text': combined_text,
                    'token_count': current_token_count
                })
        
        i = j
    
    # 各範囲のチャンク数を計算
    total_chunks = sum(len(chunks) for chunks in range_chunks.values())
    
    # 目標比率に近づけるための調整
    combined_chunks = []
    chunk_token_counts = []
    range_distribution = {}
    
    # まず各範囲から必要な数だけ取得
    for i, (min_tok, max_tok, target_ratio) in enumerate(TARGET_RANGES):
        if i in range_chunks:
            chunks = range_chunks[i]
            # この範囲の目標チャンク数
            target_count = max(1, int(total_chunks * target_ratio))
            
            # 利用可能なチャンク数に制限
            actual_count = min(len(chunks), target_count)
            
            # ランダムに選択（または全て使用）
            if actual_count < len(chunks):
                selected_chunks = random.sample(chunks, actual_count)
            else:
                selected_chunks = chunks
            
            for chunk in selected_chunks:
                combined_chunks.append(chunk['text'])
                chunk_token_counts.append(chunk['token_count'])
            
            range_distribution[f"{min_tok}-{max_tok}"] = actual_count
    
    # 範囲外のチャンク（128トークン未満）も追加
    if -1 in range_chunks:
        for chunk in range_chunks[-1]:
            combined_chunks.append(chunk['text'])
            chunk_token_counts.append(chunk['token_count'])
        range_distribution["<128"] = len(range_chunks[-1])
    
    return combined_chunks, chunk_token_counts, range_distribution

def process_jsonl_entry(entry, output_dir, token_limit=32700, exceeding_entries=None, delimiter=";<h1/>"):
    """
    JSONLの1エントリを処理する
    entry: {"id": "", "title": "", "text": ""} 形式の辞書
    """
    entry_id = entry.get("id", "")
    title = entry.get("title", "")
    content = entry.get("text", "")
    
    original_token_count = len(tokenizer(content)['input_ids'])
    
    # トークン数が制限以下の場合は分割しない
    if original_token_count <= token_limit:
        return [entry], None, {}
    
    # 指定された delimiter を使ってセグメント分割
    segments = content.split(delimiter)
    segments = [seg.strip() for seg in segments if seg.strip()]
    n_segments = len(segments)
    if n_segments == 0:
        return [entry], None, {}
    
    tokenized = tokenizer(segments, add_special_tokens=False)
    segment_token_counts = [len(ids) for ids in tokenized['input_ids']]
    
    # 各セグメントのトークン数が token_limit を超える場合
    if any(count > token_limit for count in segment_token_counts):
        if exceeding_entries is not None:
            exceeding_entries.append(entry)
        return [], {
            "id": entry_id,
            "title": title,
            "original_token_count": original_token_count,
            "skipped_due_to_segment_exceeding_limit": True,
            "max_segment_token_count": max(segment_token_counts)
        }, {}
    
    # delimiter のトークン数を計算
    delimiter_token_count = len(tokenizer(delimiter)['input_ids'])
    
    # 比率を考慮してセグメントを結合
    combined_chunks, chunk_token_counts, range_distribution = combine_segments_with_ratio(
        segments, segment_token_counts, delimiter_token_count, token_limit
    )
    
    if not combined_chunks:
        return [], {
            "id": entry_id,
            "title": title,
            "original_token_count": original_token_count,
            "error": "チャンクの作成に失敗しました。"
        }, {}
    
    # 分割されたエントリを作成
    split_entries = []
    for i, chunk in enumerate(combined_chunks):
        split_entry = {
            "id": f"{entry_id}_part{i+1}",
            "title": f"{title}_part{i+1}",
            "text": chunk
        }
        split_entries.append(split_entry)
    
    summary = {
        "id": entry_id,
        "title": title,
        "original_token_count": original_token_count,
        "split_parts": len(combined_chunks),
        "split_token_counts": chunk_token_counts,
        "max_chunk_token_count": max(chunk_token_counts) if chunk_token_counts else 0,
        "min_chunk_token_count": min(chunk_token_counts) if chunk_token_counts else 0,
        "range_distribution": range_distribution
    }
    
    return split_entries, summary, range_distribution

def process_single_entry(entry, token_limit, delimiter):
    """並列処理用の関数"""
    exceeding_entries = []
    split_entries, summary, range_dist = process_jsonl_entry(
        entry, None, token_limit, exceeding_entries, delimiter
    )
    return split_entries, summary, exceeding_entries, range_dist

def process_jsonl_file(input_file, output_file, summary_dir, token_limit=32700, exceeding_file=None, delimiter=";<h1/>"):
    """JSONLファイル全体を処理"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    os.makedirs(summary_dir, exist_ok=True)
    
    # 入力ファイルを読み込む
    entries = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    
    summary_list = []
    all_split_entries = []
    all_exceeding_entries = []
    skipped_entries = []
    
    # 全体の範囲分布を追跡
    global_range_distribution = defaultdict(int)
    
    # partial を使って必要な引数を固定
    process_func = partial(
        process_single_entry,
        token_limit=token_limit,
        delimiter=delimiter
    )
    
    # 並列処理
    with ProcessPoolExecutor() as executor:
        results = list(tqdm(
            executor.map(process_func, entries), 
            total=len(entries), 
            desc="Processing JSONL entries", 
            unit="entry"
        ))
    
    # 結果を集計
    for split_entries, summary, exceeding_entries, range_dist in results:
        all_split_entries.extend(split_entries)
        all_exceeding_entries.extend(exceeding_entries)
        
        # 範囲分布を集計
        for range_key, count in range_dist.items():
            global_range_distribution[range_key] += count
        
        if summary:
            summary_list.append(summary)
            if summary.get("skipped_due_to_segment_exceeding_limit", False):
                skipped_entries.append({
                    "id": summary["id"],
                    "title": summary["title"],
                    "original_token_count": summary["original_token_count"]
                })
    
    # 分割されたエントリを出力ファイルに書き込む
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in all_split_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    # 制限を超えたエントリを別ファイルに保存
    if exceeding_file and all_exceeding_entries:
        os.makedirs(os.path.dirname(exceeding_file), exist_ok=True)
        with open(exceeding_file, 'w', encoding='utf-8') as f:
            for entry in all_exceeding_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    # 全体の比率を計算
    total_chunks = sum(global_range_distribution.values())
    range_ratios = {}
    for range_key, count in global_range_distribution.items():
        range_ratios[range_key] = {
            "count": count,
            "ratio": count / total_chunks if total_chunks > 0 else 0
        }
    
    # サマリーを作成
    summary = {
        "input_file": os.path.basename(input_file),
        "output_file": os.path.basename(output_file),
        "num_original_entries": len(entries),
        "num_split_entries": len(all_split_entries),
        "num_skipped_entries": len(skipped_entries),
        "global_range_distribution": range_ratios,
        "target_ratios": {
            "128-512": 0.15,
            "512-2000": 0.25,
            "2000-8000": 0.40,
            "8000-15872": 0.20
        },
        "skipped_entries_due_to_segment_exceeding_limit": skipped_entries,
        "split_entries": summary_list
    }
    
    # サマリーファイルを保存
    input_base_name = os.path.splitext(os.path.basename(input_file))[0]
    summary_file = os.path.join(summary_dir, f"{input_base_name}_ratio_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)
    
    print(f"処理完了:")
    print(f"  元のエントリ数: {len(entries)}")
    print(f"  分割後のエントリ数: {len(all_split_entries)}")
    print(f"  スキップされたエントリ数: {len(skipped_entries)}")
    print(f"\n範囲別分布:")
    for range_key, data in sorted(range_ratios.items()):
        print(f"  {range_key}: {data['count']}個 ({data['ratio']:.1%})")

if __name__ == "__main__":
    # 設定ファイルから値を読み込む
    input_file = SPLIT_LONG_JSONL_CONFIG["input_file"]
    output_file = SPLIT_LONG_JSONL_CONFIG["output_file"]
    exceeding_file = SPLIT_LONG_JSONL_CONFIG["exceeding_file"]
    summary_dir = SPLIT_LONG_JSONL_CONFIG["summary_dir"]
    delimiter = SPLIT_LONG_JSONL_CONFIG["delimiter"]
    token_limit = SPLIT_LONG_JSONL_CONFIG["token_limit"]
    
    process_jsonl_file(
        input_file=input_file,
        output_file=output_file,
        summary_dir=summary_dir,
        token_limit=token_limit,
        exceeding_file=exceeding_file,
        delimiter=delimiter
    )
