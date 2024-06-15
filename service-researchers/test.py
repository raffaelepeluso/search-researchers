import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

from app import app, Researcher

class TestResearchers(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = app.test_client()
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        cls.engine = create_engine('sqlite:///:memory:', echo=True)
        cls.session = Session(cls.engine)
        
        Researcher.metadata.create_all(cls.engine)
        
        cls.researchers = [
            {"role":"Associato","surname_name":"CAPUANO Nicola","university":"	SALERNO","ssd":"ING-INF/05","department":"Ingegneria dell'Informazione ed Elettrica e Matematica applicata", "ask":False},
            {"role":"Associato","surname_name":"MOSCATO Francesco","university":"SALERNO","ssd":"ING-INF/05","department":"Ingegneria dell'Informazione ed Elettrica e Matematica applicata","ask":False},
            {"role":"Ricercatore","surname_name":"MOSCATO Stefania","university":"PISA","ssd":"BIO/17","department":"MEDICINA CLINICA E SPERIMENTALE", "ask":False},
            {"role":"Ordinario","surname_name":"VENTO Mario","university":"SALERNO	","ssd":"ING-INF/05","department":"Ingegneria dell'Informazione ed Elettrica e Matematica applicata", "ask":False}
        ]
        
        with cls.engine.begin() as connection:
            connection.execute(
                text("INSERT INTO researcher(role,surname_name,university,ssd,department,asked_publication) values(:role,:surname_name,:university,:ssd,:department,:ask)"),
                cls.researchers
            )
        
    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.engine.dispose()
    
    @patch("app.Session")
    def test_get_researcher(self, mock_session):
        mock_session.return_value= self.session
        
        response = self.client.get("/researchers/info/moscato")
        self.assertEqual(response.status_code,200)
        data = response.get_json()
        self.assertEqual(data["n_matches"],2)
        
        response = self.client.get("/researchers/info/francesco moscato")
        self.assertEqual(response.status_code,200)
        data = response.get_json()
        self.assertEqual(data["n_matches"],1)
        researcher = data["researchers"][0]
        self.assertEqual(researcher["role"], "Associato")
        self.assertEqual(researcher["surname"], "MOSCATO")
        self.assertEqual(researcher["name"], "Francesco")
        self.assertEqual(researcher["university"], "SALERNO")
        self.assertEqual(researcher["ssd"], "ING-INF/05",)
        self.assertEqual(researcher["department"], "Ingegneria dell'Informazione ed Elettrica e Matematica applicata")
        self.assertEqual(researcher["details_link"], "http://localhost:3001/researchers/details/2")
        self.assertEqual(researcher["publications_link"], "http://localhost:3002/publications/2")
        
        
        response = self.client.get("/researchers/info/moscato francesco")
        self.assertEqual(response.status_code,200)
        data = response.get_json()
        self.assertEqual(data["n_matches"],1)
        researcher = data["researchers"][0]
        self.assertEqual(researcher["role"], "Associato")
        self.assertEqual(researcher["surname"], "MOSCATO")
        self.assertEqual(researcher["name"], "Francesco")
        self.assertEqual(researcher["university"], "SALERNO")
        self.assertEqual(researcher["ssd"], "ING-INF/05",)
        self.assertEqual(researcher["department"], "Ingegneria dell'Informazione ed Elettrica e Matematica applicata")
        self.assertEqual(researcher["details_link"], "http://localhost:3001/researchers/details/2")
        self.assertEqual(researcher["publications_link"], "http://localhost:3002/publications/2")
    
        response = self.client.get("/researchers/info/Mario&_Vento")
        self.assertEqual(response.status_code,400)
        data = response.get_json()
        self.assertDictEqual(data, {"error":"Invalid or missing parameter: name"})
        
        response = self.client.get("/researchers/info/valerio")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["n_matches"],0)
    
    @patch("app.Session")
    @patch("requests.get")
    def test_get_detailed_information(self, mock_get, mock_session):
        mock_session.return_value = self.session
        mock_response = MagicMock()
        mock_response.status_code = 200
        return_value = {
                "scopus_id":1234556677,
                "h_index":10,
                "num_citations":10,
                "num_publications":10,
                "topics_of_interest":"Insegnamento"
            }
        mock_response.json.return_value = return_value
        mock_get.return_value = mock_response
        
        response = self.client.get("/researchers/details/2")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["h_index"], 10)
        self.assertEqual(data["n_citations"], 10)
        self.assertEqual(data["n_publications"], 10)
        self.assertEqual(data["topics_of_interest"], "Insegnamento")
        reseacher = self.session.get(Researcher,2)
        self.assertEqual(reseacher.scopus_id, 1234556677)
        self.assertEqual(reseacher.h_index, 10)
        self.assertEqual(reseacher.n_publications, 10)
        self.assertEqual(reseacher.n_citations, 10)
        self.assertEqual(reseacher.topics_of_interest, "Insegnamento")
        
        mock_response.status_code = 204
        response = self.client.get("/researchers/details/1")
        self.assertEqual(response.status_code, 204)
        
        response = self.client.get("/researchers/details/2")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["h_index"], 10)
        self.assertEqual(data["n_citations"], 10)
        self.assertEqual(data["n_publications"], 10)
        self.assertEqual(data["topics_of_interest"], "Insegnamento")
        
        response = self.client.get("/researchers/details/10")
        self.assertEqual(response.status_code, 204)
    
if __name__ == "__main__":
    unittest.main()
