import re

from invicta.items import InvictaItem
from scrapy.cmdline import execute
from lxml.html import fromstring
from invicta import db_config
from typing import Iterable
from scrapy import Request
import pymysql
import scrapy
import json
import html


def get_store_name(store_dict: dict) -> str:
    store_name = store_dict.get('name', 'N/A')
    return store_name if store_name not in ['', ' '] else 'N/A'


def get_city(store_dict: dict) -> str:
    city = store_dict.get('city', 'N/A')
    return city if city not in ['', ' '] else 'N/A'


def get_url(store_dict: dict) -> str:
    url = store_dict.get('websiteurl', 'N/A')
    return url if url not in ['', ' '] else 'N/A'


def get_store_no(store_dict: dict) -> str:
    store_no = store_dict.get('id', 'N/A')
    return store_no if store_no not in ['', ' '] else 'N/A'


def get_street(store_dict: dict) -> str:
    street = store_dict.get('address', 'N/A')
    return street if street not in ['', ' '] else 'N/A'


# def get_zipcode(store_dict: dict) -> str:
#     zip_code = store_dict.get('address', 'N/A').split()[-1]
#     return zip_code if zip_code not in ['', ' '] else 'N/A'

def get_zipcode(store_dict: dict) -> str:
    address = store_dict.get('address', '')  # Extract 'address' from the dictionary
    zipcode_regex = r"\b\d{5}(?:-\d{4})?\b"  # Define regex for matching ZIP codes
    match = re.search(zipcode_regex, address)  # Search for the ZIP code in the address
    return match.group(0) if match else 'N/A'  # Return the ZIP code if found, otherwise return "N/A"


def get_latitude(store_dict: dict) -> str:
    latitude = store_dict.get('lat', 'N/A')
    return latitude if latitude not in ['', ' '] else 'N/A'


def get_longitude(store_dict: dict) -> str:
    longitude = store_dict.get('lng', 'N/A')
    return longitude if longitude not in ['', ' '] else 'N/A'


def get_phone(store_dict: dict) -> str:
    phone = store_dict.get('telephone', 'N/A').replace('.', '-').replace(')', '-').replace('(', '')
    return phone if phone not in ['', ' '] else 'N/A'


def get_direction_url(street: str, city: str, state: str, zipcode: str) -> str:
    # base_url = 'https://www.google.com/maps/dir/Current+Location/401+Biscayne+Blvd+Suite+N133+Miami,+Miami,+FL,+33132,+USA/'
    street_only = "+".join(street.split()[:-2])
    city = city.replace(' ', '+') if city != 'N/A' else ''
    state = state if state != 'N/A' else ''
    zipcode = zipcode if zipcode != 'N/A' else ''
    direction_url = f'https://www.google.com/maps/dir/Current+Location/{street_only}+{city},+{state},+{zipcode},+USA/'
    return direction_url if direction_url not in ['', ' '] else 'N/A'


# def get_state(store_dict: dict) -> str:
#     state = store_dict.get('address', 'N/A').split()[-2].replace(',', '')
#     return state if state not in ['', ' '] else 'N/A'

def get_state(store_dict: dict) -> str:
    address = store_dict.get('address', '')  # Extract 'address' from the dictionary
    state_regex = r"\b([A-Z]{2})\s\d{5}(?:-\d{4})?\b"  # Define regex for matching state abbreviations
    match = re.search(state_regex, address)  # Search for the state in the address
    return match.group(1) if match else 'N/A'  # Return the state if found, otherwise return "N/A"


class InvictaWatchSpider(scrapy.Spider):
    name = "invicta_watch"

    def __init__(self, ):
        """Initialize database connection and set file paths."""
        super().__init__()
        self.client = pymysql.connect(host=db_config.db_host, user=db_config.db_user, password=db_config.db_password, database=db_config.db_name, autocommit=True)
        self.cursor = self.client.cursor()  # Create a cursor object to interact with the database

        # self.page_save_path = rf'C:\Project Files Live (using Scrapy)\storeLocator\{self.today_date_time}\{self.name}'

    def start_requests(self) -> Iterable[Request]:
        """Generates initial requests with cookies and headers."""
        cookies = {
            'client_location': '%7B%22country%22%3A%22IN%22%2C%22continent%22%3A%22AS%22%2C%22city%22%3A%22%22%2C%22state%22%3A%22%22%7D',
            'nlbi_552287': 'XH90dsXF3lM9Yj1m9qKbUAAAAADzq3Jx4uNoLlxZOgbjSR7S',
            'visid_incap_552287': 'Kj5YtGbTTNm1upxYaLQvrc0ZSGcAAAAAQUIPAAAAAAAtEbuoBGV3OYYq5o7IQTO/',
            'incap_ses_1559_552287': 'yfu+Kh7ezkXtR1ALbK6iFc0ZSGcAAAAAkHr7wh7jCDJpwZfX/Mhg6Q==',
            'visid_incap_552294': '6GL179VMSbayq08Tks5jzNIZSGcAAAAAQUIPAAAAAACt+2fBa70VIsT6UwifMoiX',
            'incap_ses_49_552294': 'o2wtK0RXqV/oV0fTaRWuANIZSGcAAAAAC2FC++DCmXlei4GLW4lYsA==',
            '_ga': 'GA1.2.663596807.1732778351',
            '_gid': 'GA1.2.272175419.1732778351',
            '_fbp': 'fb.1.1732778351471.679575561688910569',
            'ticker%20top-menu-collection-ticker%20header-ticker%20hidden-xs%20leavetickerMargin': '-114.75',
            'incap_ses_708_552287': 'bbexG4AnsTLF5FLxclLTCdsZSGcAAAAAvjMfIAoNeFX8maBs2nrf7w==',
            'nlbi_552294': 'XvkFQ1pC5koZ/3Msva+TUQAAAADBAaHPsaK8m3g5yAMJGdQf',
            'cookie-policy': '1',
            '_ga_VZ2P4VTB81': 'GS1.2.1732778351.1.1.1732778537.60.0.0',
            'incap_ses_1405_552294': '8MrTCz/nJWHTn6w+P5B/E/o2SGcAAAAAP1yYvHU3j0B/O+tKhfPHQg==',
            'incap_ses_1331_552294': '0fJIB2wRAQSkipfxpal4Evs2SGcAAAAAGza+4qToQLaukteevNvDhw==',
            'incap_ses_1329_552294': 'ul9yJSv4m3Kot1RWpo5xEuNISGcAAAAAUkBrA1NXcdwn8dYFVKpRjA==',
            'incap_ses_1324_552294': 'uw7bIvahc2DxnysbLctfEmhJSGcAAAAAxeZYGjoG1LmhohVSQTMW6Q==',
            'ticker%20top-menu-collection-ticker%20header-ticker%20hidden-xstickerMargin': '-187.25',
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://www.invictawatch.com/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        url = 'https://www.invictawatch.com/stores'

        yield scrapy.Request(url=url, cookies=cookies, headers=headers,
                             dont_filter=True)

    def parse(self, response):
        html_text: str = response.text

        parsed_html: str = fromstring(html_text)  # Parse the HTML
        encoded_string: str = parsed_html.xpath('//stores-map/attribute::*[name()=":markers"]')[0]
        decoded_string: str = html.unescape(encoded_string)
        print(decoded_string)

        stores_list: list = json.loads(decoded_string)

        for store_dict in stores_list:
            if store_dict['country'] == 'United States':
                item = InvictaItem()
                item['name'] = get_store_name(store_dict)
                item['url'] = get_url(store_dict)
                item['store_no'] = get_store_no(store_dict)
                street = get_street(store_dict)
                state = get_state(store_dict)
                zipcode = get_zipcode(store_dict)
                city = get_city(store_dict)
                item['city'] = city
                item['street'] = street
                item['state'] = state
                item['zip_code'] = zipcode
                item['latitude'] = get_latitude(store_dict)
                item['longitude'] = get_longitude(store_dict)
                item['phone'] = get_phone(store_dict)
                item['open_hours'] = 'N/A'
                item['status'] = 'N/A'
                item['direction_url'] = get_direction_url(street=street, state=state, zipcode=zipcode, city=city)
                item['updated_date'] = db_config.delivery_date
                item['provider'] = 'Invicta'
                item['category'] = 'Apparel'
                item['county'] = 'N/A'
                item['country'] = 'United States'
                print('item', item)
                print('*' * 50)
                yield item
            print('-' * 100)


if __name__ == '__main__':
    execute(f'scrapy crawl {InvictaWatchSpider.name}'.split())
