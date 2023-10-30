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

######
# 近傍位置情報検索
######
def find_closest_9999_codes(code_data, reverse=False):
    closest_codes_dict = {}
    last_9999_code = None
    special_9999_code = None

    iter_data = list(reversed(code_data)) if reverse else list(code_data)
    
    for code in iter_data:
        if code.startswith("9999"):
            special_9999_code = code
            break
        # 9999で始まるコードが見つからなかったら、空の辞書を返す
    if special_9999_code is None:
        return {}
    
    for code in iter_data:
        if code.startswith("9999"):
            last_9999_code = code
        else:
            closest_codes_dict[code] = last_9999_code if last_9999_code else special_9999_code
                
    return closest_codes_dict

# マージのロジック
def merge_forward_and_reverse_results(forward_result, reverse_result):
    return {key: (forward_result.get(key, None), reverse_result.get(key, None)) for key in set(forward_result) | set(reverse_result)}


# 元のテストデータの並び順に整える
def order_by_original_data(merged_result, original_data):
    return {key: merged_result[key] for key in original_data if key in merged_result}

def group_place(code_data):
    # 順読みの結果を取得
    forward_result = find_closest_9999_codes(code_data)
    if not forward_result:
        return {}

    # 逆読みの結果を取得
    reverse_result = find_closest_9999_codes(code_data,reverse=True)

    # 順読みと逆読みの結果をマージ
    merged_result = merge_forward_and_reverse_results(forward_result, reverse_result)

    return  merge_dicts(merged_result,{})

# Function to merge two dictionaries with tuple values

def merge_dicts(dict1, dict2):
    merged_dict = dict1.copy()
    for key, value in dict2.items():
        merged_dict[key] = tuple(set(merged_dict.get(key, ())) | set(value))
    return merged_dict

# 辞書内のデータをソートしてタプルに変換、かつ重複を取り除く
def normalize_dict_values_to_tuples(d):
    return {k: tuple(sorted(set(v))) if isinstance(v, (set, list, tuple)) else (v,) for k, v in d.items()}

def read_rfid_make_group_dict(pattern):
    filenames = glob.glob(pattern)
    merged_dict = {}
    for file_path in filenames:
        scode_list = []
        with open(file_path, 'r') as f:
            for line in f:
                scode = convert_line(line.strip())
                if scode:
                    #print(f"読み込みしました....{scode}")
                    scode_list.append(scode)

        scode_dict = group_place(scode_list)
        if scode_dict:
            merged_dict = merge_dicts(merged_dict,scode_dict)
    return normalize_dict_values_to_tuples(merged_dict)
    #return merged_dict

# キーに対応する値を空白で区切って返す関数
def get_values_as_string(key, dictionary):
    values_tuple = dictionary.get(key, ())
    return " ".join(values_tuple)

#コードをHEX文字列に変換
def convert_to_file_data_hex(test_data):
    file_data = []
    for item in test_data:
        converted_item = ''.join([format(ord(char), 'x') for char in item])
        file_data.append(converted_item)
    return file_data
