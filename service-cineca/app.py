from scraper.search_engine import ReseacherClientSearch
from sqlalchemy import create_engine, text
from string import ascii_lowercase

SEARCH_URL = "https://cercauniversita.mur.gov.it/php5/docenti/vis_docenti.php"
quary = {
    "qualifica":"**",
    "conferma":2,
    "cognome":"",
    "nome":"",
    "radiogroup":"I",
    "genere":"A",
    "universita":"00",
    "facolta":"00",
    "settore":"0000",
    "area":"0000",
    "macro":"0000",
    "settorec":"0000",
    "situazione_al":"0"
}
engine = create_engine("postgresql+psycopg://admin:admin@database:5432/exam", echo=True)

def main() -> None:
    search_client = ReseacherClientSearch(SEARCH_URL)
    for c in ascii_lowercase:
        print(f"Retriving information with letter {c}")
        quary["cognome"] = c
        search_client.search(quary)
        researchers = search_client.get_information()
        
        print("Writing information in database")
        with engine.begin() as connection:
            connection.execute(
                text("INSERT INTO researcher(role,surname_name,university,ssd,department) values(:role,:surname_name,:university,:ssd,:department)"),
                researchers
            )

if __name__ == "__main__":
    main()