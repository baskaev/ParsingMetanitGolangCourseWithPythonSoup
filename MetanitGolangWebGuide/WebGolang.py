import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Базовый URL
base_url = "https://metanit.com/go/web/"

# Список URL-адресов статей
tutorial_urls = links = [
    "1.1.php",
    "1.2.php",
    "1.3.php",
    "1.4.php",
    "1.5.php",
    "2.1.php",
    "2.2.php",
    "3.1.php",
    "3.2.php",
    "3.3.php",
    "3.4.php"
]

# User-Agent для имитации браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Папка для сохранения ресурсов
output_folder = "resourcesWebGo"
os.makedirs(output_folder, exist_ok=True)

# Функция для скачивания ресурсов
def download_resource(url, folder):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            filename = os.path.join(folder, os.path.basename(url))
            with open(filename, 'wb') as file:
                file.write(response.content)
            return filename
    except Exception as e:
        print(f"Ошибка при скачивании ресурса {url}: {e}")
    return None

# Функция для получения HTML-кода страницы
def get_page_html(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Ошибка при загрузке страницы: {response.status_code}")

# Функция для извлечения содержимого статьи и замены путей на полные URL
def extract_article_content(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', class_='item center menC')

    # Заменяем пути изображений на полные URL
    for img in content.find_all('img'):
        img_src = img['src'].strip()
        if not img_src.startswith('/'):
            img_src = '/' + img_src
        img_url = base_url + img_src
        img['src'] = img_url

    # Заменяем пути CSS-файлов на полные URL
    for link in content.find_all('link', rel='stylesheet'):
        css_url = urljoin(base_url, link['href'])
        link['href'] = css_url

    # Удаляем лишние пробелы и символы
    for element in content.find_all(text=True):
        element.replace_with(element.strip())

    return content

# Функция для удаления ненужных блоков
def remove_unwanted_blocks(soup):
    # Удаляем блоки с рекламой и социальными кнопками
    unwanted_selectors = [
        'div[style*="margin-top:23px;margin-left:5px;"]',
        'div.socBlock',
        'div[style*="margin-top:25px;"]',
        'div.commentABl',
        'div.nav'
    ]
    for selector in unwanted_selectors:
        for block in soup.select(selector):
            block.decompose()

# Основная функция
def main():
    output_file = "combined_pageWebGolang.html"

    # Создаем новый HTML-документ
    combined_html = BeautifulSoup("<html><head><title>Combined Articles</title></head><body></body></html>", 'html.parser')

    # Переходим по каждой ссылке и добавляем содержимое статьи в новый документ
    for url in tutorial_urls:
        full_url = base_url + url
        print(f"Обрабатывается статья: {full_url}")
        try:
            article_html = get_page_html(full_url)
            article_content = extract_article_content(article_html, base_url)
            if article_content:
                combined_html.body.append(article_content)
        except Exception as e:
            print(f"Ошибка при обработке статьи {full_url}: {e}")

    # Удаляем ненужные блоки
    remove_unwanted_blocks(combined_html)

    # Сохраняем результат в файл
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(combined_html.prettify())

    print(f"Все статьи объединены и сохранены в файл: {output_file}")

if __name__ == "__main__":
    main()