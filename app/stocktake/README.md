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


# Web APIの呼び出しについて

tana_web_api.pyに定義されている関数を使って、Web APIを呼び出すことができます。

- get_location: 商品コードから位置情報を取得
- get_location_all: 全商品の位置情報を取得  
- upload_locations: 位置情報をアップロード
- upload_in_chunks: データフレームをチャンク分割してアップロード

## 位置情報の取得

```python
from tana_web_api import get_location

data = get_location(商品コード)
```

## 位置情報の一括取得

```python 
from tana_web_api import get_location_all

df = get_location_all()
```

## 位置情報のアップロード

```python
from tana_web_api import upload_in_chunks

upload_in_chunks(データフレーム, mode="test") 
```

modeには"test"か"real"を指定。

## その他

実際のAPIの定義に合わせて、認証方法やエンドポイントを設定する必要があります。

.envファイルにAPIキー等を設定して利用することを想定しています。

了解しました。README.mdに近傍検索のロジックを以下のように追記しました。

# 近傍検索

rfid_bar_tool.pyには、RFIDタグの読み取りデータから近傍の位置タグを検索する機能があります。

これは棚卸し時に、読み取ったRFIDとその近くの位置タグから商品の置き場所を推定するために使用します。

## ロジック

1. RFIDタグファイルを読み込む
2. データの中から"9999"で始まる位置タグを検索
3. 各RFIDタグに対して、一番近い位置タグを探す
4. 順方向と逆方向の検索結果をマージする 
5. マージした結果を元のデータ順に並べ替える

これにより、各RFIDタグに最も近い位置タグの組み合わせが出力されます。

主な関数:

- find_closest_9999_codes : 近傍検索を行う
- merge_forward_and_reverse_results : 順逆の結果をマージ
- order_by_original_data : 元の順序で並べ替え

この機能を利用することで、RFIDと位置タグの紐づけが容易になります。