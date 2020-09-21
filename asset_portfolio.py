##### 注意事項 #####
#2020年9月現在、SBI証券はスクレイピングを禁止されておりませんが、今後禁止される可能性もありますので利用時はご注意ください。


#============================================#
#         事前準備
#============================================#

##### ライブラリの読み込み,必要な変数の用意 #####

from selenium import webdriver
import time
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request as request
import shutil
import os
import matplotlib.pyplot as plt
import numpy as np
import japanize_matplotlib
name_list = []
cash = {}
time.sleep(20)

##### ブラウザ起動 #####
browser = webdriver.Chrome(executable_path = r"C:\Users\●●●●\chromedriver.exe")#webdriverのパス
browser.implicitly_wait(8)

url_login =" https://www.sbisec.co.jp/ETGate"
browser.get(url_login)
time.sleep(7)


#============================================#
#         SBI証券口座をスクレイピング
#============================================#


##### SBI口座ログイン #####

def sbi_login (id = 0, passeord = 0):
    
    id = input("口座のIDを入力してください 例:000-0000000：")
                
    element = browser.find_element_by_name("user_id")
    element.clear()
    element.send_keys(id)
    password = input("パスワードを入力してください：")
    input_user_password = browser.find_element_by_name('user_password')
    input_user_password.send_keys(password)
    password = 0
    time.sleep(5)
    browser.find_element_by_name('ACT_login').click()
    time.sleep(5)
 
           


##### 日本株保有一覧csvのダウンロード #####
def sbi_stock_list(name): 
    browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div/ul/li[3]/a/img').click()
    time.sleep(5)
    browser.find_element_by_xpath('/html/body/div[1]/table/tbody/tr/td[1]/table/tbody/tr[2]/td/table[1]/tbody/tr/td/form/map/area[2]').click()
    time.sleep(5)
    browser.find_element_by_xpath('/html/body/div[1]/table/tbody/tr/td[1]/table/tbody/tr[2]/td/form/table[2]/tbody/tr[1]/td[2]/table[2]/tbody/tr[2]/td[6]/a').click()
    time.sleep(7)
    filename = name + ".csv"
    folder_pass = os.path.join(r"C:\Users\●●●●" + filename) #移動先のパス
    
    if os.path.exists(folder_pass):
        os.remove(folder_pass)
    new_path = shutil.move(r"C:\Users\●●●●\SaveFile.csv",foloder_pass)#ダウンロードフォルダ
    time.sleep(7)



##### 保有米ドル高、保有米国株情報取得 #######
def sbi_us_scraping():
 browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div/ul/li[3]/a/img').click()
 time.sleep(5)
 browser.find_element_by_class_name("navi2M").click()
 time.sleep(5)
 response = browser.page_source
 bs2 = BeautifulSoup(response, 'html.parser')
 dollor = bs2.select("#detail_USD > td:nth-child(3) > table > tbody > tr:nth-child(1) > td.stext")[0].text
         
 list_us_stock=[]

 us_stock = bs2.select(".mtext")
 for i in range(54,len(z)-2):
     if i%2==0:
         us_stock = us_stock[i].select("td", colspan="2")
         us_stock = us_stock[0].text
         us_stock = us_stock.split()
         code = us_stock[0]
         stock_name="".join(us_stock[1:])
     else:
         us_stock = us_stock[i].select("td",nowrap="")
         info = [us_stock[0].text,us_stock[1].text,us_stock[2].text]
         info.insert(0,stock_name)
         info.insert(0,code)
         list_us_stock.append(info)


##### ログアウトと再ログイン画面 #####
def sbi_logout():
    browser.find_element_by_xpath('//*[@id="logoutM"]/a/img').click()
    time.sleep(7)
    browser.find_element_by_xpath('//*[@id="logo"]/a/img').click()
    time.sleep(7)

sbi_login()

##### 日本円保有残高取得 #####
browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div/ul/li[3]/a/img').click()
time.sleep(5)
response = browser.page_source
bs = BeautifulSoup(response, 'html.parser')
time.sleep(7)
owner_cash = bs.select("body > div:nth-child(1) > table > tbody > tr > td:nth-child(1) > table > tbody > tr:nth-child(2) > td > table:nth-child(1) > tbody > tr > td > form > table:nth-child(3) > tbody > tr:nth-child(1) > td:nth-child(2) > table:nth-child(20) > tbody > tr > td:nth-child(1) > table:nth-child(7) > tbody > tr:nth-child(3) > td.mtext > div > font")[0].text.replace(',','')


sbi_stock_list(owner)#対象者名を入力
sbi_us_scraping()
sbi_logout()


sbi_login()
sbi_stock_list(owner2)#2人目対象者名を入力
sbi_us_scraping()
sbi_logout()



#============================================#
#         口座情報と資産管理表をmerge
#============================================#

##### ダウンロードした日本株保有一覧csvをmerge用に加工 #####

#※パス削除
df_download_data = pd.read_csv(r"C:\Users\●●●●\owner.csv", encoding="shift-jis",names=["銘柄コード", "銘柄名称","保有株数","売却注文中","取得単価","現在値","取得金額","評価額","評価損益"])#csvのパス
df_download_data = df_download_data.drop("売却注文中",axis=1)
df_download_data = df_download_data[df_download_data['取得単価'] != "取得単価"]

nisa = list(df_download_data.query('銘柄コード == "株式（NISA預り）"').index)
df_download_data.insert(2,"口座種類",0)
df_download_data.loc[0:nisa[0], '口座種類'] = 'specific'
df_download_data.loc[nisa[0]: , '口座種類'] = 'NISA'

df_download_data = df_download_data.dropna(axis = 0,how ="any")
df_download_data.insert(2, '口座名義', owner)
df_download_data = df_download_data.drop('銘柄名称', axis=1)

##### 加工したデータと事前に作成していた資産管理表をmerge ######    

df_stock_list_SBI = pd.read_csv(r"C:\Users\●●●●.csv", encoding='cp932')#資産管理表のパス
df_merge = pd.merge(df_stock_list_SBI,df_download_data,left_on=["銘柄コード","口座名義","口座種類"],right_on=["銘柄コード","口座名義","口座種類"],how="outer")
    
##### 現金と米国株情報を追加 ######
count = list(df_merge.query('銘柄コード == "owner_cash"').index)
df_merge.iloc[count[0],4:6] = 0
df_merge.iloc[count[0],8:14] = 0
df_merge.loc[count[0],"取得金額"] = cash
df_merge.loc[count[0],"評価額"] = cash
    
count = list(df_merge.query('銘柄コード == owner_us_cash').index)
df_merge.iloc[count[0],4:6] = 0
df_merge.iloc[count[0],8:14] = 0
df_merge.loc[count[0],"取得金額"] = float(dollor)*100
df_merge.loc[count[0],"評価額"] = float(dollor)*100

##### 金額データを全て数値データ化 #####
df_merge['取得金額'] = df_merge['取得金額'].astype(int)
df_merge['評価額'] = df_merge['評価額'].astype(int)
df_merge.loc[ : ,"評価損益"] = df_merge.loc[ : ,"評価額"] - df_merge.loc[ : ,"取得金額"]

#============================================#
#         資産ポートフォリオ、運用状況分析
#============================================#
df_owner = df_merge[df_merge['所有者'] == "owner"]#分析対象者名

##### ポートフォリオ #####
df_pivot_kind = df_owner.pivot_table(index="資産種類",values=["取得金額","評価額","評価損益"],aggfunc="sum")
df_pivot_kind = df_pivot_kind.loc[:, ["取得金額","評価額","評価損益"]]
df_pivot_kind = df_pivot_kind.applymap("{:,.0f}".format)
df_pivot_kind["評価額"] = df_pivot_kind["評価額"].str.replace(',','').astype(int)
df_pivot_kind = df_pivot_kind.sort_values("評価額", ascending=False)
variety = df_pivot_kind.index
variety_price = df_pivot_kind["評価額"].values
plt.pie(variety_price , labels = variety , autopct = "%.1f%%", startangle = 90,counterclock = False , radius=2)


##### 目的別保有資産比率 #####
df_pivot2 = df_owner.pivot_table(index="目的",values=["取得金額","評価額","評価損益"],aggfunc="sum")
df_pivot2 = df_pivot2.loc[:, ["取得金額","評価額","評価損益"]]
df_pivot2 = df_pivot2.applymap("{:,.0f}".format)
df_pivot2["評価額"] = df_pivot2["評価額"].str.replace(',','').astype(int)
count = df_pivot2["評価額"].values
label = df_pivot2.index
plt.pie(count, labels = label , autopct = "%.1f%%", startangle = 90,counterclock = False)

##### TOP12保有銘柄比率 #####
df_sort = df_owner[df_owner["目的"] != "cash"]
df_sort = df_sort.sort_values("評価額", ascending=Fales)
df_sort = df_sort.reset_index()
df_sort.loc[12,"銘柄名称"] = "その他"
df_sort.loc[12,"評価額"] = df_sort["評価額"][df_sort.index >= 12].sum()
df_top12 = df_sort[df_sort.index<=12]
stock_total_price = df_top12["評価額"].values
stock_name_top12 = df_top12["銘柄名称"].values
plt.pie(stock_total_price, labels = stock_name_top12 , autopct = "%.1f%%", startangle = 90,counterclock = False , radius=2)

##### 運用利回り #####
owner_total = df_owner['評価額'].sum()
df_return = pd.read_csv(r"C:\Users\●●●●.csv", encoding='cp932')#週次資産残高集計表
df_return["sp500_return"].astype(float)
x = df_return["date"]
y_sp500 = df_return["sp500_return"]
y_topics = df_return["topics_return"]
y_owner = df_return["owner_return"]
plt.ylabel("運用利回り")
plt.grid(True)
plt.plot(x,y_sp500,label="S&P500")
plt.plot(x,y_topics,label="TOPICS")
plt.plot(x,y_owner,label="owner")
plt.legend(loc = "upper left")

##### 対投下資本運用益 #####
y_owner_capital = df_return["owner_capital"]
y_owner_asset = df_return["owner"]
plt.fill_between(x , y_owner_capital , facecolor = "lightblue" , alpha =0.5 , label = "投資資本")
plt.fill_between(x , y_owner_asset , y_owner_capital , facecolor = "orange" , alpha=0.5 , label = "運用益")
plt.legend(loc = "upper left")

