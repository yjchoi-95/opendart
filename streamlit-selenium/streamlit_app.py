import os

import streamlit as st
from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.chromium.service import ChromiumService

options = ChromiumOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920x1080")

#options.add_argument("--no-sandbox")
#options.add_argument("--disable-dev-shm-usage")
#options.add_argument("--disable-gpu")
#options.add_argument("--disable-features=NetworkService")
#options.add_argument("--disable-features=VizDisplayCompositor")

def delete_selenium_log():
    if os.path.exists('selenium.log'):
        os.remove('selenium.log')

def show_selenium_log():
    if os.path.exists('selenium.log'):
        with open('selenium.log') as f:
            content = f.read()
            st.code(content)
            
def about_chrome():
    os.system('sbase get chromedriver 114.0.5735.90')
    #os.system('pwd')
    os.system('which chromedriver')
    os.system('which google-chrome')
    os.system('which chrome.exe')
    
    os.system('whereis chromedriver')
    os.system('whereis google-chrome')
    os.system('whereis chrome.exe')
    
    os.system('locate chromedriver')
    os.system('locate google-chrome')
    os.system('locate chrome.exe')
    
    os.system('sbase get geckodriver')
    os.system('locate geckodriver')
    os.system('which geckodriver')
    os.system('whereis geckodriver')
    
    os.system('locate firefox')
    os.system('which firefox')
    os.system('whereis firefox')
    
    #os.system('chmod -R 777 /root')
    #os.system('find / -name chromium -type f')
    #os.system('find / -name chrome -type f')
    #os.system('find / -name chrome.exe -type f')
    #os.system('find / -name chromedriver -type f')

def run_selenium():
    name = str()

    os.system('find / -name chrome*')
    import selenium
    st.write(selenium.__version__)
    
    #os.system('chromium-browser --product-version')
    #os.system('google-chrome --product-version')
    #os.system('docker run -ti -p 8501:8501 -v $(pwd):/app --rm selenium:latest')
    
    #service = Service(executable_path = '/app/opendart/streamlit-selenium/chromedriver')
    #with webdriver.Chrome(options=options, service_log_path='selenium.log') as driver:
    #with webdriver.Chrome(service = service, options=options) as driver:
    #with webdriver.Chrome(options=options) as driver:
    #with webdriver.ChromiumEdge(options=options) as driver:
    with webdriver.chrome.webdriver.ChromiumDriver(options=options) as driver:
        url = "https://www.unibet.fr/sport/football/europa-league/europa-league-matchs"
        driver.get(url)
        xpath = '//*[@class="ui-mainview-block eventpath-wrapper"]'
        # Wait for the element to be rendered:
        element = WebDriverWait(driver, 10).until(lambda x: x.find_elements(by=By.XPATH, value=xpath))
        name = element[0].get_property('attributes')[0]['name']
    return name


if __name__ == "__main__":
    #delete_selenium_log()
    st.set_page_config(page_title="Selenium Test", page_icon='✅',
        initial_sidebar_state='collapsed')
    st.title('🔨 Selenium Test for Streamlit Sharing')
    st.markdown('''This app is only a very simple test for **Selenium** running on **Streamlit Sharing** runtime.<br>
        The suggestion for this demo app came from a post on the Streamlit Community Forum.<br>
        <https://discuss.streamlit.io/t/issue-with-selenium-on-a-streamlit-app/11563><br>
        This is just a very very simple example and more a proof of concept.
        A link is called and waited for the existence of a specific class and read it.
        If there is no error message, the action was successful.
        Afterwards the log file of chromium is read and displayed.
        ---
        ''', unsafe_allow_html=True)

    st.balloons()
    if st.button('Start Selenium run'):
        st.info('Selenium is running, please wait...')
        result = run_selenium()
        st.info(f'Result -> {result}')
        st.info('Successful finished. Selenium log file is shown below...')
        #st.write('sucesss')
        #show_selenium_log()
