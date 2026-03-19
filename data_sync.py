from mongo_manager import get_mongo_client
from neo4j_manager import get_neo4j_driver

def migrate_mongo_to_neo4j():
    mongo_client = get_mongo_client()
    db = mongo_client.entertainment
    neo4j_driver = get_neo4j_driver()

    # 1. Get the movies from MongoDB 
    films = list(db.films.find({}))

    with neo4j_driver.session() as session:
        for movie in films:
            # Get the different attributes
            m_id = str(movie.get('_id'))
            m_title = movie.get('title') or movie.get('Title') or "Untitled"
            m_year = movie.get('year', 0)
            m_votes = movie.get('Votes', 0)
            m_rating = movie.get('rating', "N/A")
            m_revenue = movie.get('Revenue (Millions)', 0)
            m_director = movie.get('Director', "Unknown")

            # --- 2. Building movie nodes ---
            session.run("""
                MERGE (f:Film {id: $id})
                SET f.title = $title, f.year = $year, f.votes = $votes, 
                    f.revenue = $revenue, f.rating = $rating, f.director = $director
            """, id=m_id, title=m_title, year=m_year, 
                 votes=m_votes, revenue=m_revenue, 
                 rating=m_rating, director=m_director)

            # --- 3. Building actor nodes and relations ---
            raw_actors = movie.get('Actors', "")
            if raw_actors:
                # Cleaning strings to get a list
                actors_list = [a.strip() for a in raw_actors.split(',')]
                
                for actor_name in actors_list:
                    session.run("""
                        MERGE (a:Actor {name: $name})
                        WITH a
                        MATCH (f:Film {id: $id})
                        MERGE (a)-[:A_JOUE]->(f)
                    """, name=actor_name, id=m_id)
            
            # --- 4. Building the director nodes ---
            session.run("""
                MERGE (d:Realisateur {name: $name})
                WITH d
                MATCH (f:Film {id: $id})
                MERGE (d)-[:A_REALISE]->(f)
            """, name=m_director, id=m_id)

    print("✅ Migration terminée avec succès !")