from urllib.parse import urljoin

import requests
import mysql.connector

from bs4 import BeautifulSoup

main_url = 'https://www.icd10data.com/ICD10CM/Codes/'


mydb = mysql.connector.connect(
    host='192.168.208.2',
    user='user',
    password='password',
    database='pharmacy'
)
my_cursor = mydb.cursor()

my_cursor.execute(
    "CREATE TABLE disease "
    "(pk INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
    "group_code VARCHAR(255), "
    "group_desc VARCHAR(255), "
    "code VARCHAR(5), "
    "code_desc VARCHAR(255))"
)


def get_request(url: str) -> requests:
    response = requests.get(url)
    return response


def save_in_db(response: requests, main_links: dict) -> None:
    soup = BeautifulSoup(response.content, 'html.parser')
    ul_object = soup.find('ul', class_='i51')
    lis = ul_object.find_all('li')
    multiple_data = []
    for li in lis:
        for key, value in main_links.items():
            if key[0] == li.text.strip()[0] or li.text.strip()[0] == key[4]:
                multiple_data.append((key, value, li.text.strip()[:3], li.text.strip()[5:]))
                print(
                    f"Group code: {key}\n"
                    f"Group description: {value}\n"
                    f"Code: {li.text.strip()[:3]}\n"
                    f"Code description: {li.text.strip()[5:]}\n"
                )
    sql = "INSERT INTO disease (group_code, group_desc, code, code_desc) VALUES (%s, %s, %s, %s)"
    my_cursor.executemany(sql, multiple_data)
    mydb.commit()


def get_main_links(page: requests) -> None:
    soup = BeautifulSoup(page.content, 'html.parser')
    links = soup.find_all('a', class_='identifier')
    div_content = soup.find('div', class_='body-content')
    ul_object = div_content.find('ul')
    lis = ul_object.find_all('li')
    main_links = {li.text.strip()[:7]: li.text.strip()[9:] for li in lis}
    for link in links[22:]:
        response = get_request(urljoin(main_url, link.get('href')))
        save_in_db(response, main_links)


def main() -> None:
    response = get_request(main_url)
    get_main_links(response)


if __name__ == '__main__':
    main()
