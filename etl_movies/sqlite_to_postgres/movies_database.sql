CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT not null,
    file_path TEXT,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
); 

create table if not exists content.genre (
    id uuid primary key,
    name text not null,
    description text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

create table if not exists content.person (
    id uuid primary key,
    full_name text not null,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

create table if not exists content.genre_film_work (
    id uuid primary key,
    genre_id uuid not null,
    film_work_id uuid not null,
    CONSTRAINT genre_id
        FOREIGN KEY (genre_id)
        REFERENCES content.genre (id)
        ON DELETE CASCADE,
    CONSTRAINT film_work_id
        FOREIGN KEY (film_work_id)
        REFERENCES content.film_work (id)
        ON DELETE CASCADE,
    created_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid not null,
    person_id uuid not null,
    CONSTRAINT film_work_id
        FOREIGN KEY (film_work_id)
        REFERENCES content.film_work (id)
        ON DELETE CASCADE,
    CONSTRAINT person_id
        FOREIGN KEY (person_id)
        REFERENCES content.person (id)
        ON DELETE CASCADE,
    role TEXT NOT NULL,
    created_at timestamp with time zone
);

CREATE UNIQUE INDEX film_work_person_role_idx ON content.person_film_work (film_work_id, person_id, role);

CREATE UNIQUE INDEX film_work_genre_idx ON content.genre_film_work (film_work_id, genre_id);

CREATE INDEX ON content.film_work (creation_date, rating);