from PIL import Image
import sys
from pdf2image import convert_from_path

import pyocr
import pyocr.builders
import sys
import re
import mimetypes
import cv2
import numpy as np
import os
import pathlib
import datetime
import MeCab
from collections import Counter
import glob

# 変換：：convert from PDF or PNG to numpy.ndarray
def convert_pdfpng2ndarray(path):
    mime = mimetypes.guess_type(path)
    # PDFだった場合はPNGに変換する
    if mime[0] == 'application/pdf':
        images = convert_from_path(path)
        # グレースケール
        gray_scale_image = images[0].convert('L')
        # type of gray_scale_image is "PIL.Image.Image"
        image = np.array(gray_scale_image, dtype=np.uint8)

    elif mime[0] == 'image/png':
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        
    return image

# 光学認識：：PNG　⇒　TXT
def convert_png2txt(target_img, file_name):
    # 読み取り対象をPNGとして保存
    cv2.imwrite('result/' + file_name + '.png',target_img)
    print('Now recognizing.....')

    txt = tool.image_to_string(
        Image.fromarray(target_img),
        lang = lang,
        builder = pyocr.builders.TextBuilder(tesseract_layout=6))
    print('Recoginzed!\n')
    return txt


# 光学認識：：PNG（指定領域）　⇒　TXT
def convert_png2txt_fromarray(target_img, area, file_name):
    # 読み取り領域確認用
    # 　PNGファイルとして保存
    cv2.imwrite('result/' + file_name + '.png',target_img[area[1]:area[1]+area[3], area[0]:area[0]+area[2]])
    print('Now recognizing.....')

    txt = tool.image_to_string(
        Image.fromarray(target_img[area[1]:area[1]+area[3], area[0]:area[0]+area[2]]),
        lang = lang,
        builder = pyocr.builders.TextBuilder(tesseract_layout=7))

    print('Recoginzed!\n')
    return txt

# グレースケール化メソッド
def convert_grayscale(img):
    gray_img = img.convert('L')
    return gray_img

# imageをネガポジ変換
def convert_bitwise(img):
    img = cv2.bitwise_not(img)
    return img

# 不自然な空白を除去
# 日本語だけの場合は下記コメントアウト解除
def delete_space(txt):
    txt = re.sub('([あ-んア-ン一-龥ー])\s+((?=[あ-んア-ン一-龥ー]))',r'\1\2', txt)
    return txt

# 拡張子を除去したファイル名を返却
def eliminate_ext(name):
    name = name.split('.')[0] 
    return name

# 作成日時の取得
def get_ctime(path):
    p = pathlib.Path(path)
    ctime = datetime.datetime.fromtimestamp(p.stat().st_ctime)
    create_time = ctime.strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}').format(*'年月日時分')
    return create_time

# 更新日時の取得
def get_mtime(path):
    # pathlib.Pathオブジェクトに変換
    p = pathlib.Path(path)
    # 日付文字列に変換
    ctime = datetime.datetime.fromtimestamp(p.stat().st_mtime)
    update_time = ctime.strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}').format(*'年月日時分')
    return update_time

# ファイル名の取得
def get_fname(path):
    # ファイル名取得
    f_name = os.path.basename(path)
    # 拡張子を除去して返却
    return eliminate_ext(f_name)

# フォルダ名の取得
# ファイルが配置されているフォルダの名前を取得
def get_fdname(path):
    # フォルダ名の取得
    dir_name = os.path.dirname(path)
    return dir_name

# 拡張子の取得
def get_ext(path):
    extention = os.path.splitext(path)
    return extention[1][1:]

# 頻出単語の抽出
def  extract_words(txt):
    mecab = MeCab.Tagger()
    parse = mecab.parse(txt)
    lines = parse.split('\n')
    items = (re.split('[\t,]', line) for line in lines)

    # 名詞をリストに格納
    words = [item[0]
         for item in items
         if (item[0] not in ('EOS', '', 't', 'ー') and
             item[1] == '名詞' and item[2] == '一般')]

    # 頻度順に出力
    counter = Counter(words)
    list = []
    for word, count in counter.most_common():
        list.append([word,count])
    return list

# OCRの結果をテキストに書き出し
def write_to_text(text, file_name, folder_name, extention, create_date, update_date, list):
    print('Writing...')
    with open('result/' + file_name + '.txt',mode='w',encoding='utf-8') as f:
        f.write('******Property情報****************************\n')
        f.write('  ファイル名 : ' + file_name + '\n')
        f.write('  フォルダ名 : ' + folder_name + '\n')
        f.write('  拡張子     : ' + extention + '\n')
        f.write('  作成日時   : ' + create_date + '\n')
        f.write('  更新日時   : ' + update_date + '\n')
        f.write('\n\n')

        f.write('******単語抽出*******************************\n')
        f.write("《抽出数＝" + str(len(list)) + '単語》\n')
        for word_count in list:
            f.write(word_count[0] + '::' + str(word_count[1]) + '\n')

        f.write('\n\n')
        f.write('******OCR結果*********************************\n')
        f.write(text)
    print('Completed!')



# 1ファイルのOCR実行
def run(path):
    #####################＜変更箇所＞##########################
    # 領域指定か否か
    # 領域を指定してOCRする場合はTrueとする
    TARGET = False

    # 領域を指定する場合の変数
    area = np.array([])
    # 配光成績書
    # area = np.array([580,40,380,80])
    # マーキング整合確認書
    # area = np.array([100,60,550,120])
    # area = np.array([190,220,260,37])

    ##########################################################

    # PNGに変換（Tesseractの要件）
    img = convert_pdfpng2ndarray(path)
    # imageをネガポジ変換する　認識精度低下したため、ネガポジ変換はしない
    # img = convert_bitwise(img)

    # ファイル名の取得
    file_name = get_fname(path)
    print(file_name)
    # フォルダ名の取得
    folder_name = get_fdname(path)
    # 拡張子の取得
    extention = get_ext(path)
    # 作成日時の取得
    create_date = get_ctime(path)
    # 更新日時の取得
    update_date = get_mtime(path)

    # OCRの実行
    if TARGET == False:
        #### 領域指定なし######
        txt = convert_png2txt(img, file_name)
    else:
        #### 領域指定######
        txt = convert_png2txt_fromarray(img, area, file_name)

    # 文章中の不要なスペースを削除
    txt = delete_space(txt)

    # 頻出単語を抽出
    word_list = extract_words(txt)

    # 読み取ったテキストをTEXTファイルに書き出す
    write_to_text(txt, file_name, folder_name, extention, create_date, update_date, word_list)




print('＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝')
tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]
print("Will use tool '%s'" % (tool.get_name()))
# Ex: Will use tool 'libtesseract'
langs = tool.get_available_languages()
print("Available languages: %s" % ", ".join(langs))
lang = langs[2]
print("Will use lang '%s'" % (lang))
print('＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝')


# #####################＜変更箇所＞##########################
# # 領域指定か否か
# # 領域を指定してOCRする場合はTrueとする
# TARGET = False

# # 領域を指定する場合の変数
# area = np.array([])
# # 配光成績書
# # area = np.array([580,40,380,80])
# # マーキング整合確認書
# # area = np.array([100,60,550,120])
# # area = np.array([190,220,260,37])

# ##########################################################

# 引数で指定されたパスにあるイメージデータの読み込み
path = sys.argv[1]
target_list = glob.glob(path+ '/**/*.pdf', recursive=True)

# 指定のパス配下にあるファイルをOCR
for file_num in range(len(target_list)):
    print(str(file_num+1)+'件目実行開始 (全'+ str(len(target_list))+'件中）')
    try:
        run(target_list[file_num])          
    except :
        print(target_list[file_num])

# # PNGに変換（Tesseractの要件）
# img = convert_pdfpng2ndarray(path)
# # imageをネガポジ変換する　認識精度低下したため、ネガポジ変換はしない
# # img = convert_bitwise(img)

# # ファイル名の取得
# file_name = get_fname(path)
# # フォルダ名の取得
# folder_name = get_fdname(path)
# # 拡張子の取得
# extention = get_ext(path)
# # 作成日時の取得
# create_date = get_ctime(path)
# # 更新日時の取得
# update_date = get_mtime(path)

# # OCRの実行
# if TARGET == False:
#     #### 領域指定なし######
#     txt = convert_png2txt(img, file_name)
# else:
#     #### 領域指定######
#     txt = convert_png2txt_fromarray(img, area, file_name)

# # 不要なスペースを削除
# txt = delete_space(txt)

# # 頻出単語を抽出
# list = extract_words(txt)

# # 読み取ったテキストをTEXTファイルに書き出す
# write_to_text(txt, file_name, folder_name, extention, create_date, update_date, list)


# 読み取ったテキストをコマンドラインに表示
# print(txt)

