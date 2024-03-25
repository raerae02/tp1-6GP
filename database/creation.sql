CREATE DATABASE ma_base_de_donnees;

USE ma_base_de_donnees;

CREATE TABLE videos (
    id_video INT AUTO_INCREMENT PRIMARY KEY,
    nom_video VARCHAR(255),
    taille_video INT,
    md5_video VARCHAR(255),
    ordre INT
);

CREATE TABLE video_courant (
    id_courant INT AUTO_INCREMENT PRIMARY KEY,
    id_video INT,
    début_video TIMESTAMP,
    fin_video TIMESTAMP,
    temps_jouer INT,
    FOREIGN KEY (id_video) REFERENCES videos (id_video)
);

CREATE TABLE nb_video_jour (
    id_nb INT AUTO_INCREMENT PRIMARY KEY,
    date_jour DATE,
    id_video INT,
    nb_jouer INT,
    temps_total INT,
    FOREIGN KEY (id_video) REFERENCES videos (id_video)
);
