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
sys.path.append(r"F:\it\Python\brain_project_play")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brain_project.settings')

import django
django.setup()

from parser_app.models import Phone



def search_product():

    general = {}
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
            
                    try:
                        page.wait_for_selector('div.product-wrapper', timeout=10000)
                    except TimeoutError:
                        print("Block with products did not appear in time.")
     
                    first_product_link = None
                    for attempt in range(3):
                        first_product_link = page.query_selector("div.product-wrapper a[href*='Mobilniy_telefon']")
                        if first_product_link:
                            break
                        else:
                            page.wait_for_timeout(1500)
                    if first_product_link:
                        href = first_product_link.get_attribute('href')
                        #print("Переход по ссылке:", href)
                        page.goto(href, timeout=15000)
                        page.wait_for_timeout(2000)
                
                    else:
                        print("link to first product not found after retries.")

                except Error as e:
                    print(f"Error visible_inputs[0].press('Enter') {e}")
                    return
                    

                try:
          
                    page.goto(href, timeout=15000)
                    page.wait_for_timeout(2000)

                    try:
                        product_name = page.query_selector("h1.main-title").inner_text().strip()
                        general["product_name"] = product_name      
               
                    except Error as e:
                        print(f"Error getting product name: {e}")
                        product_name = None


                    color = []
                    try:
    
                        page.wait_for_selector("div.series-colors-column", timeout=5000)
                        color_items = page.query_selector_all("div.series-colors-column div.series-item.series-color a")
                        if not color_items:
                            print("No color items found.")
                        for color_link in color_items:
                            color_href = color_link.get_attribute("href")
                            if color_href:

                                color_context = browser.new_context()
                                color_page = color_context.new_page()
                                try:
                                    color_page.goto(color_href, timeout=10000)
                                    color_page.wait_for_selector("h1.main-title", timeout=10000, state="attached")
                                    color_name = color_page.query_selector("h1.main-title").inner_text().strip()
                                    color.append({"name": color_name, "url": color_href})
                                except Error as e:
                                    print(f"Error loading color page {color_href}: {e}")
                                finally:
                                    color_page.close()
                                    color_context.close()
                    except Error as e:
                        print(f"Error extracting colors: {e}")
                        colors = None
      

                    colors = []
                    for color in colors:
                        match = re.search(r'(\w+)\s*\(', color['name'])
                        if match:
                            color_name = match.group(1)
                            colors.append(color_name)
                    print(colors)
                    general["colors"] = colors

                    try:
                        memory_capacity = page.query_selector("div.stuff-series.stuff-series-characteristics.main-stuff-series-block.current-product-series").inner_text().strip()
                        #print(f"memory_capacity: {memory_capacity}")
                    except Error as e:
                        print(f"Error getting product name: {e}")
                        memory_capacity = None

                    manufacturer = None
                    try:
                        chr_blocks = page.query_selector_all("div.br-pr-chr-item")
                        for block in chr_blocks:
                          
                            spans = block.query_selector_all("span")
                            for i in range(len(spans) - 1):
                                key = spans[i].inner_text().strip().lower()
                                value = spans[i + 1].inner_text().strip()
                        
                                if any(word in key for word in ["виробник", "manufacturer", "fabricante", "fabricant", "hersteller", "producente", "производитель"]):
                                    manufacturer = value
                                    break
                            if manufacturer:
                                break
                        #print("Производитель:", manufacturer)
                    except Error as e:
                        print(f"Error getting manufacturer: {e}")
                        manufacturer = None
                    general["manufacturer"] = manufacturer

                    price = None
                    promo_price = None
                    try:
         
                        price_block = page.query_selector("div.br-pr-price.main-price-block")
                        if price_block:
                         
                            old_price_span = price_block.query_selector("div.br-pr-op .price-wrapper span")
                            if old_price_span:
                                price = old_price_span.inner_text().strip().replace(" ", "")
                    
      
                            promo_price_span = price_block.query_selector("div.br-pr-np .price-wrapper span")
                            if promo_price_span:
                                promo_price = promo_price_span.inner_text().strip().replace(" ", "")
                    
                        print(f"Обычная цена: {price}")
                        print(f"Акционная цена: {promo_price}")
                    except Error as e:
                        print(f"Error getting prices: {e}")
                        price = None
                        promo_price = None
                    general["price"] = price
                    general["promotional_price"] = promo_price


                    product_code = None
                    try:
                        product_code = page.query_selector_all("div.br-pr-code.br-code-block")
               
                        if product_code:
                            for code in product_code:
                                code = code.query_selector("div.product-code-num").inner_text().strip()
                               
                            product_code = code
                            print(product_code)
                        else:
                            print("Product code block not found.")
                    except Error as e:
                        print(f"Error getting product code: {e}")
                        product_code = None
                    general["product_code"] = product_code


                    number_of_reviews = None
                    try:
                        reviews_count = page.query_selector("div.main-comments-block.fast-navigation-comments-block a.reviews-count span")
                        if reviews_count:
                            number_of_reviews = reviews_count.inner_text().strip()
                            print(f"number_of_reviews: {number_of_reviews}")
                        else:
                            print("Reviews count not found.")
                    except Error as e:
                        print(f"Error getting product name: {e}")
                        number_of_reviews = None
                    general["number_of_reviews"] = number_of_reviews


                    screen_diagonal = None
                    try:
                        chr_blocks = page.query_selector_all("div.br-pr-chr-item")
                        for block in chr_blocks:
                          
                            spans = block.query_selector_all("span")
                            for i in range(len(spans) - 1):
                                key = spans[i].inner_text().strip().lower()
                                value = spans[i + 1].inner_text().strip()
                        
                                if any(word in key for word in ["діагональ", "диагональ"]):
                                    screen_diagonal = value
                                    break
                            if screen_diagonal:
                                break
                        print("screen_diagonal:", screen_diagonal)
                    except Error as e:
                        print(f"Error getting manufacturer: {e}")
                        screen_diagonal = None
                    general["screen_diagonal"] = screen_diagonal

                    display_resolution  = None
                    try:
                        chr_blocks = page.query_selector_all("div.br-pr-chr-item")
                        for block in chr_blocks:
                          
                            spans = block.query_selector_all("span")
                            for i in range(len(spans) - 1):
                                key = spans[i].inner_text().strip().lower()
                                value = spans[i + 1].inner_text().strip()
                                #print(key, value)
                                if "разреш" in key or "роздільн" in key:
                                    display_resolution  = value
                                    break
                            if display_resolution :
                                break
                        print("display_resolution :", display_resolution )
                    except Error as e:
                        print(f"Error getting manufacturer: {e}")
                        display_resolution  = None
                    general["display_resolution"]  = display_resolution

                    characteristics  = None
                    try:
                        chr_blocks = page.query_selector_all("div.br-pr-chr-item")
                        for block in chr_blocks:
                          
                            spans = block.query_selector_all("span")
                            for i in range(len(spans) - 1):
                                key = spans[i].inner_text().strip().lower()
                                value = spans[i + 1].inner_text().strip()
                                print(key, value)
            
                        #print("characteristics :", characteristics )
                    except Error as e:
                        print(f"Error getting manufacturer: {e}")
                        characteristics  = None
                    general["characteristics"]  = characteristics


                    photo_links = []
                    try:
                        photo_block = page.query_selector('div.main-pictures-block')
                        if photo_block:
                            img_tags = photo_block.query_selector_all('img')
                            for img in img_tags:
                                src = img.get_attribute('src')
                                if src:
                                    photo_links.append(src)
                        print("Ссылки на фото:", photo_links)
                    except Exception as e:
                        print("Ошибка при получении ссылок на фото:", e)
                    general["photo_links"] = photo_links

                    





                except TimeoutError as e:
                        print(f"Doesn`t load page.goto(href, timeout=15000): {e}")
                        product_name = None

            except Error as e:
                print(f"Playwright error page.goto https://brain.com.ua/ukr/: {e}")



    finally:
        if browser:
            try:
                browser.close()
            except Exception:
                pass 
    




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
            photos = photo_links,
            screen_diagonal = screen_diagonal,
            display_resolution = display_resolution,
            status="Done")
          

    except Error as e:
        print(f"Error saving to database: {e}")
        phone = None






def main():

    search_product()

    print("Data extraction completed.")
    
if __name__ == "__main__":
    main()
