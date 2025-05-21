"""
データ前処理スクリプト用の設定ファイル
各スクリプトで使用するパスや引数をここで一括管理します
"""

# 共通設定
MODEL_NAME = "Qwen/Qwen2.5-Coder-14B-Instruct"


# 学習データの作成に関する設定
"""
- mnm_to_txt.py: MNMファイルをテキストファイルに変換
- txt_to_jsonl.py: テキストファイルをJSONL形式に変換
- remove_short_jsonl.py: 短いJSONLファイルを除去
- split_long_txt.py: 長いテキストファイルを分割
- split_train_val_jsonl.py: JSONLファイルをtrain/valに分割
- generate_sample_jsonl.py: サンプルJSONLファイルを生成
"""

# mnm_to_txt.py
MNM_TO_TXT_CONFIG = {
    "directory": "./data/raw/通常",
    "output_directory": "./data/processed/txt/通常",
    "error_directory": "./data/raw/encoding_error",
    "debug": False
}

# txt_to_jsonl.py の設定
TXT_TO_JSONL_CONFIG = {
    "input_directories": "./data/processed/txt/通常",
    "output_dir": "./data/processed/jsonl/original",
    "output_filename": "plc_通常_02.jsonl",
    "category": "通常",
    "id_prefix": "02"
}

# remove_short_jsonl.py の設定
REMOVE_SHORT_JSONL_CONFIG = {
    "input_directory": "./data/processed/jsonl/merged",
    "output_directory": "./data/processed/jsonl/filtered",
    "length_limit": 200
}

# split_long_txt.py の設定
SPLIT_LONG_TXT_CONFIG = {
    "model_name": MODEL_NAME,
    "input_dir": "./data/processed/txt/exceeding_limit_h1",
    "output_dir": "./data/processed/txt/splitted_semicolon",
    "exceeding_dir": "./data/processed/txt/exceeding_limit_semicolon",
    "summary_dir": "./data/analysis/split_summary",
    "delimiter": "\n;",  # ;<h1/> or \n;
    "label": "通常",  # 通常 or STG命令使用
    "token_limit": 16350
}


# split_train_val_jsonl.py の設定
SPLIT_TRAIN_VAL_JSONL_CONFIG = {
    "file_path": "./data/processed/jsonl/filtered/filtered_plc_01.jsonl",
    "train_ratio": 0.95,
    "output_dir": "./data/processed/jsonl/splitted_train-val",
    "train_output": "plc_train_01.jsonl",
    "val_output": "plc_val_01.jsonl",
    "seed": 42
}


# その他のスクリプト
"""
- count_tokens.py: JSONLファイルのトークン数をカウント
- generate_sample_jsonl.py: サンプルJSONLファイルを生成
- remove_files.py: 不要なファイルを削除
"""

# count_tokens.py の設定
COUNT_TOKENS_CONFIG = {
    "jsonl_file": './data/processed/jsonl/sft/plc_sft_sample.jsonl',
    "output_dir": './data/analysis/token_count_plot'
}

# generate_sample_jsonl.py の設定
GENERATE_SAMPLE_JSONL_CONFIG = {
    "input_filename": "./data/processed/jsonl/merged/plc_normal_01.jsonl",
    "output_folder": "./data/processed/jsonl/sample",
    "output_filename": "plc_sample_01.jsonl",
    "num_samples": 1280,
    "max_tokens": 32700
}

# remove_files.py の設定
REMOVE_FILES_CONFIG = {
    "target_directories": [
        "./data/processed/txt/通常",
        # 必要に応じて他のディレクトリを追加
    ]
}







