import os
import json
import jaconv
from config import CONVERT_KANA_CONFIG

def convert_hankaku_to_zenkaku_kana(input_file, output_dir):
    """
    JSONLファイルの"text"フィールドに含まれる半角カタカナを全角カタカナに変換します。
    
    Parameters:
        input_file (str): 入力JSONLファイルのパス
        output_dir (str): 出力ディレクトリのパス
    """
    try:
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(output_dir, exist_ok=True)
        
        # 入力ファイル名から出力ファイル名を生成（末尾に_kanaを追加）
        input_filename = os.path.basename(input_file)
        name, ext = os.path.splitext(input_filename)
        output_filename = f"{name}_kana{ext}"
        output_file = os.path.join(output_dir, output_filename)
        
        converted_count = 0
        total_count = 0
        
        # JSONLファイルを読み込み、変換して出力
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # JSON行をパース
                    data = json.loads(line)
                    total_count += 1
                    
                    # "text"フィールドが存在する場合のみ変換
                    if "text" in data and data["text"]:
                        original_text = data["text"]
                        # 半角カタカナを全角カタカナに変換
                        converted_text = jaconv.hankaku2zenkaku(original_text, kana=True, ascii=False, digit=False)
                        
                        # 変換が行われた場合のみカウント
                        if original_text != converted_text:
                            converted_count += 1
                        
                        data["text"] = converted_text
                    
                    # 変換後のJSONを出力
                    json_line = json.dumps(data, ensure_ascii=False)
                    outfile.write(json_line + '\n')
                    
                except json.JSONDecodeError as e:
                    print(f"JSON解析エラー（行をスキップ）: {e}")
                    continue
        
        print(f"変換完了: {output_file}")
        print(f"処理した行数: {total_count}")
        print(f"変換が行われた行数: {converted_count}")
        
    except FileNotFoundError:
        print(f"エラー: 入力ファイルが見つかりません: {input_file}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def main():
    """
    設定ファイルから値を読み込んで変換を実行
    """
    input_file = CONVERT_KANA_CONFIG["input_file"]
    output_dir = CONVERT_KANA_CONFIG["output_dir"]
    
    print(f"入力ファイル: {input_file}")
    print(f"出力ディレクトリ: {output_dir}")
    print("半角カタカナ → 全角カタカナ変換を開始します...")
    
    convert_hankaku_to_zenkaku_kana(input_file, output_dir)

if __name__ == "__main__":
    main()
