import os
import glob

def merge_jsonl_files(input_dir, output_dir, output_filename):
    """
    指定した入力ディレクトリ内の全ての JSONL ファイルを1つにまとめ、
    指定した出力ディレクトリに指定されたファイル名で保存する関数

    Parameters:
        input_dir (str): JSONL ファイルが格納された入力ディレクトリのパス
        output_dir (str): 出力先ディレクトリのパス
        output_filename (str): マージ後の出力ファイル名
    """
    # 指定入力ディレクトリ内の *.jsonl ファイルを取得
    jsonl_files = glob.glob(os.path.join(input_dir, '*.jsonl'))
    if not jsonl_files:
        print("指定された入力ディレクトリに JSONL ファイルが見つかりません。")
        return

    # 出力ディレクトリが存在しない場合は作成する
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, output_filename)

    with open(output_file, 'w', encoding='utf-8') as out_f:
        for file in jsonl_files:
            print(f"マージ中: {file}")
            with open(file, 'r', encoding='utf-8') as in_f:
                for line in in_f:
                    out_f.write(line)
    print(f"{len(jsonl_files)} 個のファイルを {output_file} にマージしました。")

if __name__ == "__main__":
    # ここで入力ディレクトリ、出力ディレクトリ、出力ファイル名を指定します
    input_directory = "./jsonl/jsonl_merged"       # JSONL ファイルがある入力ディレクトリのパス
    output_directory = "./"      # 出力先ディレクトリのパス
    output_filename = "plc_01.jsonl"          # 出力ファイル名

    merge_jsonl_files(input_directory, output_directory, output_filename)
