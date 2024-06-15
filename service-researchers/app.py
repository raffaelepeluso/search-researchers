from flask import Flask, jsonify
from flask_cors import CORS
from waitress import serve
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from db_mappers import Researcher
import requests, re, os

SCOPUS_ENDPOINT = "http://scopus:3000/researchers"
LINK_DETAILED_INFORMATION = "http://localhost:3001/researchers/details/{}"
LINK_PUBLCIATION = "http://localhost:3002/publications/{}"

app = Flask(__name__)
CORS(app)

engine = create_engine("postgresql+psycopg://admin:admin@database:5432/exam")
Session = sessionmaker(engine)

@app.get("/researchers/info/<quary>")
def get_researchers(quary: str):
    if re.fullmatch(r'[A-Za-z]+( [A-Za-z]+)*', quary):
        response = {"researchers":[]}
        parts = quary.split(" ")
        name = parts[-1]
        surname = " ".join(parts[:-1])
        with Session() as session:
            result = session.scalars(
                select(Researcher)
                .where(Researcher.surname_name.ilike(f"%{name}%") & Researcher.surname_name.ilike(f"%{surname}%"))
            ).all()
            response["n_matches"] = len(result)
            for researcher in result:
                researcher_info = researcher.get_general_information()
                researcher_info["details_link"] = LINK_DETAILED_INFORMATION.format(researcher.get_id())
                researcher_info["publications_link"] = LINK_PUBLCIATION.format(researcher.get_id())
                response["researchers"].append(researcher_info)
        
        return jsonify(response), 200
    else:
        return {"error":"Invalid or missing parameter: name"}, 400

@app.get("/researchers/details/<int:researcher_id>")
def get_detailed_information(researcher_id: int):
    with Session() as session:
        researcher = session.get(Researcher, researcher_id)
        if researcher is not None:
            if researcher.get_scopus_id() is None:
                r_info = researcher.get_general_information()
                quary = {
                    "first_name": r_info["name"],
                    "last_name": r_info["surname"],
                    "affiliation": r_info["university"]
                }
                response = requests.get(SCOPUS_ENDPOINT, json=quary)
                if response.status_code == 200:
                    info = response.json()
                    researcher.set_detailed_information(info)
                    session.commit()
                elif response.status_code == 204:
                    return {}, 204
            
            info = researcher.get_detailed_information()
            
            return jsonify(info), 200
        else:
            return {}, 204
    
if __name__ == "__main__":
    serve(app, listen="*:3001")