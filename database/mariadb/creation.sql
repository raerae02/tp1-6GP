CREATE TABLE objets (
    id_objet INT AUTO_INCREMENT PRIMARY KEY,
    nom_objet VARCHAR(255),
    local_objet VARCHAR(255),
    is_localisation BOOLEAN
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE videos_objets (
    id_video INT AUTO_INCREMENT PRIMARY KEY,
    id_objet INT,
    nom_video VARCHAR(255),
    taille_video INT,
    md5_video VARCHAR(32), 
    ordre_video INT,
    FOREIGN KEY (id_objet) REFERENCES objets (id_objet)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE videos_par_jour (
    id_jour INT AUTO_INCREMENT PRIMARY KEY,
    date_jour DATE,
    id_video INT,
    id_objet INT,
    nb_jouer INT,
    temps_jouer INT,
    FOREIGN KEY (id_video) REFERENCES videos_objets (id_video),
    FOREIGN KEY (id_objet) REFERENCES objets (id_objet)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE videos_supprimer (
    id_video INT,
    temps_suppression TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_video)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
