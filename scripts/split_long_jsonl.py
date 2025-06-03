import os
import json
import math
from tqdm import tqdm
from transformers import AutoTokenizer
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from config import SPLIT_LONG_JSONL_CONFIG

# 環境変数で警告を回避（必要に応じて）
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 設定ファイルからモデル名を取得してトークナイザーをロード
tokenizer = AutoTokenizer.from_pretrained(SPLIT_LONG_JSONL_CONFIG["model_name"])

def split_segments_by_max_sum(segment_token_counts, delimiter_cost, token_limit):
    """
    与えられた各セグメントのトークン数リストから、
    チャンク毎のトークン数（セグメント合計＋各区切りのコスト）を、
    token_limit を超えないように分割する。

    Split Array Largest Sum の考え方を用い、まず
      token_limit を上限とした場合のチャンク数 target_chunks を求め、
    その数を崩さずに、チャンク内のトークン数（最大値）を最小化する分割を二分探索で求める。

    戻り値:
      - partitions: 各チャンクの (開始, 終了) インデックスのタプルリスト
      - chunk_token_counts: 各チャンクのトークン数リスト
    """
    n = len(segment_token_counts)
    
    def chunks_needed(max_allowed):
        chunks = 1
        current = segment_token_counts[0]
        for count in segment_token_counts[1:]:
            if current + delimiter_cost + count <= max_allowed:
                current += delimiter_cost + count
            else:
                chunks += 1
                current = count
        return chunks

    target_chunks = chunks_needed(token_limit)
    
    low = max(segment_token_counts)
    high = token_limit
    optimal = high
    while low <= high:
        mid = (low + high) // 2
        if chunks_needed(mid) <= target_chunks:
            optimal = mid
            high = mid - 1
        else:
            low = mid + 1

    partitions = []
    current_sum = segment_token_counts[0]
    start_index = 0
    for i in range(1, n):
        if current_sum + delimiter_cost + segment_token_counts[i] <= optimal:
            current_sum += delimiter_cost + segment_token_counts[i]
        else:
            partitions.append((start_index, i - 1))
            start_index = i
            current_sum = segment_token_counts[i]
    partitions.append((start_index, n - 1))
    
    chunk_token_counts = []
    for start, end in partitions:
        count = sum(segment_token_counts[start:end+1]) + delimiter_cost * (end - start)
        chunk_token_counts.append(count)
    
    return partitions, chunk_token_counts

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
        return [entry], None
    
    # 指定された delimiter を使ってセグメント分割
    segments = content.split(delimiter)
    segments = [seg.strip() for seg in segments if seg.strip()]
    n_segments = len(segments)
    if n_segments == 0:
        return [entry], None
    
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
        }
    
    # delimiter のトークン数を計算
    delimiter_token_count = len(tokenizer(delimiter)['input_ids'])
    
    partitions, chunk_token_counts = split_segments_by_max_sum(segment_token_counts, delimiter_token_count, token_limit)
    
    if max(chunk_token_counts) > token_limit:
        return [], {
            "id": entry_id,
            "title": title,
            "original_token_count": original_token_count,
            "split_parts": len(partitions),
            "split_token_counts": chunk_token_counts,
            "max_chunk_token_count": max(chunk_token_counts),
            "error": "チャンクのトークン数が上限を超えました。"
        }
    
    # 分割されたエントリを作成
    split_entries = []
    for i, (start, end) in enumerate(partitions):
        # 分割したチャンクは delimiter を用いて連結
        chunk = delimiter.join(segments[start:end+1])
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
        "split_parts": len(partitions),
        "split_token_counts": chunk_token_counts,
        "max_chunk_token_count": max(chunk_token_counts),
        "final_chunk_count_used": len(partitions)
    }
    
    return split_entries, summary

def process_single_entry(entry, token_limit, delimiter):
    """並列処理用の関数"""
    exceeding_entries = []
    split_entries, summary = process_jsonl_entry(
        entry, None, token_limit, exceeding_entries, delimiter
    )
    return split_entries, summary, exceeding_entries

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
    for split_entries, summary, exceeding_entries in results:
        all_split_entries.extend(split_entries)
        all_exceeding_entries.extend(exceeding_entries)
        
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
    
    # サマリーを作成
    summary = {
        "input_file": os.path.basename(input_file),
        "output_file": os.path.basename(output_file),
        "num_original_entries": len(entries),
        "num_split_entries": len(all_split_entries),
        "num_skipped_entries": len(skipped_entries),
        "skipped_entries_due_to_segment_exceeding_limit": skipped_entries,
        "split_entries": summary_list
    }
    
    # サマリーファイルを保存
    input_base_name = os.path.splitext(os.path.basename(input_file))[0]
    summary_file = os.path.join(summary_dir, f"{input_base_name}_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)
    
    print(f"処理完了:")
    print(f"  元のエントリ数: {len(entries)}")
    print(f"  分割後のエントリ数: {len(all_split_entries)}")
    print(f"  スキップされたエントリ数: {len(skipped_entries)}")

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
