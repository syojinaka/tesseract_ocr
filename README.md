### Tesseract OCR Program

#### 参考
https://punhundon-lifeshift.com/tesseract_ocr

#### 利用ライブラリ
|ライブラリ名|Version|
|------|----|
|click|7.0|
|flask|1.1.1|
|itsdangerous|1.1.0|  
|jinja2|2.10.3|
|markupsafe|1.1.1|
|numpy|1.17.3|
|opencv-python|4.1.1.26|
|openssl|1.1.1d|
|pdf2image|1.9.0|
|pillow|6.2.1|
|pip|19.3.1|
|pyocr|0.7.2|
|python|3.7.4|
|setuptools|41.4.0|
|sqlite|3.30.0|
|vc|14.1|
|vs2015_runtime|14.16.27012|
|werkzeug|0.16.0|
|wheel|0.33.6|
|wincertstore|0.2|

### 形態素解析
　Mecabの導入
 https://qiita.com/menon/items/f041b7c46543f38f78f7

### フォルダ内のファイル一覧作成
  glob.glob
  https://note.nkmk.me/python-glob-usage/
  
### MeCabにユーザー辞書追加
  https://qiita.com/madaaamj/items/71fbfbf71c9ff56e1987
  https://qiita.com/myaun/items/9f8fee924fdc3f7ef411

### MeCabの文字コード問題
  ユーザー辞書作成を、上記URL記載の情報を基に行った
  登録した単語を含んだ文章をMeCabで形態素解析させると、1つの単語として認識させることはできた。
  ただし、品詞名などが文字化けしてしまい、「名詞」のみを抽出する条件に引っかからなくなってしまった。
  
  原因は下記2つ
  　・システム辞書がUTF-8ではない（こちらだけでは解消されなかった）
    ・ユーザー辞書であるCSVファイルがUTF-8となっていない（これで解決）
　　　　コンパイルはUTF-8と指定して実行していたが、元のファイルがたしかEUC?とかだった 
    
 ### GCPのVisionAPIテスト
 https://qiita.com/se_fy/items/963b295bbd13101c044b

### 進捗バー（できたら・・）
  https://narito.ninja/blog/detail/68/
  
 ### いつかやりたい　Flask＆OpenCV
 https://teratail.com/questions/164621
 
 ### ひらがな・カタカナ変換 ###
 https://pypi.org/project/jaconv/
