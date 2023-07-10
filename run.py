import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re

load_dotenv()


class QuoteScraper:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.session = requests.Session()
        self.session.proxies = {"http//": self.proxy, "https//": self.proxy}

    def scrape_quotes(self, input_url, output_file):
        response = self.session.get(input_url)
        final_result_data = []

        while True:
            data, link = self._get_json_from_page(response)
            if link is None:
                break
            link = input_url + "/".join(link.split("/")[2:])
            response = self.session.get(link)
            final_result_data.extend(data)


        self._save_quotes(final_result_data, output_file)

    def _get_json_from_page(self, response):
        soup = BeautifulSoup(response.content, "html.parser")
        script_tag = soup.find('script', string=re.compile(r'var data = (\[.*?\]);', re.DOTALL))
        match = re.search(r'var data = (\[.*?\]);', script_tag.text, re.DOTALL)
        json_str = match.group(1)
        json_obj = json.loads(json_str)

        next_li = soup.find('li', class_='next')
        if next_li is not None:
            next_link = next_li.find('a')
            next_page_url = next_link['href']
        else:
            next_page_url = None

        data = []
        for i in json_obj:
            text = i['text'].replace('“', '').replace('”', '')

            author = i['author']['name'].replace('“', '').replace('”', '')
            tags = i['tags']

            new_quote = {
                'text': text,
                'by': author,
                'tags': tags
            }
            data.append(new_quote)

        return data, next_page_url

    def _save_quotes(self, quotes, output_file):
        with open(output_file, "w", encoding="utf-8") as json_file:
            for quote in quotes:
                json_file.write(json.dumps(quote,ensure_ascii=False) + "\n",)


if __name__ == "__main__":
    proxy = os.getenv("PROXY")
    input_url = os.getenv("INPUT_URL")
    output_file = os.getenv("OUTPUT_FILE", "output.jsonl")

    scraper = QuoteScraper(proxy)
    scraper.scrape_quotes(input_url, output_file)
