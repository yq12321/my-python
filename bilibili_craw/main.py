import tkinter as tk
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import ku
from tkinter import messagebox

def analyze_video():
    bvid=entry.get()
    result=basic(bvid)
    text=''
    try:
        for key, value in result.items():
            text += f"{key}:{value}\n"
    except Exception:
        text="bvid错误"
    text_output.config(state=tk.NORMAL)
    text_output.delete(1.0,tk.END)
    text_output.insert(tk.END,text)
    text_output.config(state=tk.DISABLED)
    if 'aid' in result and 'cid' in result:
        create_buttons(result['aid'],result['cid'])
def create_buttons(aid, cid):
    danmu_button=tk.Button(root,text="分析弹幕",command=lambda:danmu(cid))
    danmu_button.grid(row=3,column=0,pady=10)
    comment_button=tk.Button(root,text="分析评论",command=lambda:comments(aid))
    comment_button.grid(row=3,column=1,pady=10)
def basic(bvid):
    headers = {
        'Referer':'https://www.bilibili.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
    }
    url=f"https://www.bilibili.com/video/{bvid}"
    r=requests.get(url,headers=headers)
    html=r.text
    soup=BeautifulSoup(html,'html.parser')
    try:
        title=soup.find('h1',class_="video-title").get_text().strip()
        vide_time=soup.find("div",class_="video-info-detail-list").find("span",class_="pubdate-ip item").get_text().strip()
        data_tag=soup.find('meta', {'name': 'description'})
        data=data_tag.get('content')
        url_bvid=f"https://www.bilibili.com/video/{bvid}"
        r1=requests.get(url_bvid, headers=headers)
        html=r1.text
        cid_match=re.search(r'"cid":(\d+)',html)
        cid=cid_match.group(1)
        aid_match=re.search(r'"aid":(\d+)',html)
        aid=aid_match.group(1).strip()
        view_counts=re.search(r'视频播放量 (\d+)',data)
        danmu_num=re.search(r'弹幕量 (\d+)',data)
        like_number=re.search(r'点赞数 (\d+)',data)
        coin_number=re.search(r'投硬币枚数 (\d+)',data)
        collect_number=re.search(r'收藏人数 (\d+)',data)
        transpond_number=re.search(r'转发人数 (\d+)',data)
        text={
        "标题":title,
        "播放量":view_counts.group(1),
        "弹幕数":danmu_num.group(1),
        "视频发布时间:":vide_time,
        "点赞数":like_number.group(1),
        "投币数":coin_number.group(1),
        "收藏数":collect_number.group(1),
        "转发数":transpond_number.group(1),
        "aid":aid,
        "cid":cid
        }
        return text
    except Exception:
        pass
def danmu(cid):
    danmu_list=ku.danmu(cid)
    danmu_number=0
    for danmu in danmu_list:
        danmu_number+=1
    stop_words_path=r"stop_words.txt"
    with open(stop_words_path,"r",encoding="utf-8") as file:
         stop_word=[line.strip() for line in file]
    df=pd.DataFrame(danmu_list)
    df.to_excel("弹幕.xlsx")
    word_list=ku.divide(danmu_list,stop_word)
    ku.cloud(word_list)
    ku.edition(danmu_list)
    print("over")
    messagebox.showinfo("", f'弹幕数量:{danmu_number}')
def comments(aid):
    comments=ku.comment(aid)
    try:
        df_comment=pd.DataFrame(comments)
        df_comment.to_excel("评论.xlsx")
    except Exception:
        print("错误")
        pass
    comment_item=[comment["评论"] for comment in comments]
    comment_sex=[comment["性别"] for comment in comments]
    comment_level=[comment["用户等级"] for comment in comments]
    comment_num=len(comments)
    stop_words_path=r"stop_words.txt"
    with open(stop_words_path, "r", encoding="utf-8") as file:
         stop_word=[line.strip() for line in file]
    comment_list=ku.divide(comment_item,stop_word)
    ku.cloud(comment_list)
    ku.edition(comment_item)
    ku.sex(comment_sex)
    ku.level(comment_level)
    try:
        df_comment=pd.DataFrame(comments)
        df_comment.to_excel("评论.xlsx")
    except Exception:
        pass
    print("over")
    messagebox.showinfo("", f'评论数量:{comment_num}')
    text = "分析评论"
    print(text)
# 创建主窗口
root=tk.Tk()
root.title("B站视频分析")
root.iconbitmap('b.ico')
# 创建输入框
entry_label=tk.Label(root,text="请输入bvid:",font=(16))
entry_label.grid(row=0,column=0,pady=10)
entry=tk.Entry(root)
entry.grid(row=0,column=1,pady=10)
# 创建按钮
button=tk.Button(root,text="确认",font=10,command=analyze_video)
button.grid(row=1,column=0,pady=10)
exit_button=tk.Button(root,text="退出",font=10,command=root.destroy)
exit_button.grid(row=1,column=1,pady=10)
# 创建 Label 用于显示输入的文字
text_output=tk.Text(root,height=10,width=50,state=tk.DISABLED)
text_output.grid(row=2,column=0,columnspan=2,pady=10)
# 启动主循环
root.mainloop()