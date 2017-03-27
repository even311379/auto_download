# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 10:45:52 2017

Web scraping LANDSAT
Automatic save file
@author: user
"""
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
import re
import pandas as pd
import datetime
import os

f = open('area_content.txt','r')
content = f.read()
f.close()

p1 = re.compile('"sceneID":"(.*?)"')
p2 = re.compile('"sensor":"(.*?)"')
p3 = re.compile('"cloudCover":(.*?),')
p4 = re.compile('"sceneStartTime":(.*?),')
p5 = re.compile('"month":(.*?),')
p6 = re.compile('"year":(.*?),')
p7 = re.compile('"dayOfYear":(.*?),')
p8 = re.compile('"Shape_Length":(.*?),')
p9 = re.compile('"Shape_Area":(.*?)}')
p10 = re.compile('"CenterX":(.*?),')
p11 = re.compile('"CenterY":(.*?),')


METADATA = pd.DataFrame({"sceneID":re.findall(p1,content),"sensor":re.findall(p2,content),"cloudCover":[int(i) for i in re.findall(p3,content)],\
"sceneStartTime":[int(i) for i in re.findall(p4,content)],"month":[int(i) for i in re.findall(p5,content)],"year":[int(i) for i in re.findall(p6,content)],\
"dayOfYear":[int(i) for i in re.findall(p7,content)],"Shape_Length":[float(i) for i in re.findall(p8,content)],"Shape_Area":[float(i) for i in re.findall(p9,content)],\
"CenterX":[float(i) for i in re.findall(p10,content)],"CenterY":[float(i) for i in re.findall(p11,content)]})

#METADATA.to_excel('METADATA.xlsx')

Tidal = pd.read_excel('Tidal-time_Taichung.xlsx')


fmt = '%Y.%m.%d'

s = [str(y)+'.'+str(m)+'.'+str(d) for y,m,d in zip(Tidal.yyyy, Tidal.mm,Tidal.dd)]

Tidal_julian_day = []
fmt = '%Y.%m.%d'
for i in s:
    dt = datetime.datetime.strptime(i, fmt)
    tt = dt.timetuple()
    Tidal_julian_day.append(str(tt.tm_year * 1000 + tt.tm_yday))


scene_date = []

scene_date = [str(y*1000+jd) for y,jd in zip(METADATA.year.tolist(),METADATA.dayOfYear.tolist())]

Scene_Data = pd.concat([METADATA,pd.Series(scene_date,name='scene_date')],axis=1)

IDs =[]
for i in range(len(Scene_Data)):
    if Scene_Data.scene_date[i] in Tidal_julian_day:
        IDs.append(Scene_Data.sceneID[i])

Done_files = [fn[0:21] for fn in os.listdir('C:\LANDSAT_files')]
print('Number of Done files so far: %s'%len(Done_files))


for ID in Done_files:
    try:
        IDs.remove(ID)
    except:
        continue
        


download_urls = []
for ID in IDs:
    if 'LT5' in ID:
        download_urls.append('https://earthexplorer.usgs.gov/download/options/3119/'+ID+'?node=LL')
    elif 'LE7' in ID:
        download_urls.append('https://earthexplorer.usgs.gov/download/options/3373/'+ID+'?node=LL')
    else:
        print("Don't know how to set url for this scene ID. ID = "+ID)
 
#pd.DataFrame(download_urls).to_excel('ALL_target_download_urls.xlsx')
    

# firefox settings
binary = FirefoxBinary('C:\Program Files (x86)\Mozilla Firefox//firefox.exe')
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", 'C:\LANDSAT_files')
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")

# Excecuate the task here:


browser = webdriver.Firefox(firefox_profile=profile,firefox_binary=binary)
browser.get('https://ers.cr.usgs.gov/login/')
time.sleep(3)
user = browser.find_element_by_id('username')
user.send_keys('aychang')
password = browser.find_element_by_id('password')
password.send_keys('wolf1122')
login = browser.find_element_by_id('loginButton')
login.click()
time.sleep(3)

Done_urls = []
Unfinished_urls = download_urls
Probelmatic_urls = []

Fail_urls = pd.read_excel('Probelmatic_urls.xlsx')[0].tolist()

'''
for url in Fail_urls:
    download_urls.remove(url)
'''

print('Number of remaining files: %s'%len(download_urls))
print('Start the task:')

for url in download_urls:
    try:
        browser.get(url)
        time.sleep(5)
        download_project = browser.find_element_by_css_selector('#optionsPage > div > div:nth-child(4) > input')
        download_project.click()
        time.sleep(15)
        Done_urls.append(url)
        Unfinished_urls.remove(url)
        
    except:
        print('Something Wrong happened for this url: %s'%url)
        Probelmatic_urls.append(url)
        continue

    if (len(Done_urls))%5 == 0:
        pd.DataFrame(Done_urls).to_excel('Done_urls.xlsx')
        pd.DataFrame(Unfinished_urls).to_excel('Unfinished_urls.xlsx')
        time.sleep(900)
        print('Files finished: %s'%len(Done_urls))
        



pd.DataFrame(Probelmatic_urls+Fail_urls).to_excel('Probelmatic_urls.xlsx')    


