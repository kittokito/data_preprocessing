import os
import json
import random

def filter_jsonl_files(directory_path, length_limit):
    try:
        # ディレクトリ内のすべての.jsonlファイルを取得
        for file_name in os.listdir(directory_path):
            if file_name.endswith('.jsonl'):
                file_path = os.path.join(directory_path, file_name)

                # フィルタリングされたデータを格納するリスト
                filtered_lines = []
                removed_texts = []

                # ファイルを読み込む
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        try:
                            data = json.loads(line)
                            if 'text' in data and isinstance(data['text'], str):
                                if len(data['text']) > length_limit:
                                    filtered_lines.append(json.dumps(data, ensure_ascii=False))
                                else:
                                    removed_texts.append(data['text'])
                        except json.JSONDecodeError:
                            continue

                # ランダムに30個の削除されたテキストを表示
                if removed_texts:
                    sample_texts = random.sample(removed_texts, min(30, len(removed_texts)))
                    print("Sample of removed 'text' values:")
                    for text in sample_texts:
                        print("--------------------------------------------")
                        print(text)

                # 新しいファイル名の生成
                base_name, ext = os.path.splitext(file_name)
                if len(base_name) <= length_limit:
                    new_file_name = f"{base_name}_cut{length_limit}{ext}"
                else:
                    new_file_name = file_name

                new_file_path = os.path.join(directory_path, new_file_name)

                # フィルタリング後のデータを新しいファイルに保存
                with open(new_file_path, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(filtered_lines))

                print(f"Filtered {file_name}, remaining lines: {len(filtered_lines)} -> Saved as {new_file_name}")
    except Exception as e:
        print(f"An error occurred: {e}")

# 使用例
# 指定したディレクトリのパスに置き換えてください
directory_path = "/Users/nomura/Downloads/長野オートメーション/prepare_training_data/final_training_corpus"
length_limit = 50  # 可変長の制限値
filter_jsonl_files(directory_path, length_limit)
