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
SQLALCHEMY_DATABASE_URL_SRC = os.environ['SQLALCHEMY_DATABASE_MYSQL']
engine_src = create_engine(SQLALCHEMY_DATABASE_URL_SRC)
SessionLocal_src = sessionmaker(autocommit=False, autoflush=False, bind=engine_src)
db_src = SessionLocal_src()
BaseSrc = declarative_base()

#-------MODEL------
class Product_tran(BaseSrc):
    __tablename__ = "V_商品_入出庫"

    id = Column(Integer, primary_key=True, index=True, name="ID")
    scode = Column(String, index=True, name="コード")
    pname = Column(String, name="商品名")
    stock_qty = Column(Integer, name="在庫数量")
    stock_price = Column(Integer, name="単価")
    receipt_date = Column(DateTime, name="日付")
    sale_price = Column(Integer, name="販売価格")
    sale_date = Column(DateTime, name="販売日付")
    sale_person = Column(String, name="販売担当者")
    delivery_person = Column(String, name="納品担当者")
    disporsal_date = Column(DateTime, name="廃棄日付")
    disporsal_person = Column(String, name="廃棄担当者")
    memo = Column(String, name="備考")
    sale_class = Column(String, name="販売区分")
    category = Column(String, name="区分")
    in_qty = Column(Integer, name="入庫数量")
    person = Column(String, name="社員名")
    vendor_no = Column(Integer, name="取引先No")
    vendor_name = Column(String, name="取引先名")
    last_update = Column(DateTime,name="_LastUpdate")

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
    
def ____check_stock(scode):
    product = (
        db_src.query(Product_tran)
        .filter(Product_tran.scode == scode)
        .first()
    )

    if product:
        return product.stock_qty
    else:
        return(-999)
#
# scodeに対応するタイトルをデータベースから取得する
#
def get_title_from_db(scode):
    product = (
        db_src.query(Product_tran)
        .filter(Product_tran.scode == scode)
        .first()
    )
    if product:
        return product.pname  # 商品名を返す
    else:
        return None
#
# Webから位置情報を取得する（1件分）
#
def get_location(scode):

    url = f"{os.environ['LOCATION_WEB_URL']}/?scode={scode}"
    response = requests.get(url,auth=HTTPBasicAuth(
        os.environ['LOCATION_WEB_ID'], 
        os.environ['LOCATION_WEB_PASSWORD']
    ))
    if response.json():
        return response.json()[0]
    else:
        return {}

#
# Webから位置情報を取得する（複数件分）
# ローケーションデータ取得APIを叩いて、結果をDFで返す。
#
def get_location_all():

    # GETリクエストを送るURL
    url = f"{os.environ['LOCATION_WEB_URL']}/?gte=1&limit={os.environ['LOCATION_LOAD_LIMIT']}"

    # リクエストを送信
    response = requests.get(url,auth=HTTPBasicAuth(
        os.environ['LOCATION_WEB_ID'], 
        os.environ['LOCATION_WEB_PASSWORD']
    ))
    return pd.DataFrame(response.json())

 
def upload_locations(payload):

    # POSTリクエストを送るURL
    url = f"{os.environ['LOCATION_WEB_UPLOAD_URL']}"
    #print("url:",url)

    # 送信するデータ
    data = {
		'action': "insert_all",
        'mode': "test",
		'srcdata': payload,
    }
    # リクエストを送信
    response = requests.post(url, 
                             data=json.dumps(data),
                             headers={'Content-Type': 'application/json'},
                             auth=HTTPBasicAuth(
                                os.environ['LOCATION_WEB_ID'], 
                                os.environ['LOCATION_WEB_PASSWORD']
                             ))

    # 応答のステータスコードとテキストを表示
    #print('Status code:', response.status_code)
    #print('Response text:', response.text.message)
    return response

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


def upload_in_chunks(df_payload, start_index=0, chunk_size=50):
    n = len(df_payload)
    for i in range(start_index, n, chunk_size):
        chunk = df_payload.iloc[i:i + chunk_size]
        dict_list_chunk = chunk.to_dict('records')
        ret = upload_locations(dict_list_chunk)
        resdata = json.loads(ret.text)
        print(i, i + chunk_size, len(dict_list_chunk), ":", resdata['mode'], ":", resdata['message'], resdata['error'][0])
        
        if resdata['error'][0] != "00000":
            print(resdata)
            print("エラーのため処理を終了します")
            break


def main():
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='RFID アップロードスクリプト')
    parser.add_argument('--noup', action='store_true', help='アップロードしない場合にこのフラグを指定')
    args = parser.parse_args()

    # 棚卸し日を指定する、指定した日付を棚卸日stock_date_timeとしておく
    stock_date_time = get_stock_date()

    # 在庫が存在する商品の位置情報をWebから読み、DFに格納する
    # ※ここでは最新の棚卸しデータを参照する。
    print("商品の位置情報をWebから読みます。")
    df = get_location_all()
    df = df.rename(columns={'place': 'old_place'})
    df = df.rename(columns={'category': 'old_category'})
    df = df.rename(columns={'create_date': 'old_create_date'})
    df.to_csv("df.csv",encoding="cp932") #デバッグのためのCSV保存

    # タグ読み込みdf_tanaに格納する
    df_tana =  pd.DataFrame()
    for filetag,scode in read_rfid_file("convert/rfid_tags/*.txt"):
        #print(filetag,scode)      
        new_row = {'scode': scode, 'place': filetag,'create_date': ''}
        df_tana = df_tana.append(new_row, ignore_index=True)
    if df_tana.empty:
        print("タグデータが存在しません。処理を終了します。")
        return

    stock_date_time_str = stock_date_time.strftime('%Y-%m-%d %H:%M:%S')
    df_tana['create_date'] = stock_date_time_str

    # 現在在庫の位置情報,読み込んだタグの情報をマージする
    df_new = pd.merge(df, df_tana, on='scode', how='outer')

    # マスターの数量を代入しておく。状態チェックのため
    df_new['master_qty'] = 0
    df_new['master_memo'] = ""
    for idx, row in df_new.iterrows():
        product   = check_stock(row['scode'])
        df_new.loc[idx, 'master_qty'] = product.stock_qty if product else -999
        df_new.loc[idx, 'master_memo'] = product.memo if product else ""
        #current_title = df_new.loc[idx, 'title']
        #print(idx,current_title)
        if pd.isna(row['title']) or not row['title']:
            df_new.loc[idx, 'title'] = product.pname if product else ""
    df_new.to_csv("tana_scode.csv",encoding="cp932") #デバッグのためのCSV保存
    
    # 対象の棚卸日、以前のデータを抽出する
    # さらに、RFIDデータ抽出し、JSONペイロードを作成する（条件:場所があるもの、在庫あるもの）
    # ※棚卸日以降のデータは誰かが入力したものなので、そちらを優先するためである
    df_payload = filter_and_prepare_df(df_new, stock_date_time)
    df_payload.to_csv("stocked_rfid.csv",encoding="cp932") #デバッグのためのCSV保存
    
    # 在庫があるものだけを抽出してアップロードする
    # 50行ごとにDataFrameを分割して処理
    # start_indexがあることで、エラーがあった場合、データの開始位置を指定してそのデータから処理を続けられるようにできる。
    print("対象追加数: ",len(df_payload))
    #upload_in_chunks(df_payload,start_index=0,chunk_size=50)
    if not args.noup:
        upload_in_chunks(df_payload, start_index=0, chunk_size=50)
        print("アップロード終了しました。")
    else:
        print("アップロードはスキップされました。")

if __name__ == "__main__":
    main()