import os
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
        # new_lines は text.splitlines() の結果なので、改行は含まれていない
        return existing_lines[:20] == new_lines[:20]
    except Exception:
        return False

def convert_to_plaintext(file_path, output_directory):
    """
    ファイルをプレーンテキスト形式に変換し、指定したディレクトリに保存する。
    同一のファイル名の場合、すでに存在するファイルと最初の20行を比較し、
      - 同一なら新規作成せず既存のファイルパスを返す
      - 異なるなら末尾に _1, _2 などの番号を付与して保存する

    Args:
        file_path (str): 元のファイルのパス
        output_directory (str): プレーンテキストファイルを保存するディレクトリ

    Returns:
        str: プレーンテキストファイルのパス
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
        
        # 新たに得たテキストの行リスト（改行文字は含まない）
        new_lines = text.splitlines()

        base_name = os.path.basename(file_path)
        name, _ = os.path.splitext(base_name)
        
        # まず、候補ファイル名は「name.txt」
        candidate = os.path.join(output_directory, f"{name}.txt")
        
        # すでに同名のファイルがある場合は、最初の20行を比較
        if os.path.exists(candidate):
            if is_same_content(candidate, new_lines):
                print(f"既に同一のファイル {candidate} が存在するため、スキップします。")
                return candidate
            # 同一でなければ、番号付きのファイル名を試す
            counter = 1
            while True:
                candidate_numbered = os.path.join(output_directory, f"{name}_{counter}.txt")
                if os.path.exists(candidate_numbered):
                    if is_same_content(candidate_numbered, new_lines):
                        print(f"既に同一のファイル {candidate_numbered} が存在するため、スキップします。")
                        return candidate_numbered
                    counter += 1
                else:
                    candidate = candidate_numbered
                    break

        # candidate が存在しない場合は新規作成
        with open(candidate, 'w', encoding='utf-8') as outfile:
            outfile.write(text)

        return candidate
    except Exception as e:
        raise Exception(f"ファイル {file_path} の変換中にエラーが発生しました: {e}")

def merge_plaintext_files(directory, output_file, error_directory, temp_directory):
    """
    指定したディレクトリ内およびそのサブディレクトリ内のすべてのファイルをプレーンテキストに変換後、結合する。

    Args:
        directory (str): 入力ファイルが格納されているフォルダのパス
        output_file (str): 出力ファイルのパス（指定ディレクトリ内に保存される）
        error_directory (str): エラーが発生したファイルを移動するフォルダのパス
        temp_directory (str): 一時的なプレーンテキストファイルを保存するフォルダのパス
    """
    os.makedirs(error_directory, exist_ok=True)
    os.makedirs(temp_directory, exist_ok=True)
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 事前に処理対象のファイル総数をカウント
    total_files = 0
    for root, dirs, files in os.walk(directory):
        # 隠しファイル（.で始まるもの）は除外
        total_files += len([f for f in files if not f.startswith('.')])
    print(f"処理対象のファイル数: {total_files}")

    processed_files = 0

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            total_lines = 0
            for root, dirs, files in os.walk(directory):
                for file in files:
                    # 隠しファイル（.で始まるもの）はスキップ
                    if file.startswith('.'):
                        print(f"スキップ: {os.path.join(root, file)} (隠しファイル)")
                        continue
                    processed_files += 1
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory)
                    
                    print(f"[{processed_files}/{total_files}] {rel_path} を処理中...")
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
                        
                        print(f"[{processed_files}/{total_files}] {rel_path} の処理完了")
                    except Exception as e:
                        print(f"[{processed_files}/{total_files}] {rel_path} の処理中にエラー発生: {e}")
                        error_path = os.path.join(error_directory, os.path.basename(file))
                        shutil.move(file_path, error_path)
                        print(f"[{processed_files}/{total_files}] {rel_path} をエラー用ディレクトリへ移動")

        print(f"\nすべてのファイルが {output_file} に結合されました。")
        print(f"結合後のファイルは {total_lines} 行です。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 使用例（各ディレクトリのパスを適宜指定してください）
merge_plaintext_files(
    directory="/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/mnm_STG命令使用",
    output_file="/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/txt_merged/plc_STG_1-1.txt",
    error_directory="/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/mnm_encoding_error",
    temp_directory="/Users/nomura/02_Airion/長野オートメーション/prepare_training_data/txt_original"
)
