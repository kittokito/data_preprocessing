import os
import json
import math
from tqdm import tqdm
from transformers import AutoTokenizer

# Qwen/Qwen2.5-Coder-32B-Instruct のトークナイザーをロード
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-32B-Instruct")

# 区切り文字とそのトークン数（固定値として扱う）
DELIMITER = ';<h1/>'
DELIMITER_TOKEN_COUNT = len(tokenizer(DELIMITER)['input_ids'])

def group_cost(prefix, i, j, delimiter_cost):
    """
    セグメント i から j までを結合したときのトークン数を計算（区切り文字分を加算）
    """
    return (prefix[j+1] - prefix[i]) + delimiter_cost * (j - i)

def linear_partition(nums, k, delimiter_cost):
    """
    nums: 各セグメントのトークン数リスト
    k: 作成したいチャンク数
    delimiter_cost: 区切り文字のトークン数
    
    戻り値:
      各チャンクに含めるセグメントの (開始, 終了) インデックスのタプルリスト
    """
    n = len(nums)
    if k <= 0:
        return []
    if k >= n:
        return [(i, i) for i in range(n)]
    
    # 累積和の計算
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i+1] = prefix[i] + nums[i]
    
    # dp[i][j]: セグメント 0～j を i+1 個のチャンクに分割したときの「最大チャンクトークン数」の最小値
    dp = [[float('inf')] * n for _ in range(k)]
    partition_idx = [[0] * n for _ in range(k)]
    
    for j in range(n):
        dp[0][j] = group_cost(prefix, 0, j, delimiter_cost)
    
    for i in range(1, k):
        for j in range(i, n):
            for x in range(i-1, j):
                current = max(dp[i-1][x], group_cost(prefix, x+1, j, delimiter_cost))
                if current < dp[i][j]:
                    dp[i][j] = current
                    partition_idx[i][j] = x
    
    # 最適な分割境界の再構築
    partitions = []
    def reconstruct(i, j):
        if i == 0:
            partitions.append((0, j))
        else:
            x = partition_idx[i][j]
            reconstruct(i-1, x)
            partitions.append((x+1, j))
    reconstruct(k-1, n-1)
    return partitions

def process_file(input_file, output_dir, token_limit=32700):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_token_count = len(tokenizer(content)['input_ids'])
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # ファイル全体が token_limit 以下ならそのまま出力
    if original_token_count <= token_limit:
        output_file = os.path.join(output_dir, f"{base_name}.txt")
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(content)
        return None

    # ファイルが token_limit を超える場合、<h1> で分割
    segments = content.split(DELIMITER)
    segments = [seg.strip() for seg in segments if seg.strip()]
    n_segments = len(segments)
    if n_segments == 0:
        return None
    
    # 各セグメントのトークン数を計算
    segment_token_counts = [len(tokenizer(seg)['input_ids']) for seg in segments]

    # もし任意のセグメントが token_limit を超えていたら、そのファイルは除外してサマリに記録
    if any(count > token_limit for count in segment_token_counts):
        return {
            "file_name": os.path.basename(input_file),
            "original_token_count": original_token_count,
            "skipped_due_to_segment_exceeding_limit": True,
            "max_segment_token_count": max(segment_token_counts)
        }
    
    total_tokens = sum(segment_token_counts) + DELIMITER_TOKEN_COUNT * (n_segments - 1)
    
    # token_limit 以下に収めるために必要な最低チャンク数
    k = math.ceil(total_tokens / token_limit)
    k = min(k, n_segments)
    
    partitions = linear_partition(segment_token_counts, k, DELIMITER_TOKEN_COUNT)
    
    # 動的にチャンク数を増やして、全てのチャンクが token_limit 以下になるようにする
    while True:
        chunks = []
        chunk_token_counts = []
        for start, end in partitions:
            chunk = DELIMITER.join(segments[start:end+1])
            chunk_tokens = len(tokenizer(chunk)['input_ids'])
            chunks.append(chunk)
            chunk_token_counts.append(chunk_tokens)
        
        # すべてのチャンクが token_limit 以下であれば採用
        if all(count <= token_limit for count in chunk_token_counts):
            break
        # さらにチャンク数を増やせるなら k を1増やして再試行
        if k < n_segments:
            k += 1
            partitions = linear_partition(segment_token_counts, k, DELIMITER_TOKEN_COUNT)
        else:
            # 各セグメントは token_limit 以下なのでここには来ないはず
            break
    
    # 分割結果のチャンクをファイル出力
    for i, chunk in enumerate(chunks):
        output_file = os.path.join(output_dir, f"{base_name}_part{i+1}.txt")
        with open(output_file, 'w', encoding='utf-8') as out_f:
            out_f.write(chunk)
    
    return {
        "file_name": os.path.basename(input_file),
        "original_token_count": original_token_count,
        "split_parts": len(chunks),
        "split_token_counts": chunk_token_counts,
        "max_chunk_token_count": max(chunk_token_counts),
        "final_chunk_count_used": k
    }

def process_directory(input_dir, output_dir, summary_dir, token_limit=32700):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(summary_dir, exist_ok=True)
    
    summary_list = []
    files_with_exceeding_chunks = []
    skipped_files = []
    
    # 対象となる .txt ファイル一覧を取得し、進捗を tqdm で表示
    files = [filename for filename in os.listdir(input_dir) if filename.endswith('.txt')]
    for filename in tqdm(files, desc="Processing files", unit="file"):
        input_file = os.path.join(input_dir, filename)
        file_summary = process_file(input_file, output_dir, token_limit)
        if file_summary:
            summary_list.append(file_summary)
            if file_summary.get("skipped_due_to_segment_exceeding_limit", False):
                skipped_files.append(file_summary["file_name"])
            elif file_summary.get("max_chunk_token_count", 0) > token_limit:
                files_with_exceeding_chunks.append(file_summary["file_name"])
    
    input_dir_name = os.path.basename(os.path.normpath(input_dir))
    summary = {
        "files_with_exceeding_chunks": files_with_exceeding_chunks,
        "skipped_files_due_to_segment_exceeding_limit": skipped_files,
        "num_split_files": len(summary_list),
        "split_files": summary_list
    }
    
    summary_file = os.path.join(summary_dir, f"{input_dir_name}.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    input_dir = "/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/txt_normal"
    output_dir = "/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/txt_splitted_h1"
    summary_dir = "/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/data_analysis"
    process_directory(input_dir, output_dir, summary_dir)
