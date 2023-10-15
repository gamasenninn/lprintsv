from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

BaseSrc = declarative_base()

class Product_tran(BaseSrc):
    __tablename__ = "V_商品_入出庫"

    id = Column(Integer, primary_key=True, index=True, name="ID")
    scode = Column(String, index=True, name="コード")
    pname = Column(String, name="商品名")
    stock_qty = Column(Integer, name="在庫数量")
    stock_price = Column(Integer, name="単価")
    receipt_date = Column(DateTime, name="日付")
    sale_price = Column(Integer, name="販売価格")
    sale_date = Column(DateTime, name="販売日付")
    sale_person = Column(String, name="販売担当者")
    delivery_person = Column(String, name="納品担当者")
    disporsal_date = Column(DateTime, name="廃棄日付")
    disporsal_person = Column(String, name="廃棄担当者")
    memo = Column(String, name="備考")
    sale_class = Column(String, name="販売区分")
    category = Column(String, name="区分")
    in_qty = Column(Integer, name="入庫数量")
    person = Column(String, name="社員名")
    vendor_no = Column(Integer, name="取引先No")
    vendor_name = Column(String, name="取引先名")
    last_update = Column(DateTime,name="_LastUpdate")


class PostingItem(BaseSrc):
    __tablename__ = "出品商品管理票"

    id = Column(Integer, primary_key=True, index=True, name="管理番号")
    scode = Column(String, index=True, name="仕切書No")
    aucid = Column(String, index=True, name="オークションID")
    old_aucid = Column(String, index=True, name="旧オークションID")
