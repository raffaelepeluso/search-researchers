from scraper.html_parser import HtmlParser, ResearcherHtmlParser
import requests, math
from abc import ABC, abstractmethod

class ClienSearch(ABC):
    _search_url: str
    _results: list[dict]
    _parser: HtmlParser
    
    def __init__(self, search_url: str) -> None:
        self._search_url = search_url
        self._results = []
        self._parser = self.create_parser()
    
    @abstractmethod
    def search(self, quary: str) -> None:
        pass
    
    @abstractmethod
    def create_parser(self) -> HtmlParser:
        pass
    
    def get_information(self) -> list[dict]:
        info = self._results
        self._results = []
        return info

class ReseacherClientSearch(ClienSearch):
    
    def __init__(self, search_url: str) -> None:
        super().__init__(search_url)
    
    def create_parser(self) -> HtmlParser:
        return ResearcherHtmlParser()
    
    def search(self, quary: str) -> None:
        pages = self._fetch_all_pages(quary)
        i = 1
        for page in pages:
            print(f"Parsing page {i}")
            self._parser.parse(page)
            self._results.extend(self._parser.extract_information())
            i = i + 1 
    
    def _fetch_all_pages(self, quary: str) -> list[str]:
        pages = []
        i = 1
        while True:
            print(f"Retriving page {i}")
            quary["pagina"] = i
            response = requests.post(self._search_url, data=quary)
            pages.append(response.text)
            if i == 1:
                self._parser.parse(response.text)
                n_results = self._parser.extract_num_results()
                n_pages = math.ceil(n_results/20)
            if i == n_pages:
                break
            i = i+1
        return pages
            
            