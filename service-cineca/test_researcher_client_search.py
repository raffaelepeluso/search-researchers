import unittest
from unittest.mock import patch, MagicMock
import os
from scraper.html_parser import ResearcherHtmlParser
from scraper.search_engine import ReseacherClientSearch

class TestResearcherClientSearch(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        with open(os.path.join("test_files","example_search1.html"),"r", encoding='latin-1') as file:
            cls.search_multiple_results = file.read()
        
        with open(os.path.join("test_files","example_search2.html"),"r", encoding='latin-1') as file:
            cls.search_single_results = file.read()
        
        with open(os.path.join("test_files","example_search3.html"),"r", encoding='latin-1') as file:
            cls.search_no_results = file.read()
        
        cls.pages = [cls.search_multiple_results, cls.search_single_results]
        
        cls.client = ReseacherClientSearch("test_url")
    
    @patch("requests.post")
    @patch.object(ResearcherHtmlParser, 'extract_num_results')
    def test_fetch_all_pages(self, mock_parse, mock_post):
        mock_response = MagicMock()
        mock_response.text = "page_content"
        mock_post.return_value = mock_response
        
        mock_parse.return_value = 1
        pages = self.client._fetch_all_pages({"test":"quary"})
        self.assertEqual(len(pages),1)
        
        mock_parse.return_value = 40
        pages = self.client._fetch_all_pages({"test":"quary"})
        self.assertEqual(len(pages),2)
        
        mock_parse.return_value = 41
        pages = self.client._fetch_all_pages({"test":"quary"})
        self.assertEqual(len(pages),3)

    @patch.object(ReseacherClientSearch, "_fetch_all_pages")
    def test_search(self, mock_pages):
        correct_list = [
            {
                'role': 'Ordinario', 
                'surname_name': 'CAPUANO Alessandra', 
                'university': "ROMA 'La Sapienza'",
                'ssd': 'ICAR/14', 
                'department': 'Architettura e Progetto'
            }, 
            {
                'role': 'Ordinario', 
                'surname_name': 'CAPUANO Annalisa', 
                'university': "CAMPANIA - 'L. VANVITELLI'", 
                'ssd': 'BIO/14', 
                'department': 'MEDICINA SPERIMENTALE'
            },
            {
                'role': 'Associato', 
                'surname_name': 'CAPUANO Cristina', 
                'university': 'UniCamillus - Saint Camillus International U', 
                'ssd': 'MED/04', 
                'department': 'Facoltà dipartimentale di Medicina'
            }, 
            {
                'role': 'Ricercatore a t.d. - t.pieno (art. 24 c.3-b L. 240/10)', 
                'surname_name': 'CAPUANO Laura', 
                'university': 'ROMA TRE', 'ssd': 'MAT/02', 
                'department': 'MATEMATICA E FISICA'
            }, 
            {
                'role': 'Associato',
                'surname_name': 'CAPUANO Nicola',
                'university': 'SALERNO',
                'ssd': 'ING-INF/05',
                'department': "Ingegneria dell'Informazione ed Elettrica e Matematica applicata"
            }, 
            {
                'role': 'Associato confermato',
                'surname_name': 'CAPUANO Paolo',
                'university': 'SALERNO', 
                'ssd': 'GEO/10',
                'department': "Fisica 'E.R. Caianiello'"
             }, 
            {    
                'role': 'Ricercatore a t.d. - t.defin. (art. 24 c.3-a L. 240/10)', 
                'surname_name': 'CAPUANO Rosamaria',
                'university': "ROMA 'Tor Vergata'",
                'ssd': 'ING-INF/01', 
                'department': 'INGEGNERIA ELETTRONICA'}, 
            {
                'role': 'Associato', 
                'surname_name': 'CAPUANO Valeria', 
                'university': "'Parthenope' di NAPOLI",
                'ssd': 'IUS/14', 
                'department': 'STUDI AZIENDALI ED ECONOMICI'
            },
            {
                'role': 'Associato', 
                'surname_name': 'MOSCATO Francesco', 
                'university': 'SALERNO',
                'ssd': 'ING-INF/05', 
                'department': "Ingegneria dell'Informazione ed Elettrica e Matematica applicata"
            }
            ]
        mock_pages.return_value = self.pages
        
        self.client.search("test_quary")
        result = self.client.get_information()
        self.assertEqual(result, correct_list)
        
        
        
        
if __name__ == "__main__":
    unittest.main()