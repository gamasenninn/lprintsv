#
#　RFIDとバーコードのコードが一致しているかをチェックする
#　データがきちんと書かれているかどうか
#
#
#
import pandas as pd
from tools.rfid_bar_tool import check_posting_item_by_aucid,check_stock
from tools.rfid_bar_tool import read_bar_file,read_rfid_file


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
            aucid = any_code.split("/auction/")[1]
            postingItem = check_posting_item_by_aucid(aucid)
            print(f"出品カードからscodeを抽出した。{postingItem.aucid}..{postingItem.scode}")
            scode = postingItem.scode
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
        if product is None:
            print(f"None product scode {scode}")
        else:
            print(f"product_qty: {scode}...{product.stock_qty}")

    # bar_dfに新しい列 'stock_info' を追加し、check_stockの結果を格納
    bar_df['stock_info'] = bar_df['bar_scode'].apply(check_stock)

    # 在庫数量が0の行を抽出
    out_of_stock_df = bar_df[bar_df['stock_info'].apply(lambda x: x is not None and x.stock_qty == 0)]

    # 結果を表示
    print("Out of Stock Items:")
    print(out_of_stock_df)

    #札を新規に発行し、使えるべきもの（バーコードはあるがrfidが存在しないもの＝書き込みミス）
    print("\n札を新規に発行し、付け替えるべきリスト:")

    # right_only_dfに新しい列 'stock_info' を追加し、check_stockの結果を格納
    #right_only_df['stock_info'] = right_only_df['bar_scode'].apply(check_stock)
    right_only_df = right_only_df.copy()
    right_only_df.loc[:, 'stock_info'] = right_only_df['bar_scode'].apply(check_stock)

    # stock_info からタイトル (pname) を取得して新しい列 'title' を作成
    right_only_df.loc[:, 'title'] = right_only_df['stock_info'].apply(lambda x: x.pname if x is not None else 'Unknown')
    right_only_df.loc[:, 'stock_qty'] = right_only_df['stock_info'].apply(lambda x: x.stock_qty if x is not None else None)

    # タイトルとscodeを両方表示
    unique_df = right_only_df.drop_duplicates(subset='bar_scode', keep='first') #ダブったbar_scodeは一行にする
    print(unique_df[['bar_scode','title','stock_qty']])
