import os
import json
import math
from tqdm import tqdm
from transformers import AutoTokenizer
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from config import SPLIT_LONG_TXT_CONFIG

# 環境変数で警告を回避（必要に応じて）
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 設定ファイルからモデル名を取得してトークナイザーをロード
tokenizer = AutoTokenizer.from_pretrained(SPLIT_LONG_TXT_CONFIG["model_name"])

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

def process_file(input_file, output_dir, token_limit=32700, exceeding_dir=None, delimiter=";<h1/>"):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_token_count = len(tokenizer(content)['input_ids'])
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    if original_token_count <= token_limit:
        output_file = os.path.join(output_dir, f"{base_name}.txt")
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(content)
        return None

    # 指定された delimiter を使ってセグメント分割
    segments = content.split(delimiter)
    segments = [seg.strip() for seg in segments if seg.strip()]
    n_segments = len(segments)
    if n_segments == 0:
        return None

    tokenized = tokenizer(segments, add_special_tokens=False)
    segment_token_counts = [len(ids) for ids in tokenized['input_ids']]

    # 各セグメントのトークン数が token_limit を超える場合、exceeding_dir に保存
    if any(count > token_limit for count in segment_token_counts):
        if exceeding_dir is None:
            raise ValueError("exceeding_dirが指定されていません。")
        os.makedirs(exceeding_dir, exist_ok=True)
        output_file = os.path.join(exceeding_dir, os.path.basename(input_file))
        with open(output_file, 'w', encoding='utf-8') as out_f:
            out_f.write(content)
        return {
            "file_name": os.path.basename(input_file),
            "original_token_count": original_token_count,
            "skipped_due_to_segment_exceeding_limit": True,
            "max_segment_token_count": max(segment_token_counts)
        }
    
    # delimiter のトークン数を計算
    delimiter_token_count = len(tokenizer(delimiter)['input_ids'])
    
    partitions, chunk_token_counts = split_segments_by_max_sum(segment_token_counts, delimiter_token_count, token_limit)
    
    if max(chunk_token_counts) > token_limit:
        return {
            "file_name": os.path.basename(input_file),
            "original_token_count": original_token_count,
            "split_parts": len(partitions),
            "split_token_counts": chunk_token_counts,
            "max_chunk_token_count": max(chunk_token_counts),
            "error": "チャンクのトークン数が上限を超えました。"
        }
    
    for i, (start, end) in enumerate(partitions):
        # 分割したチャンクは delimiter を用いて連結
        chunk = delimiter.join(segments[start:end+1])
        output_file = os.path.join(output_dir, f"{base_name}_part{i+1}.txt")
        with open(output_file, 'w', encoding='utf-8') as out_f:
            out_f.write(chunk)
    
    return {
        "file_name": os.path.basename(input_file),
        "original_token_count": original_token_count,
        "split_parts": len(partitions),
        "split_token_counts": chunk_token_counts,
        "max_chunk_token_count": max(chunk_token_counts),
        "final_chunk_count_used": len(partitions)
    }

# ピクル化可能なようにグローバル関数として定義
def process_single_file(filename, input_dir, output_dir, token_limit, exceeding_dir, delimiter):
    input_file = os.path.join(input_dir, filename)
    return process_file(input_file, output_dir, token_limit, exceeding_dir, delimiter)

def process_directory(input_dir, output_dir, summary_dir, token_limit=32700, exceeding_dir=None, delimiter=";<h1/>", label=None):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(summary_dir, exist_ok=True)
    
    summary_list = []
    files_with_exceeding_chunks = []
    skipped_files = []
    
    files = [filename for filename in os.listdir(input_dir) if filename.endswith('.txt')]
    
    # partial を使って必要な引数を固定
    process_func = partial(
        process_single_file,
        input_dir=input_dir,
        output_dir=output_dir,
        token_limit=token_limit,
        exceeding_dir=exceeding_dir,
        delimiter=delimiter
    )
    
    with ProcessPoolExecutor() as executor:
        results = list(tqdm(executor.map(process_func, files), total=len(files), desc="Processing files", unit="file"))
    
    for file_summary in results:
        if file_summary:
            summary_list.append(file_summary)
            if file_summary.get("skipped_due_to_segment_exceeding_limit", False):
                skipped_files.append({
                    "file_name": file_summary["file_name"],
                    "original_token_count": file_summary["original_token_count"]
                })
            elif file_summary.get("max_chunk_token_count", 0) > token_limit:
                files_with_exceeding_chunks.append(file_summary["file_name"])
    
    summary = {
        "num_split_files": len(summary_list),
        "num_skipped_files": len(skipped_files),
        "skipped_files_due_to_segment_exceeding_limit": skipped_files,
        "split_files": summary_list
    }

    
    out_dir_name = os.path.basename(os.path.normpath(output_dir)).removeprefix("txt_")
    summary_file = os.path.join(summary_dir, f"{label}_{out_dir_name}.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # 設定ファイルから値を読み込む
    input_dir = SPLIT_LONG_TXT_CONFIG["input_dir"]
    output_dir = SPLIT_LONG_TXT_CONFIG["output_dir"]
    exceeding_dir = SPLIT_LONG_TXT_CONFIG["exceeding_dir"]
    summary_dir = SPLIT_LONG_TXT_CONFIG["summary_dir"]
    delimiter = SPLIT_LONG_TXT_CONFIG["delimiter"]
    label = SPLIT_LONG_TXT_CONFIG["label"]
    token_limit = SPLIT_LONG_TXT_CONFIG["token_limit"]
    
    process_directory(input_dir, output_dir, summary_dir, token_limit=token_limit, exceeding_dir=exceeding_dir, delimiter=delimiter, label=label)
