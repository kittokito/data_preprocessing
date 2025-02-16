import os
import sys

def count_files(directory):
    # 指定ディレクトリ内の各エントリについて、ファイルならカウント
    return sum(1 for entry in os.listdir(directory) if os.path.isfile(os.path.join(directory, entry)))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python count_files.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"{directory} は有効なディレクトリではありません。")
        sys.exit(1)
    
    file_count = count_files(directory)
    print(f"{directory} に含まれるファイル数は {file_count} 個です。")
