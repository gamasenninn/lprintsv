#
#   Webに場所情報をおくる
#   このプログラムは参考にしてください。タグの読込みはそれぞれの独自の処理が必要です。
#   もちろんDBも独自のものとなります。
#
#   実行はapp直下で。(.envの関係)
#

import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import json
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date,ForeignKey, desc,asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import sys
import pandas as pd
import glob
import logging
import argparse
from models import Product_tran, BaseSrc

# ログの設定
logging.basicConfig(
    filename='upload_rfid.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)

load_dotenv('.env')

DEBUG=bool(int(os.environ['LOCATION_DEBUG']))
UPSERT=True

ALLOWED_TAGS = ["北店", "道場", "店舗","第2展示場"]

#------読込元データべース-----
#SQLALCHEMY_DATABASE_URL_SRC = os.environ['SQLALCHEMY_DATABASE_MYSQL']
engine_src = create_engine(os.environ['SQLALCHEMY_DATABASE_MYSQL'])
SessionLocal_src = sessionmaker(autocommit=False, autoflush=False, bind=engine_src)
db_src = SessionLocal_src()
#BaseSrc = declarative_base()

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

#リファクタリング
def request_to_web_api(url, method="GET", payload=None):
    auth = HTTPBasicAuth(
        os.environ['LOCATION_WEB_ID'], 
        os.environ['LOCATION_WEB_PASSWORD']
    )
    
    headers = {'Content-Type': 'application/json'} if payload else {}
    
    response = requests.request(
        method,
        url,
        data=json.dumps(payload) if payload else None,
        headers=headers,
        auth=auth
    )

    if response.json():
        return response.json()
    else:
        return {}

#
# Webから位置情報を取得する（1件分）
#
def get_location(scode):
    url = f"{os.environ['LOCATION_WEB_URL']}/?scode={scode}"
    response = request_to_web_api(url)
    return response[0] if response else {}
#
# Webから位置情報を取得する（複数件分）
# ローケーションデータ取得APIを叩いて、結果をDFで返す。
#
def get_location_all():
    url = f"{os.environ['LOCATION_WEB_URL']}/?gte=1&limit={os.environ['LOCATION_LOAD_LIMIT']}"
    return pd.DataFrame(request_to_web_api(url))

#
# Webにローケーションデータ（複数）をアップロードする。
#
def upload_locations(payload,mode=None):
    url = f"{os.environ['LOCATION_WEB_UPLOAD_URL']}"
    data = {'action': "insert_all", 'mode': mode, 'srcdata': payload}
    return request_to_web_api(url, method="POST", payload=data)


def convert_line(line):
    line = line.strip()
    try:
        # バイナリデータではなく、16進数表現のASCII文字列であることを確認
        decoded = bytes.fromhex(line).decode('ascii')
        decoded = decoded.rstrip('\x00')
        if '-' in str(decoded):
            return str(decoded)
        else:
            return ''
    except ValueError as e:
        # バイナリデータの場合、そのまま返す
        print("decode error skipped:", line)
        logging.error(f"Decode error for line '{line}': {e}")
        return ''

# ジェネレーターとしてファイルを読む
def read_rfid_file(pattern):
    allowed_tags = ALLOWED_TAGS  # 許可するタグ
    filenames = glob.glob(pattern)

    for file_path in filenames:
        # ログ・ファイルに処理するファイル名を書く
        logging.info(f"target file name: {file_path}")
        filetag = os.path.splitext(os.path.basename(file_path))[0]

        # filetag が allowed_tags リストに含まれていない場合、処理をスキップ
        if filetag not in allowed_tags:
            logging.warning(f"Skipping file {filetag} due to unrecognized tag.")
            print(f"リストにないタグ名です。スキップします。.....{filetag} ")
            continue  # 次のイテレーションに進む

        # ファイルを開き、内容を表示する
        print(f"読み込みします....{filetag}")
        with open(file_path, 'r') as f:
            for line in f:
                scode = convert_line(line.strip())
                if scode:
                    yield filetag, scode
        print(f"読み込みしました....{filetag}")

# 棚卸し日の取得
def get_stock_date():
    stock_date_time_str = input("棚卸日(yyyy-mm-dd hh:mm:ss):")
    if not stock_date_time_str:
        input("棚卸日が未定の場合はシステム時刻が採用されます。よろしいですか？")
        return pd.Timestamp.now()  # システムの現在時刻を使用
    else:
        return pd.Timestamp(stock_date_time_str)  # 文字列からTimestampオブジェクトを作成

# 文字列のクレンジング関数
def clean_string(s):
    if isinstance(s, str):
        t = s.replace('\u3000', ' ')
        t = t.replace("'","\\'")
    return t

def filter_and_prepare_df(df_new, stock_date_time):
    # 対象日付データをdatetime型に一括変換し、棚卸し日より前のデータをフィルタリング
    # ※棚卸日以降のデータは誰かが入力したものなので、そちらを優先するためである
 
    #データの正規化
    df_new['create_date'] = pd.to_datetime(df_new['create_date'])
    df_new['old_create_date'] = pd.to_datetime(df_new['old_create_date'])
    df_new['product_qty'].fillna(0, inplace=True)
    df_new['master_qty'].fillna(0, inplace=True)
    
    # 棚卸し日より前のデータと、場所があるもの、在庫があるものをフィルタリング
    filtered_df = df_new.loc[
        (df_new['old_create_date'] < df_new['create_date']) & 
        df_new['place'].notna() & 
        (df_new['master_qty'].astype(int) >= 0)
    ].copy()  # この時点で明示的にコピーを作成

    # 前処理を行う
    filtered_df['place'].fillna('', inplace=True)
    filtered_df.loc[:, 'title'] = filtered_df['title'].apply(clean_string)
    # 新しいcreate_dateとcategoryを設定
    #filtered_df['create_date'] = stock_date_time
    filtered_df['create_date'] = filtered_df['create_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    filtered_df['old_create_date'] = filtered_df['old_create_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    filtered_df['category'] = "rfid"
    
    # 必要なカラムだけを選択する。
    return filtered_df[['srcdata','title','scode','aucid','old_place','place','old_category','category','memo','old_create_date','create_date']]

# データフレームを小さなチャンクに分割し、各チャンクをAPIを使ってアップロードする。エラーが発生した場合は処理を中断する。
def upload_in_chunks(df_payload, mode=None,start_index=0, chunk_size=50):
    go_mode = mode if mode else "test"
    print(f"{go_mode}モードでアップロードします。")
    n = len(df_payload)
    for i in range(start_index, n, chunk_size):
        chunk = df_payload.iloc[i:i + chunk_size]
        dict_list_chunk = chunk.to_dict('records')
        resdata = upload_locations(dict_list_chunk,mode=go_mode)
        print(i, i + chunk_size, len(dict_list_chunk), ":", resdata['mode'], ":", resdata['message'], resdata['error'][0])
        
        if resdata['error'][0] != "00000":
            print(resdata)
            print("エラーのため処理を終了します")
            break
# Web APIから商品の位置情報を取得し、列名をリネームして初期データフレームを作成する。
def get_and_prepare_location_data():
    print("商品の位置情報をWebから読みます。")
    df = get_location_all()
    df = df.rename(columns={'place': 'old_place', 'category': 'old_category', 'create_date': 'old_create_date'})
    df.to_csv("df_initial.csv", encoding="cp932")
    return df

# RFIDタグのテキストファイルから商品コードと位置情報を読み込み、既存のデータフレームと外部結合する。
def read_and_merge_rfid_tags(df, stock_date_time):
    df_tana = pd.DataFrame()
    for filetag, scode in read_rfid_file("convert/rfid_tags/*.txt"):
        new_row = {'scode': scode, 'place': filetag, 'create_date': ''}
        df_tana = df_tana.append(new_row, ignore_index=True)

    if df_tana.empty:
        print("タグデータが存在しません。処理を終了します。")
        return None

    stock_date_time_str = stock_date_time.strftime('%Y-%m-%d %H:%M:%S')
    df_tana['create_date'] = stock_date_time_str
    merged_df = pd.merge(df, df_tana, on='scode', how='outer')
    merged_df.to_csv("df_merged.csv", encoding="cp932")
    return merged_df

# 商品マスタから在庫情報とメモを取得し、それらの情報をデータフレームに追加する。
def enrich_with_master_data(df):
    df['master_qty'] = 0
    df['master_memo'] = ""
    for idx, row in df.iterrows():
        product = check_stock(row['scode'])
        df.loc[idx, 'master_qty'] = product.stock_qty if product else -999
        df.loc[idx, 'master_memo'] = product.memo if product else ""
        if pd.isna(row['title']) or not row['title']:
            df.loc[idx, 'title'] = product.pname if product else ""
    df.to_csv("df_enriched.csv", encoding="cp932")
    return df

# データフレームから指定された条件に合う行をフィルタリングし、必要な列の前処理を施す。
def filter_and_prepare_for_upload(df, stock_date_time):
    df_filtered = filter_and_prepare_df(df, stock_date_time)
    df_filtered.to_csv("df_filtered.csv", encoding="cp932")
    return df_filtered

# データフレームの長さ（行数）を出力し、アップロードするかどうかを選択する。選択された場合はアップロードを実行。
def upload_data(df, noup,mode):
    print("対象追加数: ", len(df))
    if not noup:
        upload_in_chunks(df, mode=mode, start_index=0, chunk_size=50)
        print("アップロード終了しました。")
    else:
        print("--noupのため、アップロードはスキップされました。")

# 主要な関数を呼び出して全体のアップロード処理を制御するメイン関数
def upload_main(stock_date_time, noup=False, mode=None):
    df = get_and_prepare_location_data()
    if df is None:
        return

    df = read_and_merge_rfid_tags(df, stock_date_time)
    if df is None:
        return

    df = enrich_with_master_data(df)
    df_to_upload = filter_and_prepare_for_upload(df, stock_date_time)
    upload_data(df_to_upload, noup,mode)


if __name__ == "__main__":
    # コマンドライン引数の設定
    try:
        parser = argparse.ArgumentParser(description='RFID アップロードスクリプト')
        parser.add_argument('--noup', action='store_true', help='アップロードしない場合にこのフラグを指定')
        parser.add_argument('--mode', choices=['test', 'real'], help='テストモードか実戦モードを指定')

        args = parser.parse_args()
        
        stock_date_time = get_stock_date() # 棚卸し日を指定する
        upload_main(stock_date_time,noup=args.noup,mode=args.mode)

    except SystemExit:
        pass
    
