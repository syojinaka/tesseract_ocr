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
    cv2.imwrite(file_name + '.png',target_img)
    print('now recognizing.....')

    txt = tool.image_to_string(
        Image.fromarray(target_img),
        lang = lang,
        builder = pyocr.builders.TextBuilder(tesseract_layout=6))
    return txt


# 光学認識：：PNG（指定領域）　⇒　TXT
def convert_png2txt_fromarray(target_img, area, file_name):
    # 読み取り領域確認用
    # 　PNGファイルとして保存
    cv2.imwrite(file_name + '.png',target_img[area[1]:area[1]+area[3], area[0]:area[0]+area[2]])
    print('now recognizing.....')

    txt = tool.image_to_string(
        Image.fromarray(target_img[area[1]:area[1]+area[3], area[0]:area[0]+area[2]]),
        lang = lang,
        builder = pyocr.builders.TextBuilder(tesseract_layout=7))
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

# 引数で指定されたパスにあるイメージデータの読み込み
path = sys.argv[1]
# ファイル名を取得
list = path.split('/')
list = list[1].split('.')
file_name = list[0]
# PDFであればPNGに変換
img = convert_pdfpng2ndarray(path)
# imageをネガポジ変換する　認識精度低下したため、ネガポジ変換はしない
# img = convert_bitwise(img)

# OCR
if TARGET == False:
    #### 領域指定なし######
    txt = convert_png2txt(img, file_name)
else:
    #### 領域指定######
    txt = convert_png2txt_fromarray(img, area, file_name)

# 不要なスペースを削除
txt = delete_space(txt)

# 読み取ったテキストをTEXTファイルに書き出す
with open(file_name + '.txt',mode='w',encoding='utf-8') as f:
    f.write(txt)

# 読み取ったテキストをコマンドラインに表示
print(txt)

