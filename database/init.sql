drop table if exists publicated cascade;
drop table if exists researcher cascade;
drop table if exists publication cascade;

create table researcher(
    id serial primary key,
    scopus_id numeric,
    surname_name varchar not null,
    university varchar not null,
    department varchar not null,
    role varchar not null,
    ssd varchar not null,
    h_index integer,
    n_citations integer,
    n_publications integer,
    topics_of_interest varchar,
    asked_publication boolean not null default FALSE
);

create table publication(
    id serial primary key,
    scopus_id numeric not null,
    title varchar not null,
    year integer not null,
    authors varchar not null,
    type varchar not null,
    num_citations integer not null,
    reference varchar not null,
    link varchar not null
);

create table publicated(
    researcher integer references researcher(id) on update restrict on delete restrict,
    publication integer references publication(id) on update restrict on delete restrict,
    primary key(researcher,publication)
);