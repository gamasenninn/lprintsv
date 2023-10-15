#
#　RFIDとバーコードのコードが一致しているかをチェックする
#　データがきちんと書かれているかどうか
#

#
#　バーコード読み取りデータで棚卸しデータを作成する
#
#
import pandas as pd
from tools.rfid_bar_tool import check_posting_item_by_aucid,check_stock
from tools.rfid_bar_tool import read_bar_file
from tools.tana_web_api import upload_data
import re

GO_DIR = 'convert/check/tana_data'

class FormatError(Exception):
    pass

def parse_filetag(filetag):
    # 正規表現を使用して年月日、時間、および店舗情報を抽出
    match = re.match(r'ReadBarcode(\d{8})_(\d{6})_(.+)', filetag)
    if match:
        date_str, time_str, location = match.groups()
        # 日付と時間を指定されたフォーマットで整形し、連結
        formatted_datetime = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:]}"
        return formatted_datetime, location
    else:
        print(f"Failed to parse filetag: {filetag}")
        return None

def enrich_with_master_data(df):
    df['title'] = ""
    df['master_qty'] = 0
    df['master_memo'] = ""
    for idx, row in df.iterrows():
        product = check_stock(row['bar_scode'])
        df.loc[idx, 'master_qty'] = product.stock_qty if product else -999
        df.loc[idx, 'master_memo'] = product.memo if product else ""
        if pd.isna(row['title']) or not row['title']:
            df.loc[idx, 'title'] = product.pname if product else ""
    return df

# 文字列のクレンジング関数
def clean_string(s):
    if isinstance(s, str):
        t = s.replace('\u3000', ' ')
        t = t.replace("'","\\'")
    return t

# 対象日付データをdatetime型に一括変換し、棚卸し日より前のデータをフィルタリング
# ※棚卸日以降のデータは誰かが入力したものなので、そちらを優先するためである
def filter_and_prepare_df(df_new):
 
    #データの正規化
    #df_new['create_date'] = pd.to_datetime(df_new['create_date'])
    #df_new['old_create_date'] = pd.to_datetime(df_new['old_create_date'])
    #df_new['product_qty'].fillna(0, inplace=True)
    df_new['master_qty'].fillna(0, inplace=True)
    
    # 棚卸し日より前のデータと、場所があるもの、在庫があるものをフィルタリング
    #filtered_df = df_new.loc[
    #    (df_new['old_create_date'] < df_new['create_date']) & 
    #    df_new['place'].notna() & 
    #    (df_new['master_qty'].astype(int) >= 0)
    #].copy()  # この時点で明示的にコピーを作成

    filtered_df = df_new.copy()
    # 前処理を行う
    filtered_df['place'].fillna('', inplace=True)
    filtered_df.loc[:, 'title'] = filtered_df['title'].apply(clean_string)
    # 新しいcreate_dateとcategoryを設定
    #filtered_df['create_date'] = stock_date_time
    #filtered_df['create_date'] = filtered_df['create_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    #filtered_df['old_create_date'] = filtered_df['old_create_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    #filtered_df['category'] = "rfid"
    filtered_df['scode'] = filtered_df['bar_scode']
    filtered_df['memo'] = filtered_df['master_memo']
    
    # 必要なカラムだけを選択する。
    return filtered_df[['scode','title','place','category','memo','create_date']]


if __name__ == "__main__":

    bar_df = pd.DataFrame(columns=['bar_scode'])
    for filetag,items in read_bar_file(f'{GO_DIR}/ReadBarcode*.txt'):
        result = parse_filetag(filetag)
        if result:
            date_time,location = result
        else:
            raise FormatError("format error")
            
        #print(f"scode: {filetag}/{items[0]}....{date_time}/{location}")
        any_code = items[0]
        if "?skey=" in any_code:
            scode = any_code.split("?skey=")[1] 
        elif "auction/" in items[0]:
            aucid = any_code.split("/auction/")[1]
            postingItem = check_posting_item_by_aucid(aucid)
            if postingItem:
                print(f"出品カードからscodeを抽出した。{postingItem.aucid}..{postingItem.scode}")          
                scode = postingItem.scode
            else:
                print(f"出品カードからscodeを抽出したが存在しません。{aucid}")          
                scode = ''

        else:
            scode = items[0]

        new_row = {'bar_scode': scode,'place':location,'category':'bar_qr','create_date':date_time}
        bar_df = bar_df.append(new_row, ignore_index=True)


    #複数行を一行に絞る
    bar_df = bar_df.drop_duplicates(subset='bar_scode')

    #タイトルなどを付加する
    enrich_df = enrich_with_master_data(bar_df)
    enrich_df.to_csv(f'{GO_DIR}/tana.csv', index=False)
    #print(enrich_df)

    #ペイロードを作成する
    payload_df = filter_and_prepare_df(enrich_df)
    print(payload_df)
    payload_df.to_csv(f'{GO_DIR}/tana_payload.csv', index=False)
 
    upload_data(payload_df, mode="test", noup=True)
