from flask import Flask, jsonify
from flask_cors import CORS
from waitress import serve
from sqlalchemy import create_engine, select, cast, Numeric
from sqlalchemy.orm import sessionmaker, selectinload
from db_mappers import Researcher, Publication
import requests

app = Flask(__name__)
CORS(app)

engine = create_engine("postgresql+psycopg://admin:admin@database:5432/exam")
Session = sessionmaker(engine)

SCOPUS_ENDPOINT = "http://scopus:3000/publications/{scopus_id}"


@app.get("/publications/<int:researcher_id>")
def get_publications(researcher_id):
    response = []
    with Session() as session:
        researcher = session.scalar(
            select(Researcher)
            .filter_by(id=researcher_id)
            .options(selectinload(Researcher.publications))
        )
        if researcher is not None:
            if researcher.has_publications():
                for publication in researcher.publications:
                    response.append(publication.get_information())
            else:
                scopus_response = requests.get(
                    SCOPUS_ENDPOINT.format(scopus_id=researcher.scopus_id)
                )
                if scopus_response.status_code == 200:
                    publications = scopus_response.json()
                    for pub in publications:
                        scopus_id = int(pub["scopus_id"])
                        publication = session.scalar(
                            select(Publication).where(
                                Publication.scopus_id == cast(scopus_id, Numeric)
                            )
                        )
                        if publication is not None:
                            publication.researchers.append(researcher)
                        else:
                            publication = Publication(
                                scopus_id=int(pub["scopus_id"]),
                                title=pub["title"],
                                year=int(pub["year"]),
                                authors=pub["authors"],
                                type=pub["type"],
                                num_citations=int(pub["num_citations"]),
                                reference=pub["reference"],
                                link=pub["link"],
                                researchers=[researcher],
                            )
                            session.add(publication)
                        response.append(publication.get_information())
                    researcher.set_asked_publication(True)
                    session.commit()
                elif scopus_response.status_code == 204:
                    return {}, 204
                else:
                    return {"error": "Internal Server Error"}, 500
            return jsonify(response), 200
        else:
            return {}, 204


if __name__ == "__main__":
    serve(app, listen="*:3002")
