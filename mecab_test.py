import MeCab
from collections import Counter
import re

def  extract_words(txt):
    mecab = MeCab.Tagger()
    parse = mecab.parse(txt)
    lines = parse.split('\n')
    items = (re.split('[\t,]', line) for line in lines)

    for item in items:
        print(item)

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



def  extract_words2(txt):
    mecab = MeCab.Tagger()
    parse = mecab.parse(txt)
    lines = parse.split('\n')
    items = (re.split('[\t,]', line) for line in lines)

    return items
            


def mecab_list(text):
    # パーサー設定
    tagger = MeCab.Tagger("-Ochasen")
    node = tagger.parseToNode(text)
    word_class = []
    while node:
        word = node.surface
        wclass = node.feature.split(',')
        if wclass[0] != u'BOS/EOS':
            if wclass[6] == None:
                word_class.append((word,wclass[0],wclass[1],wclass[2],""))
            else:
                word_class.append((word,wclass[0],wclass[1],wclass[2],wclass[6]))
        node = node.next
    return word_class

txt = u'8 の連設計 3 e 795A 号口 RCL 防曇塗装レス品 2018/07/13 (2018/07/13) 1 (ぷぷ'

mecab = MeCab.Tagger()
parse = mecab.parse(txt)
print(parse)

# print(type(parse))

# print(txt)
list = extract_words2(txt)
for item in list:
    print(item[0]+'  '+item[1])

# print(extract_words2(txt))
