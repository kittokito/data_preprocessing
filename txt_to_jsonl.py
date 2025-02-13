import os
import json

def txt_files_to_jsonl(input_dir, output_dir, output_filename, id_category, id_prefix):
    """
    指定されたディレクトリ内のすべての .txt ファイルを読み込み、
    各ファイルの内容とファイル名（拡張子除く）を JSON オブジェクトに変換し、
    そのオブジェクトに "id" キーを付与して、1行ずつ JSONL ファイルに出力します。
    
    "id" は、関数の引数で渡された id_category と id_prefix に連番（0から開始）をハイフンで連結して生成します。
    例: "normal-01-0", "normal-01-1" または "STG-01-0", "STG-01-1"
    
    Parameters:
        input_dir (str): .txt ファイルがある入力ディレクトリのパス。
        output_dir (str): 出力先ディレクトリのパス。
        output_filename (str): 出力する JSONL ファイルの名前（例："plc_normal_01.jsonl"）。
        id_category (str): id のカテゴリ。例: "normal" または "STG"。
        id_prefix (str): id の中間部分。例: "01" や "02"。
    """
    try:
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, output_filename)

        json_data = []
        counter = 0  # 連番カウンタ

        # 安定した順序で処理するためにファイル名でソート
        for file_name in sorted(os.listdir(input_dir)):
            if file_name.endswith('.txt'):
                file_path = os.path.join(input_dir, file_name)
                with open(file_path, 'r', encoding='utf-8') as in_f:
                    content = in_f.read().strip()
                # 拡張子を除いたタイトル
                title = os.path.splitext(file_name)[0]

                # id を id_category, id_prefix, 連番から生成
                json_id = f"{id_category}-{id_prefix}-{counter}"
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
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 使用例
input_directory = "/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/txt_STG"  # 入力ディレクトリ
output_directory = "/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/jsonl_merged"   # 出力ディレクトリ
output_filename = "plc_STG_01.jsonl"  # 出力ファイル名
id_category = "STG"  # "normal" または "STG"
id_prefix = "01"        # バージョン番号

txt_files_to_jsonl(input_directory, output_directory, output_filename, id_category, id_prefix)
