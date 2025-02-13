import os

def split_text_file(input_file, output_dir):
    # ファイルを読み込む
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ;<h1/>で分割
    parts = content.split(';<h1/>')
    
    # 元のファイル名から拡張子を除いた部分を取得
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # 分割したファイルを保存
    for i, part in enumerate(parts):
        if part.strip():  # 空でない部分のみ保存
            output_file = os.path.join(output_dir, f"{base_name}_part{i+1}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(part.strip())
    
    return len([p for p in parts if p.strip()])

def process_directory(input_dir, output_dir):
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)
    
    # ディレクトリ内のすべてのtxtファイルを処理
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_file = os.path.join(input_dir, filename)
            num_parts = split_text_file(input_file, output_dir)
            print(f"Processed {filename}: Split into {num_parts} parts")

if __name__ == "__main__":
    input_dir = "mnm_plaintext"
    output_dir = "splitted_mnm_plaintext"
    process_directory(input_dir, output_dir)
