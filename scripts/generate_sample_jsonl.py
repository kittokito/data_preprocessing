import json
import random
import os
from transformers import AutoTokenizer
from config import GENERATE_SAMPLE_JSONL_CONFIG

def main():
    # 設定ファイルから値を読み込む
    input_filename = GENERATE_SAMPLE_JSONL_CONFIG["input_filename"]
    output_folder = GENERATE_SAMPLE_JSONL_CONFIG["output_folder"]
    output_filename = GENERATE_SAMPLE_JSONL_CONFIG["output_filename"]
    
    num_samples = GENERATE_SAMPLE_JSONL_CONFIG["num_samples"]
    max_tokens = GENERATE_SAMPLE_JSONL_CONFIG["max_tokens"]

    # 出力フォルダが存在しない場合は作成
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 出力ファイルのフルパスを作成
    output_file_path = os.path.join(output_folder, output_filename)

    # Qwen/Qwen2.5-Coder-32B の tokenizer をロード
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-32B-Instruct", use_fast=True)

    # 入力ファイルから全エントリを読み込む
    data = []
    with open(input_filename, "r", encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                data.append(entry)
            except json.JSONDecodeError as e:
                print(f"JSONのパースに失敗しました: {e}")

    # エントリ数が足りなければ全件使用、足りる場合は無作為に num_samples 件を抽出
    if len(data) < num_samples:
        print(f"警告: 入力ファイルには {len(data)} 件しかなく、{num_samples} 件に満たないため、全件を使用します。")
        sampled_data = data
    else:
        sampled_data = random.sample(data, num_samples)

    # 各エントリの "text" フィールドをチェックし、トークン数が32700を超えている場合は切り詰める
    cut_count = 0
    for entry in sampled_data:
        if "text" in entry:
            tokens = tokenizer.encode(entry["text"])
            if len(tokens) > max_tokens:
                truncated_tokens = tokens[:max_tokens]
                entry["text"] = tokenizer.decode(truncated_tokens, skip_special_tokens=True)
                cut_count += 1

    # 新しい JSONL ファイルとして指定したフォルダに保存
    with open(output_file_path, "w", encoding="utf-8") as outfile:
        for entry in sampled_data:
            json_line = json.dumps(entry, ensure_ascii=False)
            outfile.write(json_line + "\n")

    print(f"カットされたエントリ数: {cut_count}")
    print(f"出力ファイルのパス: {output_file_path}")

if __name__ == "__main__":
    main()
