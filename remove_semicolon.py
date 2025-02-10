import re

def remove_text_after_semicolon(input_file, output_file):
    """
    入力ファイルの各行において、セミコロン（;）以降の部分を削除し、新しいファイルに保存する。

    Args:
        input_file (str): 入力ファイルのパス
        output_file (str): 出力ファイルのパス
    """
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # セミコロン以降を削除
            cleaned_line = re.split(r';', line, maxsplit=1)[0]
            outfile.write(cleaned_line + '\n')

# 使用例
remove_text_after_semicolon(
    '/Users/nomura/Downloads/prepare_training_data/output01.txt',
     '/Users/nomura/Downloads/prepare_training_data/no_semicolon.txt'
     )