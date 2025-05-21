import json
import random
import os
from config import SPLIT_TRAIN_VAL_JSONL_CONFIG

def split_jsonl(file_path, train_ratio=0.8, output_dir="./", train_output="train.jsonl", val_output="val.jsonl", seed=42):
    """
    指定したJSONLファイルをtrainとvalにリスト単位で分割し、指定フォルダに保存する。
    
    :param file_path: 入力JSONLファイルのパス
    :param train_ratio: trainデータの割合（デフォルト80%）
    :param output_dir: 出力フォルダのパス（デフォルトはカレントディレクトリ）
    :param train_output: trainデータの出力ファイル名
    :param val_output: valデータの出力ファイル名
    :param seed: 乱数シード
    """
    random.seed(seed)
    
    # 出力フォルダを作成（存在しない場合）
    os.makedirs(output_dir, exist_ok=True)
    
    # JSONLのデータを読み込む
    with open(file_path, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    
    # データをシャッフル
    random.shuffle(data)
    
    # 分割
    train_size = int(len(data) * train_ratio)
    train_data = data[:train_size]
    val_data = data[train_size:]
    
    # 出力ファイルのパス
    train_path = os.path.join(output_dir, train_output)
    val_path = os.path.join(output_dir, val_output)
    
    # train.jsonlに書き込み
    with open(train_path, "w", encoding="utf-8") as f:
        for entry in train_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    # val.jsonlに書き込み
    with open(val_path, "w", encoding="utf-8") as f:
        for entry in val_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print(f"Train data: {len(train_data)} samples → {train_path}")
    print(f"Validation data: {len(val_data)} samples → {val_path}")

# 設定ファイルから値を読み込む
split_jsonl(
    file_path=SPLIT_TRAIN_VAL_JSONL_CONFIG["file_path"],
    train_ratio=SPLIT_TRAIN_VAL_JSONL_CONFIG["train_ratio"],
    output_dir=SPLIT_TRAIN_VAL_JSONL_CONFIG["output_dir"],
    train_output=SPLIT_TRAIN_VAL_JSONL_CONFIG["train_output"],
    val_output=SPLIT_TRAIN_VAL_JSONL_CONFIG["val_output"],
    seed=SPLIT_TRAIN_VAL_JSONL_CONFIG["seed"]
)
