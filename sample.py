from PIL import Image
import sys, os, re, glob
from pdf2image import convert_from_path

import pyocr
import pyocr.builders as pb
import mimetypes
import cv2
import numpy as np
import pathlib
import datetime
import MeCab
from collections import Counter
import csv
import fileProperty
import tifffile
import shutil

# Image.MAX_IMAGE_PIXELS = 1000000000

# 変換：：convert from PDF or PNG to numpy.ndarray
def convert_pdfpng2ndarray(path):
    mime = mimetypes.guess_type(path)
    # PDFの場合
    if mime[0] == 'application/pdf':
        images = convert_from_path(path)
        print(type(images[0]))
        # グレースケール化
        gray_scale_image = images[0].convert('L')
        # PIL.Image.Image
        image = np.array(gray_scale_image, dtype=np.uint8)
        print(type(image))
        return image

    # PNG/JPEGファイルの場合
    elif mime[0] == 'image/png' or mime[0] == 'image/jpeg':
        image = cv2.imread(path)
        return image

    # TIFFファイルの場合
    elif mime[0] == 'image/tiff':
        # TIFFファイルをPNGファイルとしてdataフォルダへ格納
        shutil.copy2(target_list[file_num],'data/' + get_fname(path) + '.png')
        # ローカルのPNGファイルをイメージオブジェクトに変換
        image = cv2.imread('data/' + get_fname(path) + '.png')
        print(type(image))
        return image

# 光学認識：：PNG　⇒　TXT
def convert_png2txt(target_img, file_name):
    print('Now recognizing.....')

    txt = tool.image_to_string(
        Image.fromarray(target_img),
        lang = lang,
        builder = pb.TextBuilder(tesseract_layout=6))

    print('Recoginzed!\n')
    return txt


# 光学認識：：PNG（指定領域）　⇒　TXT
def convert_png2txt_fromarray(target_img, area, file_name):
    # 読み取り領域確認用
    # 　PNGファイルとして保存
    # imwrite('result/' + file_name + '.png',target_img[area[1]:area[1]+area[3], area[0]:area[0]+area[2]])
    print('Now recognizing.....')
    txt = tool.image_to_string(
        Image.fromarray(target_img[area[1]:area[1]+area[3], area[0]:area[0]+area[2]]),
        lang = lang,
        builder = pb.TextBuilder(tesseract_layout=7))

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

# 不要な文字/空白を除去
def eliminate_char(txt):
    # 不自然な空白を除去
    txt = re.sub('([あ-んア-ン一-龥ー])\s+((?=[あ-んア-ン一-龥ー]))',r'\1\2', txt)

    # 不要文字を除去して返却
    return eliminate_word(txt)

# 不要文字列の除去
def eliminate_word(text):
    # 文字変換の関数の中でtranslate関数が早いらしい
    table = text.maketrans({
        '|': '', 
        '一': ''
    })
    return text.translate(table)

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
def write_to_text(file_name, text, list):
    print('Writing...')
    with open('result/' + file_name + '.txt',mode='w',encoding='utf-8') as f:

        f.write('******単語抽出*******************************\n')
        f.write("《抽出数＝" + str(len(list)) + '単語》\n')
        for word_count in list:
            f.write(word_count[0] + '::' + str(word_count[1]) + '\n')

        f.write('\n\n')
        f.write('******OCR結果*********************************\n')
        f.write(text)
    print('Completed!')

# OpenCVでは日本語のファイル名が文字化けしてしまう
# 文字化け対策を施したメソッドを新たに作成
def imwrite(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

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
    # imageをネガポジ変換する　認識精度低下したため、ネガポジ変換はしない
    # img = convert_bitwise(img)

    # property情報のdictionary
    property_list = {}

    # ファイル名の取得
    property_list[0] = get_fname(path)
    # フォルダ名の取得
    property_list[1] = get_fdname(path)
    # 拡張子の取得
    property_list[2] = get_ext(path)
    # 作成日時の取得
    property_list[3] = get_ctime(path)
    # 更新日時の取得
    property_list[4] = get_mtime(path)

    # fp = FileProperty(property_list[0], property_list[1], property_list[2], property_list[3], property_list[4])
    # print(fp.get_fname())

    img = np.array([])
    txt = ''
    try:
        # PNGに変換（Tesseractの要件）
        # 元画像をOCRするとエラーになるが、コピーしてきたデータであればエラーにならない
        # OCRの対象はローカルにコピーしてきたファイル
        # img = convert_pdfpng2ndarray('data/' + property_list[0] + '.png')
        # 元画像をイメージ化したい場合
        img = convert_pdfpng2ndarray(path)
    
        # 読み取り対象をPNGとして保存
        imwrite('data/' + property_list[0] + '.png',img)

        # OCRの実行
        if TARGET == False:
            #### 領域指定なし######
            txt = convert_png2txt(img, property_list[0])
        else:
            #### 領域指定######
            txt = convert_png2txt_fromarray(img, area, property_list[0])
        # OCR成功であれば、「OK」を代入
        property_list[5] = 'OK'

    except Exception as e:
        import traceback
        traceback.print_exc()
        property_list[5] = 'NG'
        # ファイル末尾へ追記するため、mode='a'
        with open('ErrorFileList.txt',mode='a', encoding='utf-8') as f:
            f.write('=============================================' + '\n')
            f.write(target_list[file_num] + '\n')
            print(e.args)

    word_list = []
    if property_list[5] == 'OK':
        # テキストの不要な文字を除去
        txt = eliminate_char(txt)

        # 頻出単語を抽出
        word_list = extract_words(txt)
        print(property_list[0])
        print(extract_words(property_list[0]))

    # 読み取ったテキストをTEXTファイルに書き出す
    write_to_text(property_list[0], txt, word_list)

    text_path = 'result/' + property_list[0] + '.txt'
    property_list[6] = text_path

    # 出現単語数
    property_list[7] = str(len(word_list))+'語'

    if len(word_list) > 4:
        for i in range(5):
            property_list[8+i] = word_list[i][0] + '::' + str(word_list[i][1])
    elif len(word_list) > 0:
        for i in range(len(word_list)):
            property_list[8+i] = word_list[i][0] + '::' + str(word_list[i][1])

    # CSV出力
    with open('result.csv', mode='a') as f:
        for i in range(len(property_list)):
            f.write(str(property_list[i]) + ',')
        f.write('\n')

    
#####################＜変更箇所＞##########################

# EXTENTION= 'tiff'
# EXTENTION= 'pdf'
EXTENTION= 'png'
# EXTENTION= 'bmp'
# EXTENTION= 'jpg'

##########################################################

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


# 引数で指定されたパスにあるイメージデータの読み込み
path = sys.argv[1]
# 指定拡張子のデータリストを作成
target_list = glob.glob(path + '/**/*.' + EXTENTION, recursive=True)

# 指定のパス配下にあるファイルをOCR
for file_num in range(len(target_list)):
# for file_num in range(list_len):
    print(str(file_num+1)+'件目実行開始 (全'+ str(len(target_list))+'件中）')

    # 元ファイルをローカルに保存したい場合はコメントアウト解除
    # shutil.copy2(target_list[file_num],'pdf/' + get_fname(target_list[file_num]) + '.pdf')

    # TIFFの場合はdataフォルダにPNGファイルとして保存する
    # shutil.copy2(target_list[file_num],'data/' + get_fname(target_list[file_num]) + '.png')

    # OCR対象となるファイルのパスを表示
    print(target_list[file_num])

    # OCR実行
    run(target_list[file_num])

    print('========================\n')
