import os
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
from tqdm import tqdm
from transformers import AutoTokenizer
from config import COUNT_TOKENS_CONFIG, MODEL_NAME

# --- ファイルパスの設定 ---
jsonl_file = COUNT_TOKENS_CONFIG["jsonl_file"]
output_dir = COUNT_TOKENS_CONFIG["output_dir"]
filter_token_limit = COUNT_TOKENS_CONFIG["filter_token_limit"]
os.makedirs(output_dir, exist_ok=True)

# --- Hugging Face のトークナイザーを取得 ---
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# --- 総行数の取得 ---
with open(jsonl_file, 'r', encoding='utf-8') as f:
    total_lines = sum(1 for _ in f)

# --- テキストとタイトルの読み込み ---
texts = []
titles = []
with open(jsonl_file, 'r', encoding='utf-8') as f:
    for line in tqdm(f, total=total_lines, desc="テキスト読み込み", dynamic_ncols=True):
        data = json.loads(line)
        texts.append(data.get("text", ""))
        titles.append(data.get("title", "不明"))

# --- 一括トークン化とタイトルごとの集計（バッチ処理） ---
batch_size = 1000  # バッチサイズは必要に応じて調整
title_token_counts = {}  # タイトルごとのトークン数を保持
token_counts = []  # 全体の統計用

for i in tqdm(range(0, len(texts), batch_size), desc="トークン化", dynamic_ncols=True):
    batch_texts = texts[i: i+batch_size]
    batch_titles = titles[i: i+batch_size]
    batch_encoding = tokenizer(batch_texts, add_special_tokens=False)
    
    # バッチ内の各テキストのトークン数をタイトルごとに集計
    for title, token_ids in zip(batch_titles, batch_encoding["input_ids"]):
        if title not in title_token_counts:
            title_token_counts[title] = 0
        title_token_counts[title] += len(token_ids)
        token_counts.append(len(token_ids))  # 全体の統計用に追加

# タイトルごとのトークン数を出力
output_file = os.path.join(output_dir, 'title_token_counts.txt')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("タイトルごとの総トークン数\n")
    f.write("=" * 30 + "\n\n")
    for title, count in title_token_counts.items():
        f.write(f"{title}: {count}トークン\n")

print(f"タイトルごとの総トークン数を保存しました: {output_file}")

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

# --- ヒストグラムプロット1: 全体のデータ ---
fig, ax = plt.subplots(figsize=(10, 6))
bins = 50
ax.hist(token_counts, bins=bins, color='skyblue', edgecolor='black')
ax.set_title('Token Count Distribution (All Data)')
ax.set_xlabel('Token Count')
ax.set_ylabel('Frequency')
ax.grid(True)

# --- x軸の目盛り設定 ---
# 1) 目盛りの最大数を10に制限 (必要に応じて変更)
ax.xaxis.set_major_locator(ticker.MaxNLocator(10))

# 2) x軸ラベルを45度回転
ax.tick_params(axis='x', rotation=45)

# --- プロット画像の保存（全体） ---
input_filename = os.path.basename(jsonl_file)
png_filename_all = os.path.splitext(input_filename)[0] + "_all.png"
plot_path_all = os.path.join(output_dir, png_filename_all)

plt.savefig(plot_path_all, bbox_inches='tight')  # bbox_inches='tight' でラベル切れを防ぐ
plt.close()

print("全体のプロット結果を保存しました:", plot_path_all)

# --- 設定値以下のデータをフィルタリング ---
token_counts_filtered = [count for count in token_counts if count <= filter_token_limit]

if token_counts_filtered:
    # --- 設定値以下の統計値の計算 ---
    sum_tokens_filtered = sum(token_counts_filtered)
    avg_tokens_filtered = sum_tokens_filtered / len(token_counts_filtered)
    max_tokens_filtered = max(token_counts_filtered)
    min_tokens_filtered = min(token_counts_filtered)
    
    print(f"\n{filter_token_limit}トークン以下のデータ統計:")
    print(f"対象行数: {len(token_counts_filtered)}")
    print(f"総トークン数: {sum_tokens_filtered}")
    print(f"平均トークン数: {avg_tokens_filtered}")
    print(f"最大トークン数: {max_tokens_filtered}")
    print(f"最小トークン数: {min_tokens_filtered}")
    
    # --- ヒストグラムプロット2: 設定値以下のデータ ---
    fig, ax = plt.subplots(figsize=(10, 6))
    bins = 50
    ax.hist(token_counts_filtered, bins=bins, color='lightgreen', edgecolor='black')
    ax.set_title(f'Token Count Distribution (≤{filter_token_limit} tokens)')
    ax.set_xlabel('Token Count')
    ax.set_ylabel('Frequency')
    ax.grid(True)
    
    # --- x軸の目盛り設定 ---
    ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
    ax.tick_params(axis='x', rotation=45)
    
    # --- プロット画像の保存（設定値以下） ---
    png_filename_filtered = os.path.splitext(input_filename)[0] + f"_filtered_{filter_token_limit}.png"
    plot_path_filtered = os.path.join(output_dir, png_filename_filtered)
    
    plt.savefig(plot_path_filtered, bbox_inches='tight')
    plt.close()
    
    print(f"{filter_token_limit}トークン以下のプロット結果を保存しました:", plot_path_filtered)
else:
    print(f"{filter_token_limit}トークン以下のデータが見つかりませんでした。")
