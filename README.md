# データ前処理パイプライン

このプロジェクトは、テキストデータの前処理パイプラインを提供します。

## ディレクトリ構造

```
.
├── scripts/                      # Pythonスクリプト
│   ├── config.py                 # 設定ファイル
│   ├── mnm_to_txt.py             # MNMファイルをテキストに変換
│   ├── txt_to_jsonl.py           # テキストをJSONLに変換
│   ├── split_long_txt.py         # 長いテキストを分割
│   ├── split_train_val_jsonl.py  # JSONLをトレーニング/検証用に分割
│   ├── remove_short_jsonl.py     # 短いJSONLエントリを削除
│   ├── count_tokens.py           # トークン数をカウント
│   ├── count_file_folder.py      # ファイル/フォルダ数をカウント
│   ├── remove_files.py           # ファイルを削除
│   └── generate_sample_jsonl.py  # サンプルJSONLを生成
├── data/                         # データディレクトリ
│   ├── raw/                      # 元のデータ（mnmファイル）
│   │   ├── 通常/                 # 通常カテゴリのデータ
│   │   ├── STG命令使用/          # STG命令使用カテゴリのデータ
│   │   └── encoding_error/       # エンコーディングエラーのファイル
│   ├── processed/                # 処理済みデータ
│   │   ├── txt/                  # テキストファイル
│   │   │   ├── 通常/             # 通常カテゴリのテキスト
│   │   │   ├── STG命令使用/      # STG命令使用カテゴリのテキスト
│   │   │   ├── splitted_h1/      # h1タグで分割されたテキスト
│   │   │   ├── splitted_semicolon/ # セミコロンで分割されたテキスト
│   │   │   └── ...
│   │   └── jsonl/                # JSONLファイル
│   │       ├── original/         # 元のJSONLファイル
│   │       ├── filtered/         # フィルタリング済みJSONLファイル
│   │       ├── merged/           # マージされたJSONLファイル
│   │       ├── splitted_train-val/ # トレーニング/検証用に分割されたJSONL
│   │       └── ...
│   ├── output/                   # 最終出力データ
│   └── analysis/                 # 分析結果
│       ├── split_summary/        # 分割サマリー
│       └── token_count_plot/     # トークン数プロット
└── README.md                     # このファイル
```

## データ処理パイプライン

1. **mnm_to_txt.py**: .mnmファイルを.txtファイルに変換
2. **txt_to_jsonl.py**: .txtファイルを.jsonlファイルに変換
3. **split_long_txt.py**: 長いテキストファイルをトークン制限内に収まるように分割
4. **split_train_val_jsonl.py**: JSONLファイルをトレーニングセットとバリデーションセットに分割
5. **remove_short_jsonl.py**: 短いテキストを持つJSONLエントリを削除

## ユーティリティスクリプト

- **count_tokens.py**: テキストのトークン数をカウントし、統計情報を生成
- **count_file_folder.py**: ディレクトリ内のファイル数とフォルダ数をカウント
- **remove_files.py**: 指定したディレクトリ内のファイルを削除
- **generate_sample_jsonl.py**: JSONLファイルからサンプルを生成

## 使用方法

各スクリプトは設定ファイル（config.py）を使用します。スクリプトを実行する前に、config.pyで適切な設定を行ってください。

例:
```bash
# 設定ファイルを編集
vim scripts/config.py

# スクリプトを実行
python scripts/mnm_to_txt.py
python scripts/txt_to_jsonl.py
```

## 設定ファイル

config.pyには各スクリプトの設定が含まれています。主な設定項目は以下の通りです：

- **MODEL_NAME**: 使用するモデル名（トークン化に使用）
- **MNM_TO_TXT_CONFIG**: mnm_to_txt.pyの設定
- **TXT_TO_JSONL_CONFIG**: txt_to_jsonl.pyの設定
- **REMOVE_SHORT_JSONL_CONFIG**: remove_short_jsonl.pyの設定
- **SPLIT_LONG_TXT_CONFIG**: split_long_txt.pyの設定
- **SPLIT_TRAIN_VAL_JSONL_CONFIG**: split_train_val_jsonl.pyの設定
- **COUNT_TOKENS_CONFIG**: count_tokens.pyの設定
- **GENERATE_SAMPLE_JSONL_CONFIG**: generate_sample_jsonl.pyの設定
- **REMOVE_FILES_CONFIG**: remove_files.pyの設定
