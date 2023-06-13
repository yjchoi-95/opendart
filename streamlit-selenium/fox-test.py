import os

import streamlit as st
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-features=NetworkService")
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-features=VizDisplayCompositor")
#options.binary_location('/home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/chromedriver')

#service = Service(executable_path = '/home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/chromedriver')
firefoxOptions = Options()
firefoxOptions.add_argument("--headless")
driver = webdriver.Firefox(
    options=firefoxOptions,
    executable_path="/home/appuser/.conda/bin/geckodriver",
)
driver.get(URL)