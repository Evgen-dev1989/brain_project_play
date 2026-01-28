"""
This module uses Selenium to scrape product data from an https://brain.com.ua/
and saves it to a Django database model named Phone."""
import os
import time
import sys

import re

from playwright.sync_api import sync_playwright, TimeoutError, Error

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



def search_product():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            try:
                page.goto("https://brain.com.ua/ukr/", timeout=20000)
                page.wait_for_timeout(3000)

                inputs = page.query_selector_all("input[type='search']")
                search_selector = "div.search-form.header-search-form input.quick-search-input[type='search']"
                inputs = page.query_selector_all(search_selector)

                visible_inputs = [inp for inp in inputs if inp.is_visible()]
                if visible_inputs:
                    try:
                        visible_inputs[0].fill("Apple iPhone 15 128GB Black")
                    except Error as e:
                        print(f"Error filling search input: {e}")
                        visible_inputs = None
                else:
                    print("does not find visible search input")
                    return

                try:
                    visible_inputs[0].press('Enter')
                    # Явное ожидание появления блока с товарами (до 10 секунд)
                    try:
                        page.wait_for_selector('div.product-wrapper', timeout=10000)
                    except TimeoutError:
                        print("Блок с товарами не появился!")
                    # Повторные попытки поиска ссылки на первый продукт
                    first_product_link = None
                    for attempt in range(3):
                        first_product_link = page.query_selector("div.product-wrapper a[href*='Mobilniy_telefon']")
                        if first_product_link:
                            break
                        else:
                            page.wait_for_timeout(1500)
                    if first_product_link:
                        href = first_product_link.get_attribute('href')
                        print("Переход по ссылке:", href)
                        page.goto(href, timeout=15000)
                        page.wait_for_timeout(2000)
                
                        # html_content = page.content()
                        # with open("brain_first_product.html", "w", encoding="utf-8") as f:
                        #     f.write(html_content)
                    else:
                        print("link to first product not found after retries.")
           
                except Error as e:
                    print(f"Error in {e}")
                    return
            except Error as e:
                print(f"Playwright error page.goto https://brain.com.ua/ukr/: {e}")


    finally:
        if browser:
            try:
                browser.close()
            except Error as e:
                print(f"Error in closing browser: {e}")
        # html_content = page.content()
            # with open("brain_first_product.html", "w", encoding="utf-8") as f:
            #     f.write(html_content)

    



    








    # for key, value in general.items():
    #     print(f"  {key}: {value}")

    # try:

    #     phone = Phone.objects.get_or_create(
    #         product_name = product_name,
    #         number_of_reviews = number_of_reviews,
    #         product_code = product_code,
    #         promotional_price = promo_price,
    #         price = price,
    #         manufacturer = manufacturer,
    #         memory_capacity = memory_capacity,
    #         colors = colors,
    #         status="Done")
          

    # except Exception as e:
    #     print(f"Error saving to database: {e}")
    #     phone = None






def main():

  
    search_product()
    print("Data extraction completed.")
    
if __name__ == "__main__":
    main()
