import os
import sys

def count_files_and_dirs(directory):
    file_count = 0
    dir_count = 0
    
    # 指定ディレクトリ内の各エントリについて、ファイルとディレクトリを分けてカウント
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isfile(full_path):
            file_count += 1
        elif os.path.isdir(full_path):
            dir_count += 1
    
    return file_count, dir_count

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python temp.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"{directory} は有効なディレクトリではありません。")
        sys.exit(1)
    
    file_count, dir_count = count_files_and_dirs(directory)
    print(f"{directory} に含まれるファイル数は {file_count} 個です。")
    print(f"{directory} に含まれるフォルダ数は {dir_count} 個です。")
