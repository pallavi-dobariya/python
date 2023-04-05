import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from selenium.webdriver.common.by import By
import re   
import scrape_top_charts as charts
from google_play_scraper import app
import openpyxl
import googletrans
from googletrans import Translator
print(googletrans.__version__)
from openpyxl import Workbook
countries = pd.read_excel('C:/Users/kc/Desktop/Play_store_webscraping/MENA_COUNTRIES/Country_categories.xlsx',sheet_name='Countries')
df = pd.read_excel('C:/Users/kc/Desktop/Play_store_webscraping/MENA_COUNTRIES/Country_categories.xlsx',sheet_name='Categories')
categories = df['category']
print(categories)

links = list()
final_links = list()
final_link = ''
f_links = list()
data =pd.DataFrame(columns = ['all_app_links'])
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
translator = Translator()
def scrape_play_store_category_links():
# take one by one country name and country code from country sheet
    #for c_n in range(18,len(countries)):
    country_name = 'United Arab Emirates'
    print('Country Name : ',country_name)
#create excel sheet of one country 
    # workbook = Workbook()
    # workbook.save('C:/Users/kc/Desktop/Play_store_webscraping/MENA_COUNTRIES/APP_LINKS/'+country_name+".xlsx")
    country_code = 'ae'
#take one by one category from categories sheet
    for c in categories[1:]:
        row_data = [['App_Links']]
        print('category -----------------',c)
#extract the app links from top charts,top free,top grossing
        charts.top_charts = {
        "link":[],
        "title":[]
        }
        top_chart_links = list()
#extract app links from first page
        URL = "https://play.google.com/store/apps/category/"+c+"?gl="+country_code
        top_charts = charts.scrape_google_play_apps(URL)
        for j in top_charts["link"]:
            top_chart_links.append(j) 

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.get(URL)
        time.sleep(5)

        SCROLL_PAUSE_TIME = 2
        
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(SCROLL_PAUSE_TIME)
        
        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
        
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        links_games = list()  
        
        #elems = driver.find_elements(By.XPATH,"//a[@href]")
        elems = driver.find_elements(By.CLASS_NAME,"Si6A0c")
        for elem in elems:
            if "details?id" in elem.get_attribute("href"):
                links_games.append((elem.get_attribute("href")))
                
        #links_games = list(dict.fromkeys(links_games))
        
        lnk = list()
#combine app links first is top_chart_links and second is links_games 
#create unique app link list from both top_chart_links and links_games and create list as name lnk
        combine_link = top_chart_links + links_games
        for x in combine_link:
            if x not in lnk:
                lnk.append(x+'&gl='+country_code)
        print(lnk)
        print('main link-----------------------------------')
        links = lnk
        driver1 = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver2 = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        all_link = list()
# open one by one app from lnk and open similar app 
        for link in links:
            driver1.get(link)
            elems = driver1.find_elements(By.TAG_NAME,'a')
            for elem in elems:
                try:
                    if'/store/apps/collection/cluster?' in elem.get_attribute('href'):
                        ur = elem.get_attribute('href')
                        driver2.get(ur)
                        all_lnks = driver2.find_elements(By.TAG_NAME,'a')
                        for lnk in all_lnks:
                            if '/store/apps/details?' in lnk.get_attribute('href'):
                                if lnk.get_attribute('hef') not in all_link:
                                    all_link.append(lnk.get_attribute('href')+'&gl='+country_code)
                except:
                    print('except part ----------------------')
            print('inner links ------------------')
# same as again create unique list(final_link) and merge both lnk and and all_links(second list 1st level)
            final_link = all_link + links
            for f_lnk in final_link:
                if f_lnk not in f_links:
                    f_links.append(f_lnk)
        print('length of all links',len(final_link))
        data = pd.DataFrame(f_links,columns=['links'])
        print('first links----------------------------------------------')
#extract unique app links from list and store in data frame
        dd = pd.DataFrame(data['links'].unique(),columns=['lnks'])
        print('first created--------------------------')
        second_links = list()
        second_all_links = list()
#check the category of app  is same as original category and create another list(second_links)
        for u_lnk in data['links'].unique():
            try:
                ap_id = u_lnk.split('id=')[-1]
                app_details = app(ap_id)
                if app_details['genreId'] == c:
                    second_links.append(u_lnk)
                    print(u_lnk)
            except:
                print('except part------------')
        driver3 = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver4 = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))\
#again open one by one link from list(second_links) and extract app links(open similar app link) 2nd level
        for second_link in second_links:
            try:
                print(second_link)
                driver3.get(second_link)
                elems = driver3.find_elements(By.TAG_NAME,'a')
                if len(elems)>0:
                    for elem in elems:
                        try:
                            if'/store/apps/collection/cluster?' in elem.get_attribute('href'):
                                ur = elem.get_attribute('href')
                                driver4.get(ur)
                                second_all_lnks = driver4.find_elements(By.TAG_NAME,'a')
                                for second_lnk in second_all_lnks:
                                    if '/store/apps/details?' in second_lnk.get_attribute('href'):
                                        if second_lnk.get_attribute('href') not in second_all_links:
                                            second_all_links.append(second_lnk.get_attribute('href')+'&gl='+country_code)
                        except:
                            print('except part------------------')
            except:
                print('main except part---------------')
        print('length of second sub links ',len(second_all_links))
#merge bolth first level list and second level list
        final_all_link_list = second_links + second_all_links
#extrat the unique app  from list(final_all_link_list) create dataframe
        data_final = pd.DataFrame(final_all_link_list,columns=['final_links'])
        some_links = data_final['final_links'].unique().tolist()
        final_cat_list = list()
#check the category of app  is same as original category and create another list(second_links)
        for s_lnk in some_links:
            try:
                ap_id = s_lnk.split('id=')[-1]
                app_details = app(ap_id)
                if app_details['genreId'] == c:
                    final_cat_list.append(s_lnk)
                    print(s_lnk)
            except:
                print('link except part------------------------')
#final list which have app links of similar categories
        print('length of final links',len(final_cat_list))
        df = pd.DataFrame(final_cat_list,columns=['lnk'])
        print(df)
        print(len(df))
#save app links in excel file
        workbook = openpyxl.open('C:/Users/kc/Desktop/Play_store_webscraping/MENA_COUNTRIES/APP_LINKS/'+country_name+'.xlsx')
        sheet = workbook.create_sheet(c)
        for i in range(len(df)):
            row_data.append([df['lnk'][i]])
        for row in row_data:
            sheet.append(row)
        workbook.save('C:/Users/kc/Desktop/Play_store_webscraping/MENA_COUNTRIES/APP_LINKS/'+country_name+'.xlsx')

scrape_play_store_category_links()