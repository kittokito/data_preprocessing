import os
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from tqdm import tqdm
from transformers import AutoTokenizer

# --- ファイルパスの設定 ---
jsonl_file = './jsonl/jsonl_filtered/filtered_plc_01.jsonl'
output_dir = './analyzed_data/token_count_plot'
os.makedirs(output_dir, exist_ok=True)

# --- Hugging Face のトークナイザーを取得 ---
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-14B-Instruct")

# --- 総行数の取得 ---
with open(jsonl_file, 'r', encoding='utf-8') as f:
    total_lines = sum(1 for _ in f)

# --- テキスト一括読み込み ---
texts = []
with open(jsonl_file, 'r', encoding='utf-8') as f:
    for line in tqdm(f, total=total_lines, desc="テキスト読み込み", dynamic_ncols=True):
        texts.append(json.loads(line).get("text", ""))

# --- 一括トークン化（バッチ処理） ---
batch_size = 1000  # バッチサイズは必要に応じて調整
token_counts = []
for i in tqdm(range(0, len(texts), batch_size), desc="トークン化", dynamic_ncols=True):
    batch_texts = texts[i: i+batch_size]
    batch_encoding = tokenizer(batch_texts, add_special_tokens=False)
    token_counts.extend([len(ids) for ids in batch_encoding["input_ids"]])

# --- 統計値の計算 ---
if token_counts:
    sum_tokens = sum(token_counts)
    avg_tokens = sum_tokens / len(token_counts)
    max_tokens = max(token_counts)
    min_tokens = min(token_counts)
else:
    sum_tokens = avg_tokens = max_tokens = min_tokens = 0

print(f"総行数:{total_lines}")
print(f"総トークン数: {sum_tokens}")
print(f"平均トークン数: {avg_tokens}")
print(f"最大トークン数: {max_tokens}")
print(f"最小トークン数: {min_tokens}")

# --- ヒストグラムプロットの作成 ---
fig, ax = plt.subplots(figsize=(10, 6))
bins = 50
ax.hist(token_counts, bins=bins, color='skyblue', edgecolor='black')
ax.set_title('Token Count Distribution')
ax.set_xlabel('Token Count')
ax.set_ylabel('Frequency')
ax.grid(True)

# --- x軸の目盛り設定 ---
# 1) 目盛りの最大数を10に制限 (必要に応じて変更)
ax.xaxis.set_major_locator(ticker.MaxNLocator(10))

# 2) x軸ラベルを45度回転
ax.tick_params(axis='x', rotation=45)

# --- プロット画像の保存 ---
input_filename = os.path.basename(jsonl_file)
png_filename = os.path.splitext(input_filename)[0] + ".png"
plot_path = os.path.join(output_dir, png_filename)

plt.savefig(plot_path, bbox_inches='tight')  # bbox_inches='tight' でラベル切れを防ぐ
plt.close()

print("プロット結果を保存しました:", plot_path)
