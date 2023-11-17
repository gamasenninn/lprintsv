#
#   棚卸し関連のWeb API
#
#
#
import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import json
import pandas as pd

load_dotenv('.env')

DEBUG=bool(int(os.environ['LOCATION_DEBUG']))
UPSERT=True

# API呼び出し
def request_to_web_api(url, method="GET", payload=None):
    auth = HTTPBasicAuth(
        os.environ['LOCATION_WEB_ID'], 
        os.environ['LOCATION_WEB_PASSWORD']
    )
    
    headers = {'Content-Type': 'application/json'} if payload else {}
    
    try:
        response = requests.request(
            method,
            url,
            data=json.dumps(payload) if payload else None,
            headers=headers,
            auth=auth
        )
        return response.json()
    except requests.exceptions.JSONDecodeError as e:
        # JSONデコードエラーが発生した場合、生のレスポンスデータを出力
        print("JSON decode error: ", e)
        print("payload response data: ", payload)
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

# データフレームの長さ（行数）を出力し、アップロードするかどうかを選択する。選択された場合はアップロードを実行。
def upload_data(df, noup,mode):
    print("対象追加数: ", len(df))
    if not noup:
        upload_in_chunks(df, mode=mode, start_index=0, chunk_size=50)
        print("アップロード終了しました。")
    else:
        print("--noupのため、アップロードはスキップされました。")



if __name__ == "__main__":
    # コマンドライン引数の設定
    
    pass