import re
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from snownlp import SnowNLP
import numpy as np
import requests
import json

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False
def divide(danmu_list,stop_word):#分词处理
    danmu_str=" ".join(danmu_list)
    danmu_str=re.sub(r'[^\w]+','',danmu_str)
    word_list=jieba.lcut(danmu_str)
    word_list=[word for word in word_list if word not in stop_word and len(word) > 1]
    word_counts={}
    for word in word_list:
        word_counts[word]=word_counts.get(word, 0)+1
    sorted_word_counts=sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    word_list=[item for item in sorted_word_counts if item[1]>5]
    return word_list
def cloud(word_list):#词云图
    wordcloud=WordCloud(background_color="white",font_path="STKAITI.TTF",width=2000,height=1000)
    wordcloud.generate_from_frequencies({word: count for word, count in word_list})
    plt.figure(figsize=(10, 5),dpi=200)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()
    wordcloud.to_file("词云图.png")
def edition(w_list):#nlp分析
    scores=[SnowNLP(w).sentiments for w in w_list]
    data_em=np.array([sum(score >= 0.6 for score in scores),
                       sum(0.4 <= score <= 0.6 for score in scores),
                       sum(score <= 0.4 for score in scores)])
    plt.figure(dpi=300)
    plt.pie(data_em,labels=['positove','neutral','negative'],autopct='%1.1f%%')
    plt.show()
    plt.figure(dpi=300)
    plt.hist(scores,bins=10,edgecolor='black',rwidth=0.9)
    plt.savefig("情感直方图.png")
    plt.xlabel('score')
    plt.ylabel('number')
    plt.grid(axis='y', alpha=0.7)
    plt.savefig("情感饼图.png")
    plt.show()
def danmu(cid):#弹幕获取
    url_oid=f"https://api.bilibili.com/x/v1/dm/list.so?oid={cid}"
    r=requests.get(url_oid)
    xml=r.text
    xml=r.content.decode('utf-8')
    danmu_list=re.findall(r'<d p=".*?">(.*?)</d>',xml)
    return danmu_list
def comment(aid):#评论获取
    comments=[]
    n=0
    try:
        while True:
            headers = {
                'Referer':'https://www.bilibili.com/',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
            }
            comment_url=f"https://api.bilibili.com/x/v2/reply/main?csrf=40a227fcf12c380d7d3c81af2cd8c5e8&mode=3&next={n}&oid={aid}&plat=1&type=1"
            r_comment=requests.get(comment_url,headers=headers)
            html_comment=r_comment.text
            json_comment=json.loads(html_comment)
            replies=json_comment['data']['replies']
            if 'data' not in json_comment or 'replies' not in json_comment['data'] or not json_comment['data']['replies']:
                break
            for reply in replies:
                name=reply['member']['uname']
                message=reply['content']['message']
                level=reply['member']['level_info']['current_level']
                sex=reply['member']['sex']
                comments.append({
                    "用户名":name,
                    "用户等级":level,
                    "性别":sex,
                    "评论":message,
                    })
            n+=1
            if n==200:break
    except Exception:
        pass
    return comments
def sex(comment_sex):
    sex_counts={"男": 0, "女": 0, "保密": 0}
    for sex in comment_sex:
        sex_counts[sex] += 1
    sex_data=np.array(list(sex_counts.values()))
    plt.figure(dpi=300)
    plt.pie(sex_data,labels=list(sex_counts.keys()),autopct='%1.1f%%')
    plt.title('Distribution of Gender')
    plt.savefig("性别饼图.png")
    plt.show()
def level(comment_level):
    level_counts={str(i): 0 for i in range(7)}
    for num in comment_level:
        level_counts[str(num)] += 1
    level_data=np.array(list(level_counts.values()))
    plt.figure(dpi=300)
    plt.pie(level_data,labels=list(level_counts.keys()),autopct='%1.1f%%')
    plt.savefig("等级饼图.png")
    plt.show()
if __name__ == "__main__":
    divide()
    cloud()
    edition()
    danmu()
    comment()
    sex()
    level()
