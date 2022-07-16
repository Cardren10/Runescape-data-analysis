import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

#Scraping website to get names and ids for all tradable items
#browser options and connecting to page
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
url = 'https://prices.runescape.wiki/osrs/all-items'
wd = webdriver.Chrome(ChromeDriverManager().install())
wd.get(url)

#getting the page HTML
soup = BeautifulSoup(wd.page_source, 'lxml')
table = soup.find('table', class_ = 'wgl-allitemstable table table-dark table-sm table-striped table-bordered table-hover')

#loop to get item names, href, and buy limit and put them in a list
item_name_list = []
item_id_list = []
buy_limit_list = []

#loop to scrap the interactive table
lastpage = iter([True, False])
while wd.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[3]/div/div[1]/button[3]').is_enabled() == True or next(lastpage):
    soup = BeautifulSoup(wd.page_source, 'lxml')
    table = soup.find('table', class_ = 'wgl-allitemstable table table-dark table-sm table-striped table-bordered table-hover')
    for items in table.find_all('tbody'):
        rows = items.find_all('tr')                             
        for column in rows:
            item_name = column.find_all('td', {'role':'cell'})[1].text
            item_name_list.append(item_name)
            item_id = str(column.find_all('td', {'role':'cell'})[1])
            item_id_list.append(item_id)
            buy_limit = column.find_all('td', {'role':'cell'})[2].text
            buy_limit_list.append(buy_limit)
        wd.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[3]/div/div[1]/button[3]').click()
        time.sleep(0.5)
        break

#Creating a dataframe with my lists and exporting
osrs_item_df = pd.DataFrame(list(zip(item_name_list, item_id_list, buy_limit_list)), columns = ['item_name','item_id', 'buy_limit'])

#cleaning item id in the dataframe
osrs_item_df['item_id'] = osrs_item_df['item_id'].str.replace(pat = '(.*item\/)', repl = '', regex = True)
osrs_item_df['item_id'] = osrs_item_df['item_id'].str.replace(pat = '(">.*)', repl = '', regex = True)

#exporting as .csv
osrs_item_df.to_csv('osrs_item_table.csv')

#importing data from csv
osrs_item_df = pd.read_csv('osrs_item_table.csv', index_col=(0))

#Getting historical price data from the runescape wiki
#getting all item ids as a list from my item dataframe and concatenating it with the weirdgloop api format
item_ids = osrs_item_df['item_id'].tolist()
item_ids = list(map(str,item_ids))
address = 'https://api.weirdgloop.org/exchange/history/osrs/all?id='
#Loop to get all the data from the API
prices_df = pd.DataFrame()
for ids in item_ids:
    requests.get(str(address+ids))
    output = requests.get(str(address+ids)).json()
    output = output[str(ids)]
    prices_df = prices_df.append(output)
    time.sleep(0.5)
