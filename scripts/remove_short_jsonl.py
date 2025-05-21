import os
import json
import random
from config import REMOVE_SHORT_JSONL_CONFIG

def filter_jsonl_files(input_directory, output_directory, length_limit):
    try:
        # 出力フォルダが存在しない場合は作成する
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            print(f"出力フォルダ {output_directory} を作成しました。")

        # 入力ディレクトリ内のすべての.jsonlファイルを取得
        for file_name in os.listdir(input_directory):
            if file_name.endswith('.jsonl'):
                file_path = os.path.join(input_directory, file_name)

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

                # ランダムに50個の削除されたテキストを表示
                if removed_texts:
                    sample_texts = random.sample(removed_texts, min(50, len(removed_texts)))
                    print("削除された'text'値のサンプル:")
                    for text in sample_texts:
                        print("--------------------------------------------")
                        print(text)

                # 出力ファイルのパスを設定（ファイル名にプレフィックス "filtered_" を付与）
                new_file_name = "filtered_" + file_name
                new_file_path = os.path.join(output_directory, new_file_name)

                # フィルタリング後のデータを新しいファイルに保存
                with open(new_file_path, 'w', encoding='utf-8') as file:
                    file.write('\n'.join(filtered_lines))

                # 保存された行数と省かれた行数を表示
                print(f"{file_name} をフィルタリングしました。")
                print(f"  保存された行数: {len(filtered_lines)}")
                print(f"  省かれた行数: {len(removed_texts)}")
                print(f"  -> {new_file_name} に保存")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 設定ファイルから値を読み込む
input_directory = REMOVE_SHORT_JSONL_CONFIG["input_directory"]
output_directory = REMOVE_SHORT_JSONL_CONFIG["output_directory"]
length_limit = REMOVE_SHORT_JSONL_CONFIG["length_limit"]
filter_jsonl_files(input_directory, output_directory, length_limit)
