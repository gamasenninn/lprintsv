## keep-aliveを有効にするには
MainLayout.vueに次のようにする
```
    <q-page-container>
        <router-view v-slot="{Component}">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </router-view>
    </q-page-container>
```
ただし、この方法だとすべてのコンポーネントが対象になってしまうため  
keep-aliveを有効したいものだけを指定する方法がよいと思われる。
- - -
## .envを有効にするには  

@quasar/appと@quasar/dotenvをインストールする  
環境変数を設定、変更した場合かならずサーバーを再起動すること  
参照する場合は、process.env.<環境変数名>を使う。  
  
const YOUR_API_KEY = process.env.API_KEY
- - -  
## q-tableでのネストされたオブジェクトのフィールド指定
ネストされたオブジェクトをq-tableのフィールドに設定する場合、  
ファンクションの戻り値を返す形にする  
シングルクォートで包みこんではいけない  
```
    columns=[
        {name: 'person',label:'担当' ,field:'person'},
        {name: 'ownwer',label:'発行者' ,field: row=>row.owner.name},
    ]
```
- - -