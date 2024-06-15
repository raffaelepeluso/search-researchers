from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import re

class HtmlParser(ABC):
    @abstractmethod
    def parse(self, html: str) -> None:
        pass
    
    @abstractmethod
    def extract_num_results(self) -> int:
        pass
    
    @abstractmethod
    def extract_information(self) -> list[dict]:
        pass

class ResearcherHtmlParser(HtmlParser):
    __parser: BeautifulSoup
    
    def __init__(self) -> None:
        self.__parser = None
    
    def parse(self, html: str) -> None:
        self.__parser = BeautifulSoup(html, "html.parser")
    
    def extract_num_results(self) -> int:
        try:
            n_results = int(self.__parser.find("div", id="coldx").find("strong").text.split(" ")[0])
        except:
            n_results = 0
        return n_results 
    
    def extract_information(self) -> list[dict]:
        info = []
        researchers_table = self.__parser.find("table", {"class":"risultati"})
        if researchers_table is not None:
            researchers_information = researchers_table.find("tbody")
            for row in researchers_information.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) > 0:
                    info.append({
                        "role": re.sub(r"\s+", " ", cells[0].text.strip()).replace('"',"'"),
                        "surname_name": re.sub(r"\s+", " ", cells[1].text.strip()).replace('"',"'"),
                        "university": re.sub(r"\s+", " ", cells[3].text.strip()).replace('"',"'"),
                        "ssd": re.sub(r"\s+", " ", cells[5].text.strip()).replace('"',"'"),
                        "department": re.sub(r"\s+", " ", cells[7].text.strip()).replace('"',"'")
                    })
        return info