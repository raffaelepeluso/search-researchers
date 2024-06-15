import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from app import app, Researcher, Publication
from db_mappers import Base


class TestPublications(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = app.test_client()
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        cls.engine = create_engine("sqlite:///:memory:", echo=True)
        cls.session = Session(cls.engine)

        Base.metadata.create_all(cls.engine)

        researchers = [
            Researcher(
                id=1,
                role="Associato",
                surname_name="CAPUANO Nicola",
                university="SALERNO",
                department="Ingegneria dell'Informazione ed Elettrica e Matematica applicata",
                ssd="ING-INF/05",
                scopus_id=123456,
                asked_publication=False,
            ),
            Researcher(
                id=2,
                role="Associato",
                surname_name="MOSCATO Francesco",
                university="SALERNO",
                department="Ingegneria dell'Informazione ed Elettrica e Matematica applicata",
                ssd="ING-INF/05",
                scopus_id=654321,
                asked_publication=True,
            ),
            Researcher(
                id=3,
                role="Associato",
                surname_name="VENTO Mario",
                university="SALERNO",
                department="Ingegneria dell'Informazione ed Elettrica e Matematica applicata",
                ssd="ING-INF/05",
                scopus_id=348951,
                asked_publication=False,
            ),
            Researcher(
                id=4,
                role="Associato",
                surname_name="TORTORELLA Francesco",
                university="SALERNO",
                department="Ingegneria dell'Informazione ed Elettrica e Matematica applicata",
                ssd="ING-INF/05",
                scopus_id=982371,
                asked_publication=False,
            ),
        ]

        researchers[1].publications.append(
            Publication(
                scopus_id=1,
                title="Title 1",
                year=2020,
                authors="Author 1",
                type="Journal",
                num_citations=5,
                reference="Reference 1",
                link="http://link1.com",
            )
        )

        cls.session.add_all(researchers)
        cls.session.commit()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.engine.dispose()

    @patch("app.Session")
    @patch("requests.get")
    def test_get_publications(self, mock_get, mock_session):
        mock_session.return_value = self.session

        # case 1: researcher with publication in database
        response = self.client.get("/publications/2")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Title 1")
        self.assertEqual(data[0]["year"], 2020)
        self.assertEqual(data[0]["authors"], "Author 1")
        self.assertEqual(data[0]["type"], "Journal")
        self.assertEqual(data[0]["num_citations"], 5)
        self.assertEqual(data[0]["reference"], "Reference 1")
        self.assertEqual(data[0]["link"], "http://link1.com")

        # case 2: researcher with publication not in database but available in scopus
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "scopus_id": 2,
                "title": "Title 2",
                "year": 2021,
                "authors": "Author 2",
                "type": "Conference",
                "num_citations": 10,
                "reference": "Reference 2",
                "link": "http://link2.com",
            }
        ]
        mock_get.return_value = mock_response

        response = self.client.get("/publications/1")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Title 2")
        self.assertEqual(data[0]["year"], 2021)
        self.assertEqual(data[0]["authors"], "Author 2")
        self.assertEqual(data[0]["type"], "Conference")
        self.assertEqual(data[0]["num_citations"], 10)
        self.assertEqual(data[0]["reference"], "Reference 2")
        self.assertEqual(data[0]["link"], "http://link2.com")

        # check database update
        added_publication = self.session.get(Publication, 2)
        self.assertEqual(added_publication.title, "Title 2")
        self.assertEqual(added_publication.year, 2021)
        self.assertEqual(added_publication.authors, "Author 2")
        self.assertEqual(added_publication.type, "Conference")
        self.assertEqual(added_publication.num_citations, 10)
        self.assertEqual(added_publication.reference, "Reference 2")
        self.assertEqual(added_publication.link, "http://link2.com")
        self.assertEqual(added_publication.researchers[0].id, 1)
        modified_researcher = self.session.get(Researcher, 1)
        self.assertEqual(modified_researcher.asked_publication, True)

        # case 3: researcher with publication already in database and available in scopus
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "scopus_id": 2,
                "title": "Title 2",
                "year": 2021,
                "authors": "Author 2",
                "type": "Conference",
                "num_citations": 10,
                "reference": "Reference 2",
                "link": "http://link2.com",
            }
        ]
        mock_get.return_value = mock_response

        response = self.client.get("/publications/3")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Title 2")
        self.assertEqual(data[0]["year"], 2021)
        self.assertEqual(data[0]["authors"], "Author 2")
        self.assertEqual(data[0]["type"], "Conference")
        self.assertEqual(data[0]["num_citations"], 10)
        self.assertEqual(data[0]["reference"], "Reference 2")
        self.assertEqual(data[0]["link"], "http://link2.com")

        # check database update
        existed_publication = self.session.get(Publication, 2)
        self.assertEqual(existed_publication.researchers[1].id, 3)
        modified_researcher = self.session.get(Researcher, 3)
        self.assertEqual(modified_researcher.asked_publication, True)

        # case 3: researcher not found
        response = self.client.get("/publications/999")
        self.assertEqual(response.status_code, 204)

        # case 4: publications not found
        mock_response.status_code = 204
        mock_get.return_value = mock_response

        response = self.client.get("/publications/4")
        self.assertEqual(response.status_code, 204)

        # case 5: scopus error
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        response = self.client.get("/publications/4")
        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
