import os
import json
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud


# 将所有文件夹名转换为str类型
folder_name = " ".join(os.listdir(r"E:\mzitu"))

# jieba分词
jieba.load_userdict(r"E:\jieba.txt")
seg_list = jieba.lcut(folder_name, cut_all=False)

# 利用字典统计词频
counter = dict()
for seg in seg_list:
    if counter.get(seg) is None:
        counter.update({seg:1})
    else:
        counter.update({seg:counter.get(seg) + 1})

# 根据词频排序字典
counter_sort = sorted(counter.items(), key=lambda value: value[1], reverse=True)

# 解析成json类型并写入文件
words = json.dumps(counter_sort, ensure_ascii=False)
with open(r"E:\words.json", "w+", encoding="utf-8") as f:
    f.write(words)

# 生成词云
wordcloud = WordCloud(font_path=r"e:\Doc\Font\msyh.ttf",
                      max_words=100, height=600, width=1200).generate_from_frequencies(counter)
plt.imshow(wordcloud)
plt.axis('off')
plt.show()
wordcloud.to_file('worldcloud.jpg')
