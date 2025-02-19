import json
import random
import os

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

# 使い方の例
split_jsonl(
    file_path="./jsonl/jsonl_filtered/filtered_plc_01.jsonl",
    train_ratio=0.95,
    output_dir="./jsonl/jsonl_splitted_train-val",
    train_output="plc_train_01.jsonl",
    val_output="plc_val_01.jsonl"
)
