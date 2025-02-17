import os
import json
import math
from tqdm import tqdm
from transformers import AutoTokenizer
from concurrent.futures import ProcessPoolExecutor
from functools import partial

# 環境変数で警告を回避（必要に応じて）
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Qwen/Qwen2.5-Coder-32B-Instruct のトークナイザーをロード
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-32B-Instruct")

# 区切り文字とそのトークン数（固定値として扱う）
DELIMITER = '\n;'
DELIMITER_TOKEN_COUNT = len(tokenizer(DELIMITER)['input_ids'])

# 除外ファイルの保存先ディレクトリ
EXCEEDING_DIR = "/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/txt_semicolon_exceeding_limit"

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

def process_file(input_file, output_dir, token_limit=32700):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_token_count = len(tokenizer(content)['input_ids'])
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    if original_token_count <= token_limit:
        output_file = os.path.join(output_dir, f"{base_name}.txt")
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(content)
        return None

    segments = content.split(DELIMITER)
    segments = [seg.strip() for seg in segments if seg.strip()]
    n_segments = len(segments)
    if n_segments == 0:
        return None

    tokenized = tokenizer(segments, add_special_tokens=False)
    segment_token_counts = [len(ids) for ids in tokenized['input_ids']]

    if any(count > token_limit for count in segment_token_counts):
        os.makedirs(EXCEEDING_DIR, exist_ok=True)
        output_file = os.path.join(EXCEEDING_DIR, os.path.basename(input_file))
        with open(output_file, 'w', encoding='utf-8') as out_f:
            out_f.write(content)
        return {
            "file_name": os.path.basename(input_file),
            "original_token_count": original_token_count,
            "skipped_due_to_segment_exceeding_limit": True,
            "max_segment_token_count": max(segment_token_counts)
        }
    
    total_tokens = sum(segment_token_counts) + DELIMITER_TOKEN_COUNT * (n_segments - 1)
    
    partitions, chunk_token_counts = split_segments_by_max_sum(segment_token_counts, DELIMITER_TOKEN_COUNT, token_limit)
    
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
        chunk = DELIMITER.join(segments[start:end+1])
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

# グローバルに定義することでピクル化可能にする
def process_single_file(filename, input_dir, output_dir, token_limit):
    input_file = os.path.join(input_dir, filename)
    return process_file(input_file, output_dir, token_limit)

def process_directory(input_dir, output_dir, summary_dir, token_limit=32700):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(summary_dir, exist_ok=True)
    
    summary_list = []
    files_with_exceeding_chunks = []
    skipped_files = []
    
    files = [filename for filename in os.listdir(input_dir) if filename.endswith('.txt')]
    
    # partial を使ってグローバル関数に追加の引数を渡す
    process_func = partial(process_single_file, input_dir=input_dir, output_dir=output_dir, token_limit=token_limit)
    
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
        "files_with_exceeding_chunks": files_with_exceeding_chunks,
        "skipped_files_due_to_segment_exceeding_limit": skipped_files,
        "num_split_files": len(summary_list),
        "split_files": summary_list
    }
    
    # ここでサマリファイル名を、入力ディレクトリ名ではなく出力ディレクトリ名に変更
    output_dir_name = os.path.basename(os.path.normpath(output_dir))
    summary_file = os.path.join(summary_dir, f"{output_dir_name}.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    input_dir = "/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/txt_h1_exceeding_limit"
    output_dir = "/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/txt_splitted_semicolon"
    summary_dir = "/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/data_analysis"
    process_directory(input_dir, output_dir, summary_dir)
