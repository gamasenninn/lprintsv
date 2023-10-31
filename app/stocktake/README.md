はい、README.mdの内容をより詳細に描き直しました。

# 概要

Pythonスクリプトのセット。RFIDタグやバーコードの読み取りデータを処理し、商品在庫データとしてWeb APIにアップロードする。

## スクリプト一覧

- `rfid_bar_tool.py` : RFIDタグ/バーコードデータの入力/処理用汎用関数
  - データ読み込み、変換、近傍検索などの機能を提供
- `ck_rfid_bar.py` : RFIDタグとバーコードデータの整合性チェック
  - 読み取りデータの整合性を確認する
- `make_barcode_file.py` : 手動バーコードデータをReadBarcode形式に変換 
  - 手動で読み取ったデータを処理しやすい形式に変換
- `make_upload_tana_data.py` : バーコードデータから棚卸しアップロードデータ作成
  - 棚卸しアップロード用のCSVデータを生成する
- `test_tools.py` : `rfid_bar_tool.py`の関数テスト
  - ユニットテストコード
- `upload_web_scode.py` : RFIDタグデータを読み込み、Web APIへアップロード
  - メインのアップロードスクリプト

# 使い方

## データ整合性確認

`ck_rfid_bar.py` を実行し、RFIDタグとバーコードデータの整合性を確認。

```
python ck_rfid_bar.py
```

## バーコードデータの変換

`make_barcode_file.py` で手動読み取りデータをReadBarcode形式に変換。

```
python make_barcode_file.py
```

## 棚卸しアップロードデータ作成

`make_upload_tana_data.py` でバーコードデータからアップロードデータをCSV形式で作成。

``` 
python make_upload_tana_data.py
```

## RFIDタグデータのアップロード

`upload_web_scode.py` でRFIDタグデータを読み込み、Web APIにアップロード。

```
python upload_web_scode.py
```

--noupオプションでアップロードをスキップし、CSVのみ出力。

# Web API関数

`tana_web_api.py`にAPI呼び出し用の関数が定義されている。

- 商品コードから位置情報取得
- 位置情報の一括取得
- 位置情報のアップロード 
- データフレームのチャンクアップロード

などを行うことができる。

## 認証設定

実際のAPIの認証設定に合わせ`.env`ファイルで設定する。

# 近傍検索機能

`rfid_bar_tool.py`には以下の機能がある。

- RFIDタグファイルから近傍の位置タグを検索
- 商品の置き場所を推定

### 処理手順

1. RFIDタグファイルの読み込み
2. 位置タグの検索
3. 最近傍の位置タグ検索
4. 順方向/逆方向検索結果のマージ
5. マージ結果のソート

### 主要関数 

- `find_closest_9999_codes` : 近傍検索
- `merge_forward_and_reverse_results` : マージ
- `order_by_original_data` : ソート

この機能により、RFIDタグと位置タグの紐づけが容易になる。