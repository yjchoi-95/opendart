from selenium import webdriver
#from selenium.webdriver import FirefoxOptions
#from selenium.webdriver.firefox.service import Service
#from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
#from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


import streamlit as st
import os, sys

import subprocess
#st.write(subprocess.call("whereis firefox", shell=True))
#st.write(a)

@st.cache_resource
def installff():
    #os.system('/home/appuser/venv/bin/python -m pip install --upgrade pip')
    #os.system('cd . add-apt-repository ppa:ubuntu-mozilla-security/ppa')
    #os.system('sbase install geckodriver')
    #os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')
    #os.system('export PATH=$PATH:/home/appuser/venv/bin/geckodriver')
    #os.system('export PATH=$PATH:/home/appuser/venv/bin/firefox')
    #os.system('export PATH=$PATH:/home/appuser/venv/bin/firefox.exe')
    #os.system('export PATH=$PATH:/home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver')
    
    os.system('sbase install chromedriver')
    os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/chromedriver /home/appuser/venv/bin/chromedriver')
    os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/chromedriver /home/appuser/.cache/selenium/chromedriver/linux64/114.0.5735.90/chromedriver')
    os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/chromedriver /home/appuser/.wdm/selenium/chromedriver/linux64/114.0.5735.90/chromedriver')

    
    #/home/appuser/.wdm/drivers/chromedriver/linux64/114.0.5735.90/chromedriver
    
_ = installff()
st.write("finish-install")

#opts = FirefoxOptions()
#opts.add_argument("--headless")
#firefox_binary = FirefoxBinary('/home/appuser/venv/bin/firefox.exe')
#st.write("set-binary")

#opts.binary = firefox_binary
#opts.binary_location = '/home/appuser/venv/bin/geckodriver'
#opts.binary_location = '/home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver.exe'
#opts.binary_location = '/home/appuser/venv/bin/firefox.exe'

#service = Service(GeckoDriverManager().install())
st.write("set-service")
#browser = webdriver.Firefox(service = service, options=opts)
st.write("run-browser")
#browser = webdriver.Firefox(options=opts)
options = Options()
options.add_argument("--headless")

#browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options = options)

#browser = webdriver.Chrome(service = Service(excutable_path = '/home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/chromedriver'), options = options)
browser = webdriver.Chrome(options = options)

#browser.get('http://naver.com')
st.write(browser.page_source)