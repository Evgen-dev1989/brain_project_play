""" get characteristics and photos links from product page https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_15_128GB_Black-p1044347.html
and saves them to Django model Phone."""
import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import re


project_root1 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root1 not in sys.path:
    sys.path.insert(0, project_root1)

project_root2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root2 not in sys.path:
    sys.path.insert(0, project_root2)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'brain_project'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brain_project.settings')

import django
django.setup()

from parser_app.models import Phone

def get_characteristics_photos(driver, wait, query=None):
    

    try:
        overlay = driver.find_element(By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'overlay') or contains(@class, 'popup') or contains(@class, 'fancybox-active')]//button[contains(@class, 'close') or contains(@class, 'btn-close') or contains(@class, 'fancybox-close')]")
        if overlay.is_displayed():
            overlay.click()
            time.sleep(0.5)
    except NoSuchElementException:
        print("No overlay found, continuing...")
        overlay = None


    search_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'search-form') and contains(@class, 'header-search-form')]//input[@type='search' and contains(@class, 'quick-search-input')]")))
    search_input.clear()
    search_input.send_keys(query if query is not None else "")
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'search-form') and contains(@class, 'header-search-form')]//input[@type='submit']")))
    try:
        search_button.click()
    except TimeoutException:
        print(f"doesn't exist: {search_button}")
        search_button = None


    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'product-wrapper') and contains(@class, 'br-pcg-product-wrapper')]")))
    except TimeoutException:
        print("Product wrapper not found (TimeoutException)")
        return

    product_link_xpath = "//div[contains(@class, 'product-wrapper')][1]//a[img[contains(@src, 'prod_img')]]"
    try:
        first_product = wait.until(EC.presence_of_element_located((By.XPATH, product_link_xpath)))
        href = first_product.get_attribute('href')

    except TimeoutException:
        print(f"Product link not found with xpath: {product_link_xpath}")
        product_link_xpath = None
        return


    old_url = driver.current_url
    driver.execute_script("arguments[0].click();", first_product)

    WebDriverWait(driver, 10).until(lambda d: d.current_url != old_url)


    screen_diagonal = None
    try:
        chr_blocks = driver.find_elements(By.XPATH, "//div[contains(@class,'br-pr-chr-item')]")
        for block in chr_blocks:
            try:
                h3 = block.find_element(By.TAG_NAME, "h3")
                h3_text = h3.text.strip().lower()
                if 'дисплей' in h3_text or 'display' in h3_text:
                    divs = block.find_elements(By.TAG_NAME, "div")
                    for div in divs:
                        spans = div.find_elements(By.TAG_NAME, "span")
                        if len(spans) >= 2:
                            label = spans[0].get_attribute('textContent').strip().lower()
                            if re.search(r'diagon|діагон|диагон', label):
                                val = ""
                                try:
                                    a_tag = spans[1].find_element(By.TAG_NAME, "a")
                                    val = a_tag.get_attribute('textContent').strip()
                                except NoSuchElementException:
                                    val = spans[1].get_attribute('textContent').strip()
                                if not val:
                                    val = spans[1].text.strip()
                                if val:
                                    screen_diagonal = val
                                    break
                    break
            except NoSuchElementException:
                continue
    except NoSuchElementException as e:
        print(f"Screen diagonal not found: {e}")
        screen_diagonal = None
    #print("Screen diagonal:", screen_diagonal)

    

    display_resolution = None
    try:
        chr_blocks = driver.find_elements(By.XPATH, "//div[contains(@class,'br-pr-chr-item')]")
        for block in chr_blocks:
            try:
                h3 = block.find_element(By.TAG_NAME, "h3")
                h3_text = h3.text.strip().lower()
                if 'дисплей' in h3_text or 'display' in h3_text:
                    divs = block.find_elements(By.TAG_NAME, "div")
                    for div in divs:
                        spans = div.find_elements(By.TAG_NAME, "span")
                        if len(spans) >= 2:
                            label = spans[0].get_attribute('textContent').strip().lower()
                            if re.search(r'разреш|роздільн|resol', label):
                                val = ""
                                try:
                                    a_tag = spans[1].find_element(By.TAG_NAME, "a")
                                    val = a_tag.get_attribute('textContent').strip()
                                except NoSuchElementException:
                                    val = spans[1].get_attribute('textContent').strip()
                                if not val:
                                    val = spans[1].text.strip()
                                if val:
                                    display_resolution = val
                                    break
                    break
            except NoSuchElementException:
                continue
    except NoSuchElementException as e:
        print(f"Screen resolution not found: {e}")
        display_resolution = None
    #print("Screen resolution:", display_resolution)

     

    characteristics = {}
    try:
        chr_blocks = driver.find_elements(By.XPATH, "//div[contains(@class,'br-pr-chr-item')]")
        for block in chr_blocks:
            try:
                h3 = block.find_element(By.TAG_NAME, "h3")
                h3_text = h3.text.strip()
                divs = block.find_elements(By.TAG_NAME, "div")
                for div in divs:
                    spans = div.find_elements(By.TAG_NAME, "span")
                    if len(spans) >= 2:
                        label = spans[0].get_attribute('textContent').strip()
                        try:
                            a_tag = spans[1].find_element(By.TAG_NAME, "a")
                            value = a_tag.get_attribute('textContent').strip()
                        except NoSuchElementException:
                            value = spans[1].get_attribute('textContent').strip()
                        if not value:
                            value = spans[1].text.strip()
                        if label and value:
                            characteristics[label] = value
            except NoSuchElementException:
                continue
    except NoSuchElementException as e:
        print(f"Characteristics collection error: {e}")
        characteristics = None
    #print("All characteristics:")
    for k, v in characteristics.items():
        clean_k = k.replace('\xa0', ' ').replace('  ', ' ').strip()
        clean_v = v.replace('\xa0', ' ').replace('  ', ' ').strip()
        print(f"  {clean_k}: {clean_v}")


    photo_links = []

    try:
        img_elements = driver.find_elements(By.XPATH, "//div[contains(@class,'product-modal-left-slider')]//img")
        for img in img_elements:
            src = img.get_attribute("src")
            if src and "no-photo.png" not in src:
                photo_links.append(src)

    except NoSuchElementException as e:
        print(f"Photo links extraction error: {e}")
        photo_links = None
    print("Photo links:", photo_links)

            
    try:

        phone = Phone.objects.get_or_create(
            characteristics=characteristics,
            photos=photo_links,
            screen_diagonal=screen_diagonal,
            display_resolution=display_resolution,
            status="Done")
          

    except Exception as e:
        print(f"Error saving to database: {e}")
        phone = None


def get_data():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=ru")
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://brain.com.ua/")
    wait = WebDriverWait(driver, 10)
    try:
        get_characteristics_photos(driver, wait, "Apple iPhone 15 128GB Black")
    finally:
        driver.quit()


def main():
    get_data()
    print("Data extraction completed.")

if __name__ == "__main__":
    main()