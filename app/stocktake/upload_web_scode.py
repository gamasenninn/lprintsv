#
#   Webに場所情報をおくる
#   このプログラムは参考にしてください。タグの読込みはそれぞれの独自の処理が必要です。
#   もちろんDBも独自のものとなります。
#
#   実行はapp直下で。(.envの関係)
#
"""
Web在庫       タグの状態  マスター  状態                棚卸対象  処理
----------------------------------------------------------------------
読み込めた     ある        1以上    在庫あり            ◯       棚卸処理
読み込めた     ある        0        DB未同期            ◯       同期処理
読み込めた     なし        1以上    在庫見つけてない              在庫を見つける（人力）
読み込めた     なし        0        DB未同期                     同期処理
----------------------------------------------------------------------
読み込まない   ある        1以上    DB未同期かタグ未装着         同期処理
読み込まない   ある        0        処理済か復活在庫か備品か      調査
読み込まない   ある        -999     マスター登録前               マスター登録
"""
#
#
import os
from dotenv import load_dotenv
import pandas as pd
import logging
import argparse
from tools.tana_web_api import get_location_all,upload_in_chunks
from tools.rfid_bar_tool import check_stock,read_rfid_file,parse_filetag
from tools.rfid_bar_tool import get_stock_all
import numpy as np

TAGS_DIR = 'stocktake/rfid_tags'
OUT_DIR = 'stocktake'

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

#ALLOWED_TAGS = ["北店", "道場", "店舗","第2展示場"]

class FormatError(Exception):
    pass

# 文字列のクレンジング関数
def clean_string(s):
    if isinstance(s, str):
        t = s.replace('\u3000', ' ')
        t = t.replace("'","\\'")
    return t

# 対象日付データをdatetime型に一括変換し、棚卸し日より前のデータをフィルタリング
# ※棚卸日以降のデータは誰かが入力したものなので、そちらを優先するためである
def filter_and_prepare_df(df_new):

    df_new['product_qty'].fillna(0, inplace=True)
    df_new['master_qty'].fillna(0, inplace=True)

    # 棚卸し日より前のデータと、場所があるもの、在庫があるものをフィルタリング
    filtered_df = df_new.loc[
        #(df_new['old_create_date'] < df_new['create_date']) & 
        df_new['place'].notna() & 
        (df_new['master_qty'].astype(int) >= 0)
    ].copy()  # この時点で明示的にコピーを作成

    filtered_df['category'] = "rfid"

    # 必要なカラムだけを選択する。
    return filtered_df[['srcdata','title','scode','aucid','old_place','place','old_category','category','memo','old_create_date','create_date']]


    return df_new
 
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


# Web APIから商品の位置情報を取得し、列名をリネームして初期データフレームを作成する。
def get_and_prepare_location_data():
    print("商品の位置情報をWebから読みます。")
    df = get_location_all()
    df = df.rename(columns={'place': 'old_place', 'category': 'old_category', 'create_date': 'old_create_date'})
    df.to_csv(f"{OUT_DIR}/df_initial.csv", encoding="cp932")
    return df

# RFIDタグのテキストファイルから商品コードと位置情報を読み込み、既存のデータフレームと外部結合する。
def read_and_merge_rfid_tags(df):
    df_tana = pd.DataFrame()
    for filetag, scode in read_rfid_file(f"{TAGS_DIR}/*.txt"):
        result = parse_filetag(filetag,prefix="ReadTag")
        if result:
            date_time,location = result
        else:
            raise FormatError("format error")
        print(f"scode: {filetag}/{scode}/{date_time}/{location}")

        new_row = {'scode': scode, 'place': location, 'create_date': date_time}
        df_tana = df_tana.append(new_row, ignore_index=True)

    if df_tana.empty:
        print("タグデータが存在しません。処理を終了します。")
        return None

    #stock_date_time_str = stock_date_time.strftime('%Y-%m-%d %H:%M:%S')
    #df_tana['create_date'] = stock_date_time_str
    df_tana = df_tana.drop_duplicates(subset='scode')

    df_tana.to_csv(f"{OUT_DIR}/df_rfid_daa.csv", encoding="cp932")
    merged_df = pd.merge(df_tana,df, on='scode', how='outer')
    merged_df.to_csv(f"{OUT_DIR}/df_merged.csv", encoding="cp932")
    return merged_df

# 商品マスタから在庫情報とメモを取得し、それらの情報をデータフレームに追加する。
def enrich_with_master_data(df):

    products = get_stock_all()
    if products is not None:
        # 必要なフィールドだけを選択してDataFrameに変換
        product_df = pd.DataFrame([{"scode": p.scode, "master_title": p.pname, "master_qty": p.stock_qty,"master_memo":p.memo} for p in products])

    #print(product_df)
    merged_df = pd.merge(df, product_df, on='scode', how='outer')
    #複数行を一行にする
    merged_df = merged_df.drop_duplicates(subset='scode')

    merged_df['title'].replace('', np.nan, inplace=True)
    merged_df['title'].fillna(merged_df['master_title'], inplace=True)


    merged_df.to_csv(f"{OUT_DIR}/df_enriched.csv", encoding="cp932")
    return merged_df

    df['master_qty'] = 0
    df['master_memo'] = ""
    for idx, row in df.iterrows():
        product = check_stock(row['scode'])
        df.loc[idx, 'master_qty'] = product.stock_qty if product else -999
        df.loc[idx, 'master_memo'] = product.memo if product else ""
        if pd.isna(row['title']) or not row['title']:
            df.loc[idx, 'title'] = product.pname if product else ""
    df.to_csv(f"{OUT_DIR}/df_enriched.csv", encoding="cp932")
    return df

# データフレームから指定された条件に合う行をフィルタリングし、必要な列の前処理を施す。
def filter_and_prepare_for_upload(df):
    df_filtered = filter_and_prepare_df(df)
    df_filtered.to_csv(f"{OUT_DIR}/df_filtered.csv", encoding="cp932")
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
def upload_main(noup=False, mode=None):
    df = get_and_prepare_location_data()
    if df is None:
        return

    df = read_and_merge_rfid_tags(df)
    if df is None:
        return

    df = enrich_with_master_data(df)


    df_to_upload = filter_and_prepare_for_upload(df)

    exit()


    upload_data(df_to_upload, noup,mode)


if __name__ == "__main__":
    # コマンドライン引数の設定
    try:
        parser = argparse.ArgumentParser(description='RFID アップロードスクリプト')
        parser.add_argument('--noup', action='store_true', help='アップロードしない場合にこのフラグを指定')
        parser.add_argument('--mode', choices=['test', 'real'], help='テストモードか実戦モードを指定')

        args = parser.parse_args()
        
        #stock_date_time = get_stock_date() # 棚卸し日を指定する
        upload_main(noup=args.noup,mode=args.mode)

    except SystemExit:
        pass
    
