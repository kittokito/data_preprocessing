import os
import json

def txt_files_to_jsonl(input_dirs, output_dir, output_filename, category, id_prefix):
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
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 使用例
input_directories = [
    "./txt/txt_sft",

]

category = "sft"  
id_prefix = "sample"     # バージョン番号
output_directory = "./jsonl/jsonl_sft/sample"  # 出力ディレクトリ
output_filename = f"plc_{category}_{id_prefix}.jsonl"  # 出力ファイル名

txt_files_to_jsonl(input_directories, output_directory, output_filename, category, id_prefix)
