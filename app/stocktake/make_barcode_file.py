#
# 手動で拾ってきたコードをReadBarcodeXXXXファイルに変換する
#
import argparse
import csv
import glob
import os

GO_DIR = "stocktake/check"

def convert_line(code):
    return code

def convert_to_hex(input_str):
    return ''.join(format(ord(char), '02x') for char in input_str)

# ジェネレーターとしてRFIDタグファイルを読む
def read_bar_simple_file(pattern):
    filenames = glob.glob(pattern)

    for file_path in filenames:
        # ログ・ファイルに処理するファイル名を書く
        filetag = os.path.splitext(os.path.basename(file_path))[0]

        # ファイルを開き、内容を表示する
        print(f"読み込みします....{filetag}")
        with open(file_path, 'r') as f:
            for line in f:
                scode = convert_line(line.strip())
                if scode:
                    yield filetag, scode
        print(f"読み込みしました....{filetag}")



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='手動で拾ってきたコードからバーコーソファイルを作成する')
    parser.add_argument('--noup', action='store_true', help='アップロードしない場合にこのフラグを指定')
    parser.add_argument('--mode', choices=['test', 'real'], help='テストモードか実戦モードを指定')

    args = parser.parse_args()

    out_file_name = "ReadBarcode20230000_00000.txt"

    with open(f"{GO_DIR}/{out_file_name}", 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
    #バーコードファイルを読む   

        for filetag, scode in read_bar_simple_file(f"{GO_DIR}/simple_bar*.txt"):
            hex_code = convert_to_hex(scode)
            print(filetag,scode,hex_code,"T")
            csv_writer.writerow([scode, hex_code, 'T'])



