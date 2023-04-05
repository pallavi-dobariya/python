import time, json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parsel import Selector

top_charts = {
    "link":[],
    "title":[]
}

def scroll_page(url):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    while True:
        try:
            driver.execute_script("document.querySelector('.kofMvc').click();")
            WebDriverWait(driver, 10000).until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))
            break
        except:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, 10000).until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))
    scrape_top_charts(driver=driver, chart='Top free', button_selector='#ct\|apps_topselling_free .ypTNYd')
    scrape_top_charts(driver=driver, chart='Top grossing', button_selector='#ct\|apps_topgrossing .ypTNYd')
    scrape_top_charts(driver=driver, chart='Top paid', button_selector='#ct\|apps_topselling_paid .ypTNYd')
    
    selector = Selector(driver.page_source)
    driver.quit()
    return selector

def scrape_top_charts(driver, chart, button_selector):
    print('----------scrape_top_charts-----------')
    button = driver.find_element(By.CSS_SELECTOR, button_selector)
    driver.execute_script("arguments[0].click();", button)
    time.sleep(2)
    selector = Selector(driver.page_source)
    for result in selector.css('.itIJzb'):
        title = result.css('.OnEJge::text').get()
        link = 'https://play.google.com' + result.css('::attr(href)').get()
        top_charts['link'].append(link)
        top_charts['title'].append(title)
            
def scrape_google_play_apps(URL):
    result = scroll_page(URL)
    return top_charts