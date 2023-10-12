#
#　RFIDとバーコードのコードが一致しているかをチェックする
#　データがきちんと書かれているかどうか
#

#
#　バーコード読み取りデータで棚卸しデータを作成する
#
#
import pandas as pd
from ck_rfid_bar_tool import check_posting_item_by_aucid,check_stock
from ck_rfid_bar_tool import read_bar_file,read_rfid_file
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

        new_row = {'bar_scode': scode,'place':location,'create_date':date_time}
        bar_df = bar_df.append(new_row, ignore_index=True)
    print(bar_df)
