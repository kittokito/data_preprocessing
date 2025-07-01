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
    "directory": "./data/raw/STG命令使用",
    "output_directory": "./data/processed/txt/STG命令使用",
    "error_directory": "./data/raw/encoding_error/STG命令使用",
    "debug": False
}

# txt_to_jsonl.py の設定
TXT_TO_JSONL_CONFIG = {
    "input_directories": "./data/processed/txt/通常",
    "output_dir": "./data/processed/jsonl/original",
    "output_filename": "plc_normal_05-1_kana.jsonl",
    "category": "normal",
    "id_prefix": "05",
    "use_delimiter": True,  # デリミタを使用するかどうか
    "delimiter": ";<h1/>"  # ファイルを分割するデリミタ（use_delimiterがTrueの場合のみ使用）
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
    "input_dir": "./data/processed/jsonl/deduplicated/plc_normal_01-3.jsonl",
    "output_dir": "./data/processed/jsonl/long_text_splitted",
    "exceeding_dir": "./data/processed/jsonl/exceeding_limit_h1",
    "summary_dir": "./data/analysis/split_summary",
    "delimiter": ";<h1/>",  # ;<h1/> or \n;
    "token_limit": 15872
}

# split_long_jsonl.py の設定
SPLIT_LONG_JSONL_CONFIG = {
    "model_name": MODEL_NAME,
    "input_file": "./data/processed/jsonl/exceeding_limit/h1/plc_normal_05-2_exceeding.jsonl",
    "output_file": "./data/processed/jsonl/long_text_splitted/plc_normal_05-2_semicolon.jsonl",
    "exceeding_file": "./data/processed/jsonl/exceeding_limit/semicolon/plc_normal_05-2_exceeding.jsonl",
    "summary_dir": "./data/analysis/split_summary",
    "delimiter": "\n;",  # ;<h1/> or \n;
    "token_limit": 15872
}


# split_train_val_jsonl.py の設定
SPLIT_TRAIN_VAL_JSONL_CONFIG = {
    "file_path": "./data/processed/jsonl/long_text_splitted/plc_normal_05-3.jsonl",
    "train_ratio": 0.95,
    "output_dir": "./data/processed/jsonl/splitted_train-val",
    "train_output": "plc_normal_05-3_train.jsonl",
    "val_output": "plc_normal_05-3_val.jsonl",
    "seed": 42
}


# その他のスクリプト
"""
- merge_jsonl.py: JSONLファイルを結合
- count_tokens.py: JSONLファイルのトークン数をカウント
- generate_sample_jsonl.py: サンプルJSONLファイルを生成
- remove_files.py: 不要なファイルを削除
"""

# merge_jsonl.py の設定
MERGE_JSONL_CONFIG = {
    "file1_path": "./data/processed/jsonl/long_text_splitted/plc_normal_05-2_h1.jsonl",
    "file2_path": "./data/processed/jsonl/long_text_splitted/plc_normal_05-2_semicolon.jsonl",
    "output_path": "./data/processed/jsonl/long_text_splitted/plc_normal_05-3.jsonl"
}


# count_tokens.py の設定
COUNT_TOKENS_CONFIG = {
    "jsonl_file": './data/processed/jsonl/exceeding_limit/semicolon/plc_normal_05-2_exceeding.jsonl',
    "output_dir": './data/analysis/token_count_plot',
    "filter_token_limit": 8192  # フィルタリング用のトークン制限値
}

# generate_sample_jsonl.py の設定
GENERATE_SAMPLE_JSONL_CONFIG = {
    "input_filename": "./data/processed/jsonl/deduplicated/plc_normal_05-2.jsonl",
    "output_folder": "./data/processed/jsonl/sample",
    "output_filename": "sample_plc_normal_05-2.jsonl",
    "num_samples": 300,
    "max_tokens": 16384
}

# remove_files.py の設定
REMOVE_FILES_CONFIG = {
    "target_directories": [
        "./data/processed/txt/通常",
        # 必要に応じて他のディレクトリを追加
    ]
}

# convert_kana.py の設定
CONVERT_KANA_CONFIG = {
    "input_file": "./data/processed/jsonl/original/plc_normal_05-1_kana.jsonl",
    "output_dir": "./data/processed/jsonl/kana"
}

# merge_jsonl_by_title.py の設定
MERGE_JSONL_BY_TITLE_CONFIG = {
    "input_file": "./data/processed/jsonl/deduplicated/plc_normal_05-2.jsonl",
    "output_file": "./data/processed/jsonl/merged/merged_plc_normal_05-2.jsonl",
    "text_delimiter": "\n;<h1/>"  # テキスト結合時の区切り文字
}
