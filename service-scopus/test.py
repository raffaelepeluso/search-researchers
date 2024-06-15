import unittest
from unittest.mock import patch, MagicMock
from app import (
    app,
    _search_author_id,
    _get_author_details,
    _get_author_publications,
    ScopusAPIError,
    NoMatchError,
)


class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @patch("requests.get")
    def test_search_author_id_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {"entry": [{"dc:identifier": "AUTHOR_ID:123456"}]}
        }
        mock_get.return_value = mock_response

        author_id = _search_author_id("John", "Doe", "University")
        self.assertEqual(author_id, "123456")

    @patch("requests.get")
    def test_search_author_id_no_match(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"search-results": {"entry": []}}
        mock_get.return_value = mock_response

        with self.assertRaises(NoMatchError):
            _search_author_id("John", "Doe", "University")

    @patch("requests.get")
    def test_search_author_id_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.assertRaises(ScopusAPIError):
            _search_author_id("John", "Doe", "University")

    @patch("requests.get")
    def test_get_author_details_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "author-retrieval-response": [
                {
                    "h-index": 10,
                    "coredata": {"document-count": 20, "citation-count": 100},
                    "subject-areas": {"subject-area": [{"$": "Computer Science"}]},
                }
            ]
        }
        mock_get.return_value = mock_response

        h_index, n_publications, total_n_citations, topics_of_interest = (
            _get_author_details("123456")
        )
        self.assertEqual(h_index, 10)
        self.assertEqual(n_publications, 20)
        self.assertEqual(total_n_citations, 100)
        self.assertEqual(topics_of_interest, "Computer Science")

    @patch("requests.get")
    def test_get_author_details_no_match(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        with self.assertRaises(NoMatchError):
            _get_author_details("123456")

    @patch("requests.get")
    def test_get_author_details_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.assertRaises(ScopusAPIError):
            _get_author_details("123456")

    @patch("requests.get")
    def test_get_author_publications_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {
                "entry": [
                    {
                        "dc:identifier": "SCOPUS_ID:7891011",
                        "dc:title": "Publication 1",
                        "prism:coverDate": "2023-01-01",
                        "author": [{"authname": "John Doe"}],
                        "prism:aggregationType": "Journal",
                        "citedby-count": 5,
                        "prism:publicationName": "Journal 1",
                        "link": [{"@ref": "scopus", "@href": "https://example.com"}],
                    }
                ],
                "cursor": {"@current": "*", "@next": "next"},
            }
        }
        mock_get.return_value = mock_response

        publications = _get_author_publications("123456")
        self.assertEqual(len(publications), 1)
        self.assertEqual(publications[0]["scopus_id"], "7891011")
        self.assertEqual(publications[0]["title"], "Publication 1")
        self.assertEqual(publications[0]["year"], "2023")
        self.assertEqual(publications[0]["authors"], "John Doe")
        self.assertEqual(publications[0]["type"], "Journal")
        self.assertEqual(publications[0]["num_citations"], 5)
        self.assertEqual(publications[0]["reference"], "Journal 1")
        self.assertEqual(publications[0]["link"], "https://example.com")

    @patch("requests.get")
    def test_get_author_publications_no_match(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "search-results": {
                "entry": [],
                "cursor": {"@current": "*", "@next": "next"},
            }
        }
        mock_get.return_value = mock_response

        publications = _get_author_publications("123456")
        self.assertEqual(publications, [])

    @patch("requests.get")
    def test_get_author_publications_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.assertRaises(ScopusAPIError):
            _get_author_publications("123456")


if __name__ == "__main__":
    unittest.main()
