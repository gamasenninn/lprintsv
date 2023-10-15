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
import re

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


if __name__ == "__main__":

    bar_df = pd.DataFrame(columns=['bar_scode'])
    for filetag,items in read_bar_file('convert/check/tana_data/ReadBarcode*.txt'):
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
            print(f"出品カードからscodeを抽出した。{postingItem.aucid}..{postingItem.scode}")
            scode = postingItem.scode
        else:
            scode = items[0]

        new_row = {'bar_scode': scode,'place':location,'category':'bar_qr','create_date':date_time}
        bar_df = bar_df.append(new_row, ignore_index=True)


    #複数行を一行に絞る
    bar_df = bar_df.drop_duplicates(subset='bar_scode')

    #タイトルなどを付加する
    enrich_df = enrich_with_master_data(bar_df)


    enrich_df.to_csv('convert/check/tana_data/tana.csv', index=False)
    print(enrich_df)
