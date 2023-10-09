#
#　RFIDとバーコードのコードが一致しているかをチェックする
#　データがきちんと書かれているかどうか
#
#
#
import glob
import os
import pandas as pd
from models import Product_tran, BaseSrc
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date,ForeignKey, desc,asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv


load_dotenv('.env')


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




if __name__ == "__main__":
    rfid_df = pd.DataFrame(columns=['rfid_scode'])
    for filetag,scode in read_rfid_file('convert/check/ReadTag*.txt'):
        #print(f"scode: {filetag}/{scode}")
        new_row = {'rfid_scode': scode}
        rfid_df = rfid_df.append(new_row, ignore_index=True)
    print(rfid_df)

    bar_df = pd.DataFrame(columns=['bar_scode'])
    for filetag,items in read_bar_file('convert/check/ReadBarcode*.txt'):
        #print(f"scode: {filetag}/{items[0]}")
        any_code = items[0]
        if "?skey=" in any_code:
            scode = any_code.split("?skey=")[1] 
        elif "auction/" in items[0]:
            scode = any_code.split("/auction/")[1]
        else:
            scode = items[0]

        new_row = {'bar_scode': scode}
        bar_df = bar_df.append(new_row, ignore_index=True)
    print(bar_df)

    # 'outer'で両方のデータフレームを結合し、どちらに存在するかを示す_merge列を追加
    merged_df = pd.merge(rfid_df, bar_df, left_on='rfid_scode', right_on='bar_scode', how='outer', indicator=True)

    # 共通に存在するコード
    common_df = merged_df[merged_df['_merge'] == 'both']

    # rfid_dfには存在して、bar_dfには存在しないコード
    left_only_df = merged_df[merged_df['_merge'] == 'left_only']

    # bar_dfには存在して、rfid_dfには存在しないコード
    right_only_df = merged_df[merged_df['_merge'] == 'right_only']

    # 結果を表示（または必要に応じて保存）
    #print("Common Codes:")
    print("●バーコードにも、RFIDにも存在するもの:")
    print(common_df)

    #print("Right Only Codes:")
    print("●バーコードには存在して、RFIDには存在しないもの:")
    print(right_only_df)


    #print("Left Only Codes:")
    print("●RFIDには存在して、バーコードには存在しないもの:")
    print(left_only_df)


    for scode in bar_df['bar_scode']:
        product = check_stock(scode)
        print(f"product_qty: {scode}...{product.stock_qty}")
        if product is None:
            print(f"Attributes of Product_tran for scode {scode}....{product.stock_qty}")



    # bar_dfに新しい列 'stock_info' を追加し、check_stockの結果を格納
    bar_df['stock_info'] = bar_df['bar_scode'].apply(check_stock)

    # 在庫数量が0の行を抽出
    out_of_stock_df = bar_df[bar_df['stock_info'].apply(lambda x: x is not None and x.stock_qty == 0)]

    # 結果を表示
    print("Out of Stock Items:")
    print(out_of_stock_df)
