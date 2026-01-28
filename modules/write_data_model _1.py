"""
This module uses Selenium to scrape product data from an https://brain.com.ua/
and saves it to a Django database model named Phone."""
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

import sys
import os
import re
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException


import sys
import os

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
from get_characteristics_photos import get_characteristics_photos




def search_product(driver, wait, query=None):
    general = {}

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
    search_input.send_keys(query)
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'search-form') and contains(@class, 'header-search-form')]//input[@type='submit']")))
    try:
        search_button.click()
    except NoSuchElementException:
        print(f"doesn't exist: {search_button}")
        search_button = None


    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'product-wrapper') and contains(@class, 'br-pcg-product-wrapper')]")))

        product_link_xpath = "//div[contains(@class, 'product-wrapper')][1]//a[img[contains(@src, 'prod_img')]]"
        first_product = wait.until(EC.presence_of_element_located((By.XPATH, product_link_xpath)))
        href = first_product.get_attribute('href')

    except TimeoutException:
        print(f"Product link not found with xpath: {product_link_xpath}")
        product_link_xpath = None
        return

    try:
        old_url = driver.current_url
        driver.execute_script("arguments[0].click();", first_product)
        WebDriverWait(driver, 20).until(lambda d: d.current_url != old_url)
    except TimeoutException:
        print("Page did not load after clicking the product link.")
        return
    
    try:
       
        product_name_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'desktop-only-title')]"))
        )
  
        product_name = driver.execute_script("return arguments[0].textContent;", product_name_element)
        if product_name:
            product_name = product_name.strip()
        general['product_name'] = product_name
        #print("Product Name:", product_name)
        
    except TimeoutException:
        print("Timeout while waiting for product name element.")
        element = None

    except NoSuchElementException:
        print("Product name not found.")
        product_name = None

    
    colors = []
    
    color_items = driver.find_elements(By.XPATH, "//div[contains(@class, 'series-item') and contains(@class, 'series-color')]")
    for item in color_items:
        try:
            a_tag = item.find_element(By.TAG_NAME, 'a')
            url = a_tag.get_attribute('href')
            match = re.search(r'iPhone_15_128GB_([A-Za-z]+)-p', url)
            if match:
                color = match.group(1).replace('_', ' ')
            else:
                color_div = item.find_element(By.CSS_SELECTOR, '.slice')
                style = color_div.get_attribute('style')
                color = style.split('background:')[1].split(';')[0].strip() if style and 'background:' in style else None
            colors.append(color)
        except NoSuchElementException:
            colors = None
        colors = list(set(colors)) 

    filtered_colors = [c for c in colors if c and not c.startswith('rgb')]
    general['colors'] = filtered_colors

    #print("Colors:", filtered_colors)


    memory_capacity = []
    memory_items = driver.find_elements(
        By.XPATH,
        "//div[contains(@class, 'stuff-series-characteristics') and contains(@class, 'current-product-series')]//div[contains(@class, 'series-item') and contains(@class, 'series-characteristic')]//a"
    )
    for item in memory_items:
        try:
            text = item.text.strip()
            memory_capacity.append(text)
        except NoSuchElementException:
            memory_capacity = None
    general['memory_capacity'] = memory_capacity
    #print("Memory capacities:", memory_capacity)


    manufacturer = None
    try:
        div = driver.find_element(
            By.XPATH,
            "//div[span[contains(translate(text(),'ВИРОБНИКПРОИЗВОДИТЕЛЬMANUFACTURER','виробникпроизводительmanufacturer'),'виробник') or contains(translate(text(),'ВИРОБНИКПРОИЗВОДИТЕЛЬMANUFACTURER','виробникпроизводительmanufacturer'),'производитель') or contains(translate(text(),'ВИРОБНИКПРОИЗВОДИТЕЛЬMANUFACTURER','виробникпроизводительmanufacturer'),'manufacturer')]]"
        )
        spans = div.find_elements(By.TAG_NAME, "span")
        if len(spans) > 1:
            manufacturer = spans[1].text.strip()
            if not manufacturer:
                inner_html = driver.execute_script("return arguments[0].innerHTML;", spans[1])
                if inner_html:
                    manufacturer = inner_html.strip().replace('\n', '').replace('\r', '').replace('  ', '').strip()
    except NoSuchElementException:
        manufacturer = None
    general['manufacturer'] = manufacturer
    #print("Manufacturer:", manufacturer)
                

    price = None
    promo_price = None
    try:
 
        price_elem = driver.find_element(By.XPATH, "//div[contains(@class,'br-pr-op')]//div[contains(@class,'price-wrapper')]/span")
        price = price_elem.text.strip().replace('\xa0', ' ')
    except Exception:
        price = None
    try:

        promo_elem = driver.find_element(By.XPATH, "//div[contains(@class,'br-pr-np')]//div[contains(@class,'price-wrapper')]/span[contains(@class,'red-price') or not(@class)]")
        promo_price = promo_elem.text.strip().replace('\xa0', ' ')
    except Exception:
        promo_price = None
        price = None
    general['price'] = price
    general['promotional_price'] = promo_price
    # print("Price:", price)
    # print("Promo price:", promo_price)


    

    product_code = None
    try:
        code_block = driver.find_element(By.XPATH, "//div[contains(@class,'product-code-num')]")
        spans = code_block.find_elements(By.TAG_NAME, "span")
        for span in spans:
            if "br-pr-code-val" in span.get_attribute("class"):
                product_code = driver.execute_script("return arguments[0].textContent;", span).strip()
                break
    except NoSuchElementException as e:
        print(f"Product code not found: {e}")
    general['product_code'] = product_code
    #print("Product code:", product_code)


    number_of_reviews = None
    try:
        reviews_block = driver.find_element(By.XPATH, "//div[contains(@class,'series-comments-block') and contains(@class,'fast-navigation-comments-block')]")
        reviews_link = reviews_block.find_element(By.XPATH, ".//a[contains(@class,'series-reviews') and contains(@class,'reviews-count')]")
        span = reviews_link.find_element(By.TAG_NAME, "span")
        number_of_reviews = driver.execute_script("return arguments[0].textContent;", span).strip()
    except NoSuchElementException as e:
        print(f"Number of reviews not found: {e}")
    #print("Number of reviews:", number_of_reviews)
    general['number_of_reviews'] = number_of_reviews

     

    # print("General info extracted:")
    for key, value in general.items():
        print(f"  {key}: {value}")

    try:

        phone = Phone.objects.get_or_create(
            product_name = product_name,
            number_of_reviews = number_of_reviews,
            product_code = product_code,
            promotional_price = promo_price,
            price = price,
            manufacturer = manufacturer,
            memory_capacity = memory_capacity,
            colors = colors,
            status="Done")
          

    except Exception as e:
        print(f"Error saving to database: {e}")
        phone = None




def main():
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
        search_product(driver, wait, "Apple iPhone 15 128GB Black")
        get_characteristics_photos(driver, wait, "Apple iPhone 15 128GB Black")
    finally:
        driver.quit()

    print("Data extraction completed.")
    
if __name__ == "__main__":
    main()
