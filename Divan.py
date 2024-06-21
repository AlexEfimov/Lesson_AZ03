import time
import csv
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://www.divan.ru/category/divany-i-kresla?types%5B%5D=1&types%5B%5D=54"
driver = webdriver.Firefox()
driver.get(url)

# Ожидание загрузки главной страницы
wait = WebDriverWait(driver, 10)
categories = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.ui-j6Lq6 a')))

# Получаем все ссылки категорий
category_urls = [category.get_attribute('href') for category in categories]

parsed_data = []

# Парсим каждую категорию
for category_url in category_urls:
    driver.get(category_url)
    time.sleep(3)  # Увеличение времени ожидания для полной загрузки страницы

    try:
        products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="product-card"]')))
        for product in products:
            try:
                product_url = product.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                product_name = product.find_element(By.CSS_SELECTOR, 'span[itemprop="name"]').text
                product_price = product.find_element(By.CSS_SELECTOR, 'meta[itemprop="price"]').get_attribute('content')

                parsed_data.append({
                    'name': product_name,
                    'price': product_price,
                    'url': product_url,
                })
            except Exception as e:
                print(f"Произошла ошибка при парсинге продукта: {e}")
                continue
    except Exception as e:
        print(f"Произошла ошибка при парсинге категории: {e}")
        continue

driver.quit()

# Запись данных в CSV файл
with open('products.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['name', 'price', 'url'])
    writer.writeheader()
    writer.writerows(parsed_data)

# Загружаем файл данных как pandas dataframe для дальнейшей обработки
data = pd.read_csv('products.csv')

# Отфильтровываем товары, содержащие слово "диван" в названии (точное соответствие,без учета регистра)
filtered_data = data[data['name'].str.contains("диван", case=False, regex=False)]

# Вычисляем среднюю цену отфильтрованных товаров
average_price = filtered_data['price'].astype(float).mean()
print(f'Средняя цена на диваны: {average_price:.2f} руб.')

# Создание гистограммы цен
plt.figure(figsize=(10, 6))
plt.hist(filtered_data['price'].astype(float), bins=20, color='blue', alpha=0.7)
plt.title('Гистограмма цен на диваны')
plt.xlabel('Цена')
plt.ylabel('Количество')
plt.grid(True)
plt.show()