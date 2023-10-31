これらのPythonスクリプトは、RFIDタグやバーコードの読み取りデータを処理し、商品の在庫データとしてWeb APIにアップロードするためのツール群です。

# 概要

- rfid_bar_tool.py: RFIDタグとバーコードのデータを読み込み、処理するための汎用的な関数群
- ck_rfid_bar.py: RFIDタグとバーコードの読み取りデータの整合性をチェックする
- make_barcode_file.py: 手動で読み取ったバーコードデータをReadBarcode形式のファイルに変換する
- make_upload_tana_data.py: バーコード読み取りデータから棚卸しアップロードデータを作成する
- test_tools.py: rfid_bar_tool.pyの関数のユニットテスト
- upload_web_scode.py: RFIDタグデータを読み込み、在庫データとしてWeb APIにアップロードするメインスクリプト

# 使い方

## RFIDタグとバーコードデータのチェック

ck_rfid_bar.pyを実行すると、RFIDタグとバーコードの読み取りデータを読み込み、商品コードの整合性をチェックします。

```
python ck_rfid_bar.py
```

異なるデータがある場合は警告が出力されるので、札の紛失や読み取りミスがないかを確認してください。

## バーコードデータの変換

手動で読み取ったバーコードのテキストデータを、ReadBarcodeフォーマットのファイルに変換します。

```
python make_barcode_file.py
```

## 棚卸しアップロードデータの作成

バーコードの読み取りデータから、棚卸しアップロード用のCSVデータを作成します。

```
python make_upload_tana_data.py
```

## RFIDタグデータのアップロード

upload_web_scode.pyを実行すると、RFIDタグデータを読み込み、商品マスタデータと結合した後、在庫データとしてWeb APIにアップロードします。

```
python upload_web_scode.py
```

--noupオプションをつけるとアップロード処理はスキップされ、CSVだけが出力されます。

# 備考

- マスタデータやWeb APIの定義は実際に合わせてカスタマイズが必要です。
- ログを取ることを推奨します。