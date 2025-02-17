import os
import json
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from transformers import AutoTokenizer  # transformers を利用

# --- ファイルパスの設定 ---
jsonl_file = '/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/sft.jsonl'
output_dir = '/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/token_count_plot'
os.makedirs(output_dir, exist_ok=True)

# --- Hugging Face のトークナイザーを取得 ---
# Qwen/Qwen2.5-Coder-14B-Instruct 用のトークナイザーを読み込みます
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-14B-Instruct")

# --- 総行数の取得 ---
with open(jsonl_file, 'r', encoding='utf-8') as f:
    total_lines = sum(1 for _ in f)

# --- 各エントリのトークン数をカウント ---
token_counts = []
with open(jsonl_file, 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, start=1):
        data = json.loads(line)
        text = data.get("text", "")
        # トークン化（必要に応じて add_special_tokens の有無を調整）
        tokens = tokenizer.encode(text, add_special_tokens=False)
        token_counts.append(len(tokens))
        
        # 進捗表示（同一ライン上で更新）
        progress = idx / total_lines * 100
        print(f"\r進捗: {progress:.2f}%", end="", flush=True)
print()  # 最終的な改行

# --- 統計値の計算 ---
if token_counts:
    avg_tokens = sum(token_counts) / len(token_counts)
    max_tokens = max(token_counts)
    min_tokens = min(token_counts)
else:
    avg_tokens = max_tokens = min_tokens = 0

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

# --- 裾部分の拡大 inset を追加 ---
# 90パーセンタイル以上の範囲をズーム表示
percentile_90 = np.percentile(token_counts, 90)
# inset の大きさや位置は適宜調整してください
inset_ax = inset_axes(ax, width="40%", height="40%", loc='upper right')
inset_ax.hist(token_counts, bins=bins, color='skyblue', edgecolor='black')
inset_ax.set_xlim(percentile_90, max_tokens)
inset_ax.set_title('Tail Zoom', fontsize=10)
inset_ax.grid(True)

# 入力ファイル名に合わせたPNGファイル名を作成
input_filename = os.path.basename(jsonl_file)                 # 例: sft.jsonl
png_filename = os.path.splitext(input_filename)[0] + ".png"      # 例: sft.png
plot_path = os.path.join(output_dir, png_filename)

plt.savefig(plot_path)
plt.close()

print("プロット結果を保存しました:", plot_path)
