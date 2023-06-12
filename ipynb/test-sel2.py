from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from webdriver_manager.firefox import GeckoDriverManager

#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager


import streamlit as st
import os, sys

firefoxOptions = Options()
firefoxOptions.add_argument("--headless")

driver = webdriver.Firefox(
    options=firefoxOptions,
    executable_path="/home/appuser/.conda/bin/geckodriver",
)

driver.get("https://www.naver.com/")
st.write(driver.page_source)