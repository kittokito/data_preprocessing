import os
import sys
import shutil
import chardet  # エンコーディング検出ライブラリ

def is_same_content(existing_file, new_lines):
    """
    既存ファイルの最初の20行と new_lines（リスト）の最初の20行を比較する。
    行末の改行コードは除去して比較する。
    """
    try:
        with open(existing_file, 'r', encoding='utf-8') as f:
            existing_lines = [line.rstrip('\r\n') for line in f.readlines()]
        return existing_lines[:20] == new_lines[:20]
    except Exception:
        return False

def convert_to_plaintext(file_path, output_directory):
    """
    ファイルをプレーンテキスト形式に変換し、指定したディレクトリに保存する。
    同一のファイル名の場合、すでに存在するファイルと最初の20行を比較し、
      - 同一なら新規作成せず既存のファイルパスを返す
      - 異なるなら末尾に _1, _2 などの番号を付与して保存する
    """
    os.makedirs(output_directory, exist_ok=True)
    
    try:
        with open(file_path, 'rb') as infile:
            raw_data = infile.read()
            detected = chardet.detect(raw_data)
            encoding = detected['encoding']
            if encoding is None:
                encoding = 'shift_jis'  # デフォルトを shift_jis に設定
            text = raw_data.decode(encoding)
        
        new_lines = text.splitlines()

        base_name = os.path.basename(file_path)
        name, _ = os.path.splitext(base_name)
        
        # まず、候補ファイル名は「name.txt」
        candidate = os.path.join(output_directory, f"{name}.txt")
        
        if os.path.exists(candidate):
            if is_same_content(candidate, new_lines):
                # 既に同一の内容がある場合はそのまま返す
                return candidate
            counter = 1
            while True:
                candidate_numbered = os.path.join(output_directory, f"{name}_{counter}.txt")
                if os.path.exists(candidate_numbered):
                    if is_same_content(candidate_numbered, new_lines):
                        return candidate_numbered
                    counter += 1
                else:
                    candidate = candidate_numbered
                    break

        with open(candidate, 'w', encoding='utf-8') as outfile:
            outfile.write(text)

        return candidate
    except Exception as e:
        raise Exception(f"ファイル {file_path} の変換中にエラーが発生しました: {e}")

def merge_plaintext_files(directory, output_file, error_directory, temp_directory):
    """
    指定したディレクトリ内およびそのサブディレクトリ内のすべてのファイルを
    プレーンテキストに変換後、結合する。

    処理状況は全体の何%完了しているかを同一行上に更新して表示します。
    """
    os.makedirs(error_directory, exist_ok=True)
    os.makedirs(temp_directory, exist_ok=True)
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 事前に処理対象の非隠しファイル総数をカウント
    total_files = 0
    for root, dirs, files in os.walk(directory):
        total_files += len([f for f in files if not f.startswith('.')])
    
    print(f"処理対象のファイル数: {total_files}")
    processed_files = 0

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            total_lines = 0
            for root, dirs, files in os.walk(directory):
                for file in files:
                    # 隠しファイルはスキップ（ただしカウントはする）
                    if file.startswith('.'):
                        processed_files += 1
                        sys.stdout.write(f'\r進捗: {processed_files/total_files*100:.2f}%')
                        sys.stdout.flush()
                        continue
                    
                    processed_files += 1
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory)
                    
                    try:
                        # プレーンテキスト形式に変換
                        plaintext_file = convert_to_plaintext(file_path, temp_directory)
                        
                        # 結合処理
                        with open(plaintext_file, 'r', encoding='utf-8') as infile:
                            lines = infile.readlines()
                            total_lines += len(lines)
                            outfile.write(f"--- Start of {rel_path} ---\n")
                            outfile.writelines(lines)
                            outfile.write(f"\n--- End of {rel_path} ---\n\n")
                    except Exception as e:
                        # エラー発生時は改行してエラーメッセージを表示
                        sys.stdout.write(f"\nエラー: {rel_path} の処理中にエラー発生: {e}\n")
                        error_path = os.path.join(error_directory, os.path.basename(file))
                        shutil.move(file_path, error_path)
                        sys.stdout.write(f"    -> {rel_path} をエラー用ディレクトリへ移動\n")
                        sys.stdout.flush()
                    
                    # 進捗パーセンテージを更新
                    sys.stdout.write(f'\r進捗: {processed_files/total_files*100:.2f}%')
                    sys.stdout.flush()
            sys.stdout.write('\n')  # 進捗表示後に改行
        print(f"\nすべてのファイルが {output_file} に結合されました。")
        print(f"結合後のファイルは {total_lines} 行です。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 使用例（各ディレクトリのパスを適宜指定してください）
merge_plaintext_files(
    directory="/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/mnm_通常",
    output_file="/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/txt_merged/plc_normal_01.txt",
    error_directory="/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/mnm_encoding_error",
    temp_directory="/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/txt_normal"
)
