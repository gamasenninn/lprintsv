import gspread
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
import pandas as pd
from tools.find_env import find_dotenv

GOOGLE_SCOPE = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']


def load_spreadsheet(secret_json, spreadsheet_key):
    scope = GOOGLE_SCOPE
    credentials = ServiceAccountCredentials.from_json_keyfile_name(secret_json, scope)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key(spreadsheet_key)
    return workbook

def get_cleaned_dataframe(workbook, worksheet_name):
    worksheet = workbook.worksheet(worksheet_name)
    df = get_as_dataframe(worksheet, evaluate_formulas=True)
    df.dropna(how='all', inplace=True)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df

def remove_duplicates(df, column_name):
    return df.drop_duplicates(subset=column_name, keep='last')

def get_gsp():
    SECRET_JSON = os.environ["SECRET_JSON"]
    SPREADSHEET_KEY = os.environ["SPREADSHEET_KEY"]

    workbook = load_spreadsheet(SECRET_JSON, SPREADSHEET_KEY)
    gs_df_shop = get_cleaned_dataframe(workbook, 'IM店売進捗')
    gs_df_net = get_cleaned_dataframe(workbook, 'IMネット売進捗')

    # gs_df_net から特定のカラムを抽出
    selected_columns_net = ['仕切', '支払い方法', '商談状況', '店長確認']
    gs_df_net_selected = gs_df_net[selected_columns_net]
    gs_df_net_selected = gs_df_net_selected.rename(columns={
        '仕切': 'scode',
        '支払い方法': 'payment',
        '商談状況': 'nego_status',
        '店長確認': 'confirmation'
    })
    gs_df_net_selected['sell_type'] ="ネット売"
    gs_df_net_selected.fillna('',inplace=True)

    # gs_df_shop から特定のカラムを抽出
    selected_columns_shop = ['仕切', '支払', '商談状況', '確認']
    gs_df_shop_selected = gs_df_shop[selected_columns_shop]
    gs_df_shop_selected = gs_df_shop_selected.rename(columns={
        '仕切': 'scode',
        '支払': 'payment',
        '商談状況': 'nego_status',
        '確認': 'confirmation'
    })
    gs_df_shop_selected['sell_type'] ="店売"
    gs_df_shop_selected.fillna('',inplace=True)


    # gs_df_net_selected と gs_df_shop_selected を合体
    combined_df = pd.concat([gs_df_net_selected, gs_df_shop_selected], axis=0)
    #print("//////////統合/////////////")
    #print( combined_df.head())

    unique_gs_df = remove_duplicates(combined_df, 'scode')

    return unique_gs_df

if __name__ == "__main__":

    load_dotenv(find_dotenv())
    df = get_gsp()
    print(df.head())
    df.to_csv("gsp.csv",encoding="utf8")
