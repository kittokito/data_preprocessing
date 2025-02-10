import os

def count_lines_in_jsonl_files(directory_path):
    total_lines = 0
    try:
        # ディレクトリ内のすべてのファイルを取得
        for file_name in os.listdir(directory_path):
            # .jsonl拡張子のファイルを対象とする
            if file_name.endswith('.jsonl'):
                file_path = os.path.join(directory_path, file_name)
                # ファイルの行数をカウント
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = sum(1 for line in file)
                    total_lines += lines
                    print(f"{file_name}: {lines} lines")
        print(f"Total lines in all .jsonl files: {total_lines}")
    except Exception as e:
        print(f"An error occurred: {e}")

# 使用例
# 指定したディレクトリのパスに置き換えてください
directory_path = "/Users/nomura/Downloads/長野オートメーション/prepare_training_data/final_training_corpus"
count_lines_in_jsonl_files(directory_path)
