import os
import json

# 指定されたディレクトリ内の.txtファイルを結合してJSONLファイルにする
def txt_files_to_jsonl(input_dir, output_file):
    """
    指定されたディレクトリ内のすべての.txtファイルを読み込み、
    各ファイルをJSON形式のオブジェクトに変換し、JSONLファイルとして出力します。
    各行が独立したJSONオブジェクトとなります。

    Parameters:
        input_dir (str): 入力ディレクトリのパス。
        output_file (str): 出力するJSONLファイルのパス。
    """
    try:
        json_data = []
        for file_name in os.listdir(input_dir):
            # ファイルが.txtであることを確認
            if file_name.endswith('.txt'):
                file_path = os.path.join(input_dir, file_name)
                with open(file_path, 'r', encoding='utf-8') as in_f:
                    content = in_f.read().strip()  # ファイル内容を読み込んでトリム
                    title = os.path.splitext(file_name)[0]  # .txt拡張子を削除
                    json_entry = {
                        "title": title,
                        "text": content
                    }
                    json_data.append(json_entry)
        
        # JSONLファイルとして出力
        with open(output_file, 'w', encoding='utf-8') as out_f:
            for entry in json_data:
                json_line = json.dumps(entry, ensure_ascii=False)
                out_f.write(json_line + '\n')
        
        print(f"JSONLファイルが作成されました: {output_file}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 使用例
input_directory = "/Users/nomura/Downloads/長野オートメーション/prepare_training_data/splitted_mnm_plaintext"  # .txtファイルがあるディレクトリ
output_jsonl_file = "output01.jsonl"  # 出力するJSONLファイル名

txt_files_to_jsonl(input_directory, output_jsonl_file)
