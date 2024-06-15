from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column, Numeric
from typing import List, Optional


class Base(DeclarativeBase):
    pass


association_table = Table(
    "publicated",
    Base.metadata,
    Column("researcher", ForeignKey("researcher.id"), primary_key=True),
    Column("publication", ForeignKey("publication.id"), primary_key=True),
)


class Researcher(Base):
    __tablename__ = "researcher"

    id: Mapped[int] = mapped_column(primary_key=True)
    scopus_id: Mapped[Optional[int]] = mapped_column(Numeric)
    surname_name: Mapped[str]
    university: Mapped[str]
    department: Mapped[str]
    role: Mapped[str]
    ssd: Mapped[str]
    h_index: Mapped[Optional[int]]
    n_citations: Mapped[Optional[int]]
    n_publications: Mapped[Optional[int]]
    topics_of_interest: Mapped[Optional[str]]
    asked_publication: Mapped[bool]

    publications: Mapped[List["Publication"]] = relationship(
        secondary=association_table, back_populates="researchers"
    )

    def get_id(self) -> int:
        return self.id

    def get_scopus_id(self) -> int:
        return self.scopus_id

    def get_general_information(self) -> dict:
        surname, name = self.surname_name.rsplit(" ", 1)
        info = {
            "researcher_id": self.id,
            "name": name,
            "surname": surname,
            "university": self.university,
            "department": self.department,
            "role": self.role,
            "ssd": self.ssd,
        }

        return info

    def get_detailed_information(self) -> dict:
        info = {
            "h_index": self.h_index,
            "n_citations": self.n_citations,
            "n_publications": self.n_publications,
            "topics_of_interest": self.topics_of_interest,
        }

        return info

    def set_detailed_information(self, info: dict) -> None:
        self.scopus_id = info["scopus_id"]
        self.h_index = info["h_index"]
        self.n_citations = info["num_citations"]
        self.n_publications = info["num_publications"]
        self.topics_of_interest = info["topics_of_interest"]

    def set_asked_publication(self, asked_publication: bool):
        self.asked_publication = asked_publication

    def has_publications(self) -> bool:
        return self.asked_publication


class Publication(Base):
    __tablename__ = "publication"

    id: Mapped[int] = mapped_column(primary_key=True)
    scopus_id: Mapped[int] = mapped_column(Numeric)
    title: Mapped[str]
    year: Mapped[int]
    authors: Mapped[str]
    type: Mapped[str]
    num_citations: Mapped[int]
    reference: Mapped[str]
    link: Mapped[str]

    researchers: Mapped[List[Researcher]] = relationship(
        secondary=association_table, back_populates="publications"
    )

    def get_information(self) -> dict:
        info = {
            "title": self.title,
            "year": self.year,
            "authors": self.authors,
            "type": self.type,
            "num_citations": self.num_citations,
            "reference": self.reference,
            "link": self.link,
        }
        return info
