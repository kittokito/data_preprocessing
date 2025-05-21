import os
import shutil
from config import REMOVE_FILES_CONFIG

# 設定ファイルから削除対象のディレクトリパスを取得
target_directories = REMOVE_FILES_CONFIG["target_directories"]

def remove_files_in_directory(directory_path):
    """
    指定されたディレクトリ内のファイルを削除する
    
    Args:
        directory_path (str): 削除対象のディレクトリパス
    Returns:
        tuple: (削除成功件数, 削除失敗件数)
    """
    # ディレクトリの存在確認
    if not os.path.exists(directory_path):
        print(f"エラー: 指定されたパス '{directory_path}' が存在しません。")
        return 0, 0
    
    if not os.path.isdir(directory_path):
        print(f"エラー: 指定されたパス '{directory_path}' はディレクトリではありません。")
        return 0, 0
    
    # ディレクトリ内のファイル一覧を取得
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    
    if not files:
        print(f"指定されたディレクトリ '{directory_path}' にファイルが存在しません。")
        return 0, 0
    
    # 削除前の確認
    print(f"\n対象ディレクトリ: {directory_path}")
    print("以下のファイルを削除します:")
    for file in files:
        print(f"- {file}")
    
    # ファイルの削除
    deleted_count = 0
    error_count = 0
    
    for file in files:
        file_path = os.path.join(directory_path, file)
        try:
            os.remove(file_path)
            deleted_count += 1
            print(f"削除成功: {file}")
        except Exception as e:
            error_count += 1
            print(f"削除失敗: {file} - エラー: {str(e)}")
    
    return deleted_count, error_count

def main():
    if not target_directories:
        print("エラー: 削除対象のディレクトリが指定されていません。")
        print("スクリプト内の target_directories リストにパスを追加してください。")
        return
    
    # 削除前の最終確認
    print("削除対象のディレクトリ:")
    for directory in target_directories:
        print(f"- {directory}")
    
    confirmation = input("\n本当に削除を実行しますか？ (y/n): ")
    if confirmation.lower() != 'y':
        print("削除をキャンセルしました。")
        return
    
    # 各ディレクトリの処理
    total_deleted = 0
    total_errors = 0
    
    for directory in target_directories:
        deleted, errors = remove_files_in_directory(directory)
        total_deleted += deleted
        total_errors += errors
    
    # 最終結果の表示
    print(f"\n全体の処理結果:")
    print(f"- 処理したディレクトリ数: {len(target_directories)}個")
    print(f"- 削除成功: {total_deleted}件")
    print(f"- 削除失敗: {total_errors}件")

if __name__ == "__main__":
    main()
