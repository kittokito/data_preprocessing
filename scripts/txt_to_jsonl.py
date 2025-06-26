import os
import json
from config import TXT_TO_JSONL_CONFIG

def txt_files_to_jsonl(input_dirs, output_dir, output_filename, category, id_prefix, use_delimiter=False, delimiter="\n;"):
    """
    指定されたディレクトリ（またはディレクトリのリスト）内のすべての .txt ファイルを読み込み、
    各ファイルの内容とファイル名（拡張子除く）を JSON オブジェクトに変換し、
    そのオブジェクトに "id" キーを付与して、1行ずつ JSONL ファイルに出力します。
    
    "id" は、関数の引数で渡された category と id_prefix に連番（0から開始）をハイフンで連結して生成します。
    例: "normal-01-0", "normal-01-1" または "STG-01-0", "STG-01-1"
    
    Parameters:
        input_dirs (str or list): .txt ファイルがある入力ディレクトリのパス、またはそのリスト。
        output_dir (str): 出力先ディレクトリのパス。
        output_filename (str): 出力する JSONL ファイルの名前（例："plc_normal_01.jsonl"）。
        category (str): id のカテゴリ。例: "normal" または "STG"。
        id_prefix (str): id の中間部分。例: "01" や "02"。
        use_delimiter (bool): デリミタを使用してファイルを分割するかどうか。デフォルトはFalse。
        delimiter (str): ファイルを分割するデリミタ。デフォルトは"\n;"。
    """
    try:
        # 入力が文字列の場合はリストに変換
        if isinstance(input_dirs, str):
            input_dirs = [input_dirs]
        
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, output_filename)

        json_data = []
        counter = 0  # 連番カウンタ

        # 各ディレクトリごとに .txt ファイルを処理
        for input_dir in input_dirs:
            # 安定した順序で処理するためにファイル名でソート
            for file_name in sorted(os.listdir(input_dir)):
                if file_name.endswith('.txt'):
                    file_path = os.path.join(input_dir, file_name)
                    with open(file_path, 'r', encoding='utf-8') as in_f:
                        content = in_f.read().strip()
                    # 拡張子を除いたタイトル
                    title = os.path.splitext(file_name)[0]

                    if use_delimiter:
                        # デリミタを使用してファイルを分割
                        blocks = content.split(delimiter)
                        for block_index, block in enumerate(blocks):
                            block = block.strip()
                            if block:  # 空のブロックは無視
                                # id を category, id_prefix, 連番から生成
                                json_id = f"{category}-{id_prefix}-{counter}"
                                counter += 1

                                # タイトルにブロック番号を追加
                                block_title = f"{title}_block_{block_index}"

                                json_entry = {
                                    "id": json_id,
                                    "title": block_title,
                                    "text": block
                                }
                                json_data.append(json_entry)
                    else:
                        # 従来の処理（1ファイル1エントリ）
                        # id を category, id_prefix, 連番から生成
                        json_id = f"{category}-{id_prefix}-{counter}"
                        counter += 1

                        json_entry = {
                            "id": json_id,
                            "title": title,
                            "text": content
                        }
                        json_data.append(json_entry)

        # JSONL ファイルとして出力（1行に1つの JSON オブジェクト）
        with open(output_file, 'w', encoding='utf-8') as out_f:
            for entry in json_data:
                json_line = json.dumps(entry, ensure_ascii=False)
                out_f.write(json_line + '\n')

        print(f"JSONLファイルが作成されました: {output_file}")
        print(f"処理した行数: {len(json_data)}")
        if use_delimiter:
            print(f"デリミタ '{delimiter}' を使用してファイルを分割しました")
        else:
            print("従来の処理（1ファイル1エントリ）で処理しました")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 設定ファイルから値を読み込む
input_directories = TXT_TO_JSONL_CONFIG["input_directories"]
category = TXT_TO_JSONL_CONFIG["category"]
id_prefix = TXT_TO_JSONL_CONFIG["id_prefix"]
output_directory = TXT_TO_JSONL_CONFIG["output_dir"]
output_filename = TXT_TO_JSONL_CONFIG["output_filename"]
use_delimiter = TXT_TO_JSONL_CONFIG.get("use_delimiter", False)
delimiter = TXT_TO_JSONL_CONFIG.get("delimiter", "\n;")

txt_files_to_jsonl(input_directories, output_directory, output_filename, category, id_prefix, use_delimiter, delimiter)
