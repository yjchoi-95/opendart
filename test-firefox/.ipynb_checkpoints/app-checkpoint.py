import streamlit as st
import time
import os

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

import subprocess

#os.system("google-chrome --version")
#os.system("firefox -v")
os.system("apt install flatpak")
os.system("flatpak install flathub org.mozilla.firefox")

#os.system("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
#os.system("cd ~")
#os.system("apt install ./google-chrome-stable_current_amd64.deb")

#os.system("apt-get update && \
#      apt-get -y install sudo")

#os.system("sudo add-apt-repository ppa:ubuntu-mozilla-security/ppa")

def test():
    st.write(subprocess.call("locate firefox", shell=True))
    st.write(subprocess.call("whereis firefox", shell=True))
    st.write(subprocess.call("which firefox", shell=True))
    st.write(os.getcwd())

    #os.system('sbase install chromedriver')
    st.write(subprocess.call("locate chromedriver", shell=True))
    st.write(subprocess.call("whereis chromedriver", shell=True))
    st.write(subprocess.call("which chromedriver", shell=True))

    #os.system('sbase install geckodriver')
    st.write(subprocess.call("locate geckodriver", shell=True))
    st.write(subprocess.call("whereis geckodriver", shell=True))
    st.write(subprocess.call("which geckodriver", shell=True))

def save():

    URL = "https://www.unibet.fr/sport/football/europa-league/europa-league-matchs"
    XPATH = "//*[@class='ui-mainview-block eventpath-wrapper']"
    TIMEOUT = 20

    st.title("Test Selenium")
    st.markdown("You should see some random Football match text below in about 21 seconds")

    firefoxOptions = Options()
    firefoxOptions.add_argument("--headless")
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(
        options=firefoxOptions,
        service=service,
    )
    driver.get(URL)

    try:
        WebDriverWait(driver, TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, XPATH,))
        )

    except TimeoutException:
        st.warning("Timed out waiting for page to load")
        driver.quit()

    time.sleep(10)
    elements = driver.find_elements_by_xpath(XPATH)
    st.write([el.text for el in elements])
    driver.quit()
