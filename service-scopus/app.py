from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from waitress import serve

app = Flask(__name__)
CORS(app)

API_KEY = ""
SCOPUS_AUTHOR_SEARCH = "https://api.elsevier.com/content/search/author"
SCOPUS_AUTHOR_DETAILS = "https://api.elsevier.com/content/author/author_id/{author_id}"
SCOPUS_AUTHOR_PUBLICATIONS = "https://api.elsevier.com/content/search/scopus"
HEADERS = {"X-ELS-APIKey": API_KEY, "Accept": "application/json"}


class ScopusAPIError(Exception):
    pass


class NoMatchError(Exception):
    pass


def _search_author_id(name: str, surname: str, university: str) -> int:
    query = f"AUTHFIRST({name}) AND AUTHLASTNAME({surname}) AND AFFIL({university})"
    params = {"query": query}
    response = requests.get(SCOPUS_AUTHOR_SEARCH, headers=HEADERS, params=params)
    if response.status_code != 200:
        raise ScopusAPIError()
    try:
        author_id = response.json()["search-results"]["entry"][0][
            "dc:identifier"
        ].split(":")[1]
    except Exception:
        raise NoMatchError()
    return author_id


def _get_author_details(scopus_author_id: int) -> tuple[int, int, int, list[str]]:
    url = SCOPUS_AUTHOR_DETAILS.format(author_id=scopus_author_id)
    response = requests.get(url, headers=HEADERS, params={"view": "ENHANCED"})
    if response.status_code != 200:
        raise ScopusAPIError()
    try:
        author_details = response.json()
        h_index = author_details["author-retrieval-response"][0]["h-index"]
        n_publications = author_details["author-retrieval-response"][0]["coredata"][
            "document-count"
        ]
        total_n_citations = author_details["author-retrieval-response"][0]["coredata"][
            "citation-count"
        ]
        topics = [
            area["$"]
            for area in author_details["author-retrieval-response"][0]["subject-areas"][
                "subject-area"
            ]
        ]
        topics_of_interest = ";".join(topics)
    except Exception:
        raise NoMatchError()
    return h_index, n_publications, total_n_citations, topics_of_interest


def _get_author_publications(scopus_author_id: int) -> list[dict]:
    publications = []
    cursor = "*"
    params = {
        "query": f"AU-ID({scopus_author_id})",
        "view": "COMPLETE",
        "cursor": cursor,
    }
    more_publications = True
    while more_publications:
        response = requests.get(
            SCOPUS_AUTHOR_PUBLICATIONS, headers=HEADERS, params=params
        )
        if response.status_code != 200:
            raise ScopusAPIError()
        try:
            publications_details = response.json()
            cursor = publications_details["search-results"]["cursor"]["@next"]
            if params["cursor"] != cursor:
                for pub in publications_details["search-results"]["entry"]:
                    publication = {
                        "scopus_id": pub["dc:identifier"].split(":")[-1],
                        "title": pub["dc:title"],
                        "year": pub["prism:coverDate"][:4],
                        "authors": ";".join(
                            [author["authname"] for author in pub["author"]]
                        ),
                        "type": pub.get("prism:aggregationType", "N/A"),
                        "num_citations": pub.get("citedby-count", 0),
                        "reference": pub.get("prism:publicationName", "N/A"),
                        "link": next(
                            (
                                link["@href"]
                                for link in pub.get("link", [])
                                if link.get("@ref") == "scopus"
                            ),
                            "N/A",
                        ),
                    }
                    publications.append(publication)
                params["cursor"] = cursor
            else:
                more_publications = False
        except Exception:
            raise NoMatchError()
    return publications


@app.route("/researchers", methods=["GET"])
def get_researcher():
    if not request.is_json:
        return {"error": "Request must be JSON"}, 415
    body = request.get_json()
    required_fields = ["first_name", "last_name", "affiliation"]
    for field in required_fields:
        if field not in body or not isinstance(body[field], str):
            return {"error": "Invalid or missing parameter"}, 400
    first_name = body["first_name"]
    last_name = body["last_name"]
    affiliation = body["affiliation"]
    try:
        scopus_id = _search_author_id(first_name, last_name, affiliation)
        h_index, n_publications, total_n_citations, topics_of_interest = (
            _get_author_details(scopus_id)
        )
    except ScopusAPIError:
        return {"error": "Internal Server Error"}, 500
    except NoMatchError:
        return {}, 204
    response_data = {
        "scopus_id": scopus_id,
        "h_index": h_index,
        "num_citations": total_n_citations,
        "num_publications": n_publications,
        "topics_of_interest": topics_of_interest,
    }
    return jsonify(response_data), 200


@app.route("/publications/<int:researcher_scopus_id>", methods=["GET"])
def get_publications(researcher_scopus_id):
    try:
        publications = _get_author_publications(researcher_scopus_id)
    except ScopusAPIError:
        return {"error": "Internal Server Error"}, 500
    except NoMatchError:
        return {}, 204
    return jsonify(publications), 200


if __name__ == "__main__":
    serve(app, listen="*:3000")
