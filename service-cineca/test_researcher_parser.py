import unittest
import os

from scraper.html_parser import ResearcherHtmlParser

class TestResearcherHtmlParser(unittest.TestCase):
    
    def setUp(self) -> None:
        with open(os.path.join("test_files","example_search1.html"),"r", encoding='latin-1') as file:
            self.search_multiple_results = file.read()
        
        with open(os.path.join("test_files","example_search2.html"),"r", encoding='latin-1') as file:
            self.search_single_results = file.read()
        
        with open(os.path.join("test_files","example_search3.html"),"r", encoding='latin-1') as file:
            self.search_no_results = file.read()
            
        self.parser = ResearcherHtmlParser()
    
    def test_extract_num_results(self):
        self.parser.parse(self.search_multiple_results)
        n_results = self.parser.extract_num_results()
        self.assertEqual(n_results, 8)
        
        self.parser.parse(self.search_single_results)
        n_results = self.parser.extract_num_results()
        self.assertEqual(n_results, 1)
        
        self.parser.parse(self.search_no_results)
        n_results = self.parser.extract_num_results()
        self.assertEqual(n_results, 0)
    
    def test_extract_information(self):
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
            }]
        self.parser.parse(self.search_multiple_results)
        result = self.parser.extract_information()
        self.assertListEqual(correct_list, result)
        
        correct_list = [
            {
                'role': 'Associato', 
                'surname_name': 'MOSCATO Francesco', 
                'university': 'SALERNO',
                'ssd': 'ING-INF/05', 
                'department': "Ingegneria dell'Informazione ed Elettrica e Matematica applicata"
            }
        ]
        
        self.parser.parse(self.search_single_results)
        result = self.parser.extract_information()
        print(result)
        self.assertListEqual(correct_list, result)
        
        correct_list = []
        
        self.parser.parse(self.search_no_results)
        result = self.parser.extract_information()
        self.assertListEqual(correct_list, result)

if __name__ == '__main__':
    unittest.main()