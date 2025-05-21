import os
import sys
import shutil
import chardet  # エンコーディング検出ライブラリ
from config import MNM_TO_TXT_CONFIG

def convert_to_plaintext(file_path, output_directory, base_directory):
    """
    ファイルをプレーンテキスト形式に変換し、指定したディレクトリに保存する。
    同一のファイル名の場合、内容比較はせずに常に番号を振って新しいファイルを作成する。
    指定したディレクトリからの相対パスの最初の部分をファイル名の先頭に追加する。
    深い階層がある場合は、その階層も含める。
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

        # 指定したディレクトリからの相対パスを取得
        rel_path = os.path.relpath(file_path, base_directory)
        rel_path_parts = rel_path.split(os.sep)
        
        # ファイル名を除いたパス部分を取得
        path_prefix = "_".join(rel_path_parts[:-1]) if len(rel_path_parts) > 1 else "unknown"
        
        base_name = os.path.basename(file_path)
        name, _ = os.path.splitext(base_name)
        
        # 相対パスの部分をファイル名の先頭に追加
        prefixed_name = f"{path_prefix}_{name}"
        
        # 候補ファイル名は「prefixed_name.txt」
        candidate = os.path.join(output_directory, f"{prefixed_name}.txt")
        
        # 同名ファイルが存在する場合は、内容比較せずに番号を振る
        if os.path.exists(candidate):
            counter = 1
            while True:
                candidate_numbered = os.path.join(output_directory, f"{prefixed_name}_{counter}.txt")
                if not os.path.exists(candidate_numbered):
                    candidate = candidate_numbered
                    break
                counter += 1

        with open(candidate, 'w', encoding='utf-8') as outfile:
            outfile.write(text)

        return candidate
    except Exception as e:
        raise Exception(f"ファイル {file_path} の変換中にエラーが発生しました: {e}")

def process_files(directory, output_directory, error_directory, debug=False):
    """
    指定したディレクトリ内およびそのサブディレクトリ内のすべてのファイルを
    プレーンテキスト形式に変換する。結合はせず、個別のファイルとして保存する。

    処理状況は全体の何%完了しているかを同一行上に更新して表示します。
    """
    os.makedirs(error_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)
    
    # 事前に処理対象の非隠しファイル総数をカウント
    total_files = 0
    for root, dirs, files in os.walk(directory):
        total_files += len([f for f in files if not f.startswith('.')])
    
    print(f"処理対象のファイル数: {total_files}")
    processed_files = 0
    converted_files = 0

    try:
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
                    # デバッグモードの場合、処理中のファイルパスを表示
                    if debug:
                        print(f"処理中: {file_path}")
                        print(f"親フォルダ: {os.path.basename(os.path.dirname(file_path))}")
                    
                    # プレーンテキスト形式に変換（指定したディレクトリを渡す）
                    plaintext_file = convert_to_plaintext(file_path, output_directory, directory)
                    converted_files += 1
                    
                    # デバッグモードの場合、変換後のファイル名を表示
                    if debug:
                        print(f"変換後: {os.path.basename(plaintext_file)}")
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
        print(f"\n{converted_files}個のファイルが {output_directory} に変換されました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 設定ファイルから値を読み込む
process_files(
    directory=MNM_TO_TXT_CONFIG["directory"],
    output_directory=MNM_TO_TXT_CONFIG["output_directory"],
    error_directory=MNM_TO_TXT_CONFIG["error_directory"],
    debug=MNM_TO_TXT_CONFIG["debug"]  # デバッグ情報を表示する場合はTrueに設定
)
