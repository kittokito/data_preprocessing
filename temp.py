def count_lines_in_file(file_path):
    """
    指定したファイルの行数をカウントして表示する。

    Args:
        file_path (str): ファイルのパス
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            line_count = sum(1 for _ in file)
        print(f"ファイル '{file_path}' は {line_count} 行です。")
    except Exception as e:
        print(f"ファイルを開く際にエラーが発生しました: {e}")

# 使用例
count_lines_in_file('/Users/nomura/Downloads/prepare_training_data/output01.txt')
