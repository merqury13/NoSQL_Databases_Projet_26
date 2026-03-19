from mongo_manager import get_mongo_client
from neo4j_manager import get_neo4j_driver

def migrate_mongo_to_neo4j():
    mongo_client = get_mongo_client()
    db = mongo_client.entertainment
    neo4j_driver = get_neo4j_driver()

    # 1. Récupérer les films de MongoDB
    films = list(db.films.find({}))

    with neo4j_driver.session() as session:
        for movie in films:
            # --- CRÉATION DU NŒUD FILM ---
            # On respecte les champs demandés : id, title, year, Votes, Revenue, rating, director [cite: 84]
            session.run("""
                MERGE (f:Film {id: $id})
                SET f.title = $title, f.year = $year, f.votes = $votes, 
                    f.revenue = $revenue, f.rating = $rating, f.director = $director
            """, id=str(movie['_id']), title=movie['title'], year=movie['year'], 
                 votes=movie['Votes'], revenue=movie.get('Revenue (Millions)', 0), 
                 rating=movie['rating'], director=movie['Director'])

            # --- CRÉATION DES ACTEURS ET RELATIONS ---
            # Le champ Actors est souvent une string séparée par des virgules 
            actors_list = [a.strip() for a in movie['Actors'].split(',')]
            for actor_name in actors_list:
                session.run("""
                    MERGE (a:Actor {name: $name})
                    WITH a
                    MATCH (f:Film {id: $id})
                    MERGE (a)-[:A_JOUE]->(f)
                """, name=actor_name, id=str(movie['_id']))

    print("✅ Migration terminée avec succès !")