from PIL import Image
import sys, os, re, glob
from pdf2image import convert_from_path

import pyocr
import pyocr.builders as pb
import sample


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
    sample.run(target_list[file_num])

    print('========================\n')
