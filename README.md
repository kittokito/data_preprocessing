# データ前処理パイプライン

このプロジェクトは、テキストデータの前処理パイプラインを提供します。

## ディレクトリ構造

```
.
├── scripts/                              # Pythonスクリプト
│   ├── config.py                         # 設定ファイル
│   ├── mnm_to_txt.py                     # MNMファイルをテキストに変換
│   ├── txt_to_jsonl.py                   # テキストをJSONLに変換
│   ├── split_long_txt.py                 # 長いテキストを分割
│   ├── split_long_jsonl.py               # 長いJSONLエントリを分割
│   ├── split_long_jsonl_with_ratio.py    # 長いJSONLエントリを指定比率で分割
│   ├── merge_jsonl.py                    # 2つのJSONLファイルを結合
│   ├── split_train_val_jsonl.py          # JSONLをトレーニング/検証用に分割
│   ├── remove_short_jsonl.py             # 短いJSONLエントリを削除
│   ├── count_tokens.py                   # トークン数をカウント・可視化
│   ├── count_file_folder.py              # ファイル/フォルダ数をカウント
│   ├── remove_files.py                   # ファイルを削除
│   ├── generate_sample_jsonl.py          # サンプルJSONLを生成
│   └── convert_kana.py                   # 半角カタカナを全角カタカナに変換
├── data/                                 # データディレクトリ
│   ├── raw/                              # 元のデータ（mnmファイル）
│   │   ├── 通常/                         # 通常カテゴリのデータ
│   │   ├── STG命令使用/                  # STG命令使用カテゴリのデータ
│   │   ├── SFTデータに使った機器/        # SFTデータ用の機器データ
│   │   └── encoding_error/               # エンコーディングエラーのファイル
│   ├── processed/                        # 処理済みデータ
│   │   ├── txt/                          # テキストファイル
│   │   │   ├── 通常/                     # 通常カテゴリのテキスト
│   │   │   ├── STG命令使用/              # STG命令使用カテゴリのテキスト
│   │   │   ├── exceeding_limit_h1/       # h1タグ分割で制限超過したファイル
│   │   │   ├── exceeding_limit_semicolon/# セミコロン分割で制限超過したファイル
│   │   │   ├── filtered/                 # フィルタリング済みテキスト
│   │   │   └── merged/                   # マージされたテキスト
│   │   └── jsonl/                        # JSONLファイル
│   │       ├── original/                 # 元のJSONLファイル
│   │       ├── deduplicated/             # 重複除去済みJSONLファイル
│   │       ├── exceeding_limit/          # トークン制限超過ファイル
│   │       ├── long_text_splitted/       # 長文分割済みJSONLファイル
│   │       ├── short_removed/            # 短文除去済みJSONLファイル
│   │       └── splitted_train-val/       # トレーニング/検証用に分割されたJSONL
│   ├── output/                           # 最終出力データ（未使用）
│   └── analysis/                         # 分析結果
│       ├── split_summary/                # 分割処理のサマリー
│       └── token_count_plot/             # トークン数の分布プロット
└── README.md                             # このファイル
```

## データ処理パイプライン

1. **mnm_to_txt.py**: .mnmファイルを.txtファイルに変換
2. **txt_to_jsonl.py**: .txtファイルを.jsonlファイルに変換
3. **split_long_txt.py**: 長いテキストファイルをトークン制限内に収まるように分割
4. **split_long_jsonl.py**: 長いJSONLエントリをトークン制限内に収まるように分割（JSONLファイルの各エントリのtextフィールドを処理）
5. **split_long_jsonl_with_ratio.py**: 長いJSONLエントリを指定された比率（128-512、512-2000、2000-8000、8000-15872トークン）で分割
6. **merge_jsonl.py**: 2つのJSONLファイルを結合してIDでソート
7. **split_train_val_jsonl.py**: JSONLファイルをトレーニングセットとバリデーションセットに分割
8. **remove_short_jsonl.py**: 短いテキストを持つJSONLエントリを削除

## ユーティリティスクリプト

- **count_tokens.py**: JSONLファイルのトークン数をカウントし、統計情報とヒストグラムを生成。タイトルごとの総トークン数も出力
- **count_file_folder.py**: ディレクトリ内のファイル数とフォルダ数をカウント
- **remove_files.py**: 指定したディレクトリ内のファイルを削除
- **generate_sample_jsonl.py**: JSONLファイルからサンプルを生成
- **convert_kana.py**: JSONLファイルの"text"フィールドに含まれる半角カタカナを全角カタカナに変換。変換後のファイル名は末尾に"_kana"が追加される

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

- **MODEL_NAME**: 使用するモデル名（トークン化に使用、デフォルト: Qwen/Qwen2.5-Coder-14B-Instruct）
- **MNM_TO_TXT_CONFIG**: mnm_to_txt.pyの設定
- **TXT_TO_JSONL_CONFIG**: txt_to_jsonl.pyの設定
- **REMOVE_SHORT_JSONL_CONFIG**: remove_short_jsonl.pyの設定
- **SPLIT_LONG_TXT_CONFIG**: split_long_txt.pyの設定
- **SPLIT_LONG_JSONL_CONFIG**: split_long_jsonl.pyの設定（split_long_jsonl_with_ratio.pyでも使用）
- **MERGE_JSONL_CONFIG**: merge_jsonl.pyの設定
- **SPLIT_TRAIN_VAL_JSONL_CONFIG**: split_train_val_jsonl.pyの設定
- **COUNT_TOKENS_CONFIG**: count_tokens.pyの設定
- **GENERATE_SAMPLE_JSONL_CONFIG**: generate_sample_jsonl.pyの設定
- **REMOVE_FILES_CONFIG**: remove_files.pyの設定
- **CONVERT_KANA_CONFIG**: convert_kana.pyの設定

## スクリプトの詳細

### split_long_jsonl_with_ratio.py
長いJSONLエントリを以下の目標比率で分割します：
- 15%: 128-512トークン（テスト、小関数、短ドキュメント）
- 25%: 512-2000トークン（一般的な関数集合／スクリプト）
- 40%: 2000-8000トークン（中規模ファイル・ノートブック）
- 20%: 8000-15872トークン（大規模ライブラリ／マルチクラスファイル）

### merge_jsonl.py
2つのJSONLファイルを結合し、IDでソートして出力します。重複IDの検出機能も含まれています。

### count_tokens.py
JSONLファイルの各エントリのトークン数を計算し、以下を出力します：
- 統計情報（総トークン数、平均、最大、最小）
- トークン数分布のヒストグラム（PNG形式）
- タイトルごとの総トークン数（テキストファイル）
