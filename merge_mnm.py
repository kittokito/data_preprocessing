import os
import shutil
import chardet  # エンコーディング検出ライブラリ

def convert_to_plaintext(file_path, output_directory):
    """
    ファイルをプレーンテキスト形式に変換し、指定したディレクトリに保存する。

    Args:
        file_path (str): 元のファイルのパス
        output_directory (str): プレーンテキストファイルを保存するディレクトリ

    Returns:
        str: プレーンテキストファイルのパス
    """
    try:
        with open(file_path, 'rb') as infile:
            raw_data = infile.read()
            detected = chardet.detect(raw_data)
            encoding = detected['encoding']

            if encoding is None:
                encoding = 'shift_jis'  # デフォルトを shift_jis に設定

            text = raw_data.decode(encoding)

            # プレーンテキストファイルの保存
            base_name = os.path.basename(file_path)
            plaintext_file = os.path.join(output_directory, f"{os.path.splitext(base_name)[0]}.txt")

            with open(plaintext_file, 'w', encoding='utf-8') as outfile:
                outfile.write(text)

            return plaintext_file
    except Exception as e:
        raise Exception(f"ファイル {file_path} の変換中にエラーが発生しました: {e}")

def merge_plaintext_files(directory, output_file, error_directory, temp_directory):
    """
    指定したディレクトリ内のすべてのファイルをプレーンテキストに変換後、結合する。

    Args:
        directory (str): 入力ファイルが格納されているフォルダのパス
        output_file (str): 出力ファイルのパス
        error_directory (str): エラーが発生したファイルを移動するフォルダのパス
        temp_directory (str): 一時的なプレーンテキストファイルを保存するフォルダのパス
    """
    # 必要なディレクトリの作成
    os.makedirs(error_directory, exist_ok=True)
    os.makedirs(temp_directory, exist_ok=True)

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            total_lines = 0
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)

                if not os.path.isfile(file_path):
                    continue

                try:
                    # プレーンテキスト形式に変換
                    plaintext_file = convert_to_plaintext(file_path, temp_directory)

                    # 結合処理
                    with open(plaintext_file, 'r', encoding='utf-8') as infile:
                        lines = infile.readlines()
                        total_lines += len(lines)
                        outfile.write(f"--- Start of {file} ---\n")
                        outfile.writelines(lines)
                        outfile.write(f"\n--- End of {file} ---\n\n")
                except Exception as e:
                    print(f"{file} を処理中にエラーが発生しました: {e}")
                    error_path = os.path.join(error_directory, file)
                    shutil.move(file_path, error_path)

        print(f"すべてのファイルが {output_file} に結合されました。")
        print(f"結合後のファイルは {total_lines} 行です。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 使用例
merge_plaintext_files(
    directory="/Users/nomura/Downloads/長野オートメーション/prepare_training_data/splitted_mnm_plaintext",
    output_file="output01.txt",
    error_directory="/Users/nomura/Downloads/長野オートメーション/prepare_training_data/encoding_error",
    temp_directory="/Users/nomura/Downloads/長野オートメーション/prepare_training_data/temp_plaintext"
)
