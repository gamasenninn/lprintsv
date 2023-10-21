#
#　RFIDとバーコードのコードが一致しているかをチェックする
#　データがきちんと書かれているかどうか
#
import glob
import os
import pandas as pd
from models import Product_tran, PostingItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import re


load_dotenv('.env')

# 在庫チェック用のDBを準備する
engine_src = create_engine(os.environ['SQLALCHEMY_DATABASE_MYSQL'])
SessionLocal_src = sessionmaker(autocommit=False, autoflush=False, bind=engine_src)
db_src = SessionLocal_src()


#
# 在庫チェック
#
def check_stock(scode):
    product = (
        db_src.query(Product_tran)
        .filter(Product_tran.scode == scode)
        .first()
    )
    return product or None

def check_posting_item_by_aucid(aucid):
    postingItem = (
        db_src.query(PostingItem)
        .filter(PostingItem.aucid == aucid)
        .first()
    )
    return postingItem or None

def get_stock_all():
    product = (
        db_src.query(Product_tran)
        .filter(Product_tran.stock_qty >= 1)
        .all()
    )
    return product or None


#
# HEX文字列をアスキー文字列に変換する
# -がない文字列は正規データとしてみなさない
# (例:12345-1)
def convert_line(line):
    line = line.strip()
    try:
        # バイナリデータではなく、16進数表現のASCII文字列であることを確認
        decoded = bytes.fromhex(line).decode('ascii')
        decoded = decoded.rstrip('\x00')
        if '-' in str(decoded):
            return str(decoded)
        else:
            print("Decode error for line but not include (-): ", line)
            return ''
    except ValueError as e:
        # バイナリデータの場合、そのまま返す
        print("decode error skipped:", line)
        return ''

# ジェネレーターとしてRFIDタグファイルを読む
def read_rfid_file(pattern):
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

# ジェネレーターとしてバーコードファイルを読む
def read_bar_file(pattern):
    filenames = glob.glob(pattern)

    for file_path in filenames:
        # ログ・ファイルに処理するファイル名を書く
        filetag = os.path.splitext(os.path.basename(file_path))[0]

        # ファイルを開き、内容を表示する
        print(f"読み込みします....{filetag}")
        with open(file_path, 'r') as f:
            for line in f:
                #scode = convert_line(line.strip())
                items = line.split(',')
                yield filetag, items
        print(f"読み込みしました....{filetag}")

def parse_filetag(filetag,prefix="ReadBarcode"):
    # 正規表現を使用して年月日、時間、および店舗情報を抽出

    match = re.match(f'{prefix}'+r'(\d{8})_(\d{6})_(.+)', filetag)
    if match:
        date_str, time_str, location = match.groups()
        # 日付と時間を指定されたフォーマットで整形し、連結
        formatted_datetime = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
        return formatted_datetime, location
    else:
        print(f"Failed to parse filetag: {filetag}")
        return None

if __name__ == "__main__":
    pass