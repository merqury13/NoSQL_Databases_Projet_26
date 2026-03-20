import streamlit as st
import pandas as pd
from neo4j_manager import run_query
from streamlit_agraph import agraph, Node, Edge, Config

st.header("Relations and graphs with Neo4j")

#Query to count number of nodes
cypher_count = "MATCH (n) RETURN count(n) AS total"
data_neo = run_query(cypher_count)

if data_neo:
    total_nodes = data_neo[0]['total']
    st.write(f"Total numeber of nodes : **{total_nodes}**")

    st.subheader("14. Which actor has appeared in the most films?")
    query_14 = """
    MATCH (a:Actor)-[:A_JOUE]->(f:Film)
    RETURN a.name AS actor_name, count(f) AS film_count
    ORDER BY film_count DESC
    LIMIT 1
    """
    # Exécution (exemple avec une fonction fictive run_query)
    result_14 = run_query(query_14)

    if result_14:
        actor = result_14[0]
        st.success(f"The actor with the most appearances is **{actor['actor_name']}** with **{actor['film_count']}** films.")
    else:
        st.warning("No actor found with the current query.")

    #################################################################################################################

    st.subheader("15. Which actors have appeared in films in which the actress Anne Hathaway has also appeared?")
    query_15 = """
    MATCH (anne:Actor {name: "Anne Hathaway"})-[:A_JOUE]->(f:Film)<-[:A_JOUE]-(coActor:Actor)
    WHERE coActor.name <> "Anne Hathaway"
    RETURN DISTINCT coActor.name AS co_actor
    ORDER BY co_actor ASC
    """
    result_15 = run_query(query_15)

    if result_15:
        co_actors = [record['co_actor'] for record in result_15]
        st.write(f"Actors who worked with Anne Hathaway: {', '.join(co_actors)}")
    else:
        st.info("No co-actors found for Anne Hathaway in the database.")
    #################################################################################################################

    st.subheader("16. Which actor has appeared in films with the highest total box office takings?")
    query_16 = """
    MATCH (a:Actor)-[:A_JOUE]->(f:Film)
    WHERE f.revenue IS NOT NULL 
    AND f.revenue <> "" 
    AND f.revenue <> "unrated"
    // On force la conversion en flottant pour chaque film avant de sommer
    WITH a, toFloat(f.revenue) AS rev_val
    RETURN a.name AS actor_name, sum(rev_val) AS total_revenue
    ORDER BY total_revenue DESC
    LIMIT 1
    """

    result_16 = run_query(query_16)

    if result_16:
        res = result_16[0]
        st.metric(
            label=f"🏆 {res['actor_name']}", 
            value=f"{res['total_revenue']:.2f} M$"
        )
    else:
        st.warning("No revenue data found for actors.")

    #################################################################################################################

    st.subheader("17. What is the average number of votes?")
    query_17 = """
    MATCH (f:Film)
    WHERE f.votes IS NOT NULL AND f.votes <> ""
    WITH toInteger(f.votes) AS vote_val
    RETURN avg(vote_val) AS average_votes
    """

    result_17 = run_query(query_17)

    if result_17 and result_17[0]['average_votes'] is not None:
        avg_votes = result_17[0]['average_votes']
        # Affichage avec séparateur de milliers pour plus de lisibilité
        st.info(f"The average number of votes per film is **{avg_votes:,.0f}**")
    else:
        st.warning("No voting data found in the database.")
    #################################################################################################################
    st.subheader("18. Which genre is most represented in the database?")
    query_18 = """
    MATCH (f:Film)-[:HAS_GENRE]->(g:Genre)
    RETURN g.name AS genre_name, count(f) AS film_count
    ORDER BY film_count DESC
    LIMIT 1
    """

    result_18 = run_query(query_18)

    if result_18:
        genre_data = result_18[0]
        st.success(f"The most represented genre is **{genre_data['genre_name']}** with **{genre_data['film_count']}** films.")
    else:
        st.warning("No genre relationships found. Did you re-run the migration?")
    #################################################################################################################
    st.subheader("19. Which films have the actors who starred alongside you also appeared in?")
    my_name = "Oscar SALOMON" 

    query_19 = f"""
    MATCH (me:Actors {{name: "{my_name}"}})-[:A_JOUE]->(f1:Film)<-[:A_JOUE]-(coActor:Actor)
    MATCH (coActor)-[:A_JOUE]->(otherFilm:Film)
    WHERE otherFilm <> f1
    RETURN DISTINCT otherFilm.title AS title, coActor.name AS actor_name
    ORDER BY title ASC
    """

    result_19 = run_query(query_19)

    if result_19:
        st.write(f"Films involving actors who worked with **{my_name}**:")
        for row in result_19:
            st.write(f"- **{row['title']}** (featuring {row['actor_name']})")
    else:
        st.info("No common films found. The co actors have only played in this movie, from the list in the DB.")

    #################################################################################################################

    st.subheader("20. Which director has worked with the most different actors?")
    #We link directors to films, and then films to actors, in order to count the number of unique actors per director.
    query_20 = """
    MATCH (d:Realisateur)-[:A_REALISE]->(f:Film)<-[:A_JOUE]-(a:Actor)
    RETURN d.name AS director_name, count(DISTINCT a) AS actor_count
    ORDER BY actor_count DESC
    LIMIT 1
    """

    result_20 = run_query(query_20)

    if result_20:
        data = result_20[0]
        st.success(f"The director who worked with the most diverse actors is **{data['director_name']}** with **{data['actor_count']}** different actors.")
    else:
        st.warning("No data found for directors and actors.")
    #################################################################################################################
    st.subheader("21. Which films are the most ‘connected’, i.e. those that share the most actors with other films?")
    #A film is considered to be ‘connected’ if it shares actors with other films. We therefore look for the films that have the most ‘neighbours’ via their actors.
    query_21 = """
    MATCH (f1:Film)<-[:A_JOUE]-(a:Actor)-[:A_JOUE]->(f2:Film)
    WHERE f1 <> f2
    RETURN f1.title AS title, count(DISTINCT f2) AS connections
    ORDER BY connections DESC
    LIMIT 5
    """

    result_21 = run_query(query_21)

    if result_21:
        st.write("Top 5 most connected films:")
        for row in result_21:
            st.write(f"- **{row['title']}** : connected to {row['connections']} other films.")
    else:
        st.info("No connections found between films.")
    #################################################################################################################
    st.subheader("22. Find the 5 actors who have worked with the most different directors.")
    query_22 = """
    MATCH (a:Actor)-[:A_JOUE]->(f:Film)<-[:A_REALISE]-(d:Realisateur)
    RETURN a.name AS actor_name, count(DISTINCT d) AS director_count
    ORDER BY director_count DESC
    LIMIT 5
    """

    result_22 = run_query(query_22)

    if result_22:
        df_22 = pd.DataFrame(result_22, columns=["Actor", "Number of Directors"])

        df_22.index = df_22.index + 1#to have the right place number (instead of starting at 0)
        st.table(df_22)
    else:
        st.warning("No actor/director relationships found.")
    #################################################################################################################
    @st.cache_data # Pour ne pas relancer la requête à chaque clic
    def get_all_actors():
        query = "MATCH (a:Actor) RETURN a.name AS name ORDER BY name ASC"
        results = run_query(query)
        return [r['name'] for r in results] if results else []

    all_actors = get_all_actors()
        
    st.subheader("23. Recommend a film to an actor based on the genres of the films in which they have already starred.")
    if all_actors:
        target_actor = st.selectbox("Select an actor for recommendations:", all_actors, key="sb_23")

        query_23 = """
        MATCH (a:Actor {name: $name})-[:A_JOUE]->(f1:Film)-[:HAS_GENRE]->(g:Genre)
        WITH a, collect(DISTINCT g) AS favoriteGenres
        MATCH (f2:Film)-[:HAS_GENRE]->(g2:Genre)
        WHERE g2 IN favoriteGenres AND NOT (a)-[:A_JOUE]->(f2)
        RETURN f2.title AS title, count(DISTINCT g2) AS common_genres
        ORDER BY common_genres DESC
        LIMIT 5
        """

        if target_actor:
            res_23 = run_query(query_23, parameters={"name": target_actor})
            if res_23:
                st.success(f"Top 5 recommendations for **{target_actor}**:")
                for row in res_23:
                    st.write(f"- 🎬 **{row['title']}** ({row['common_genres']} matching genres)")
            else:
                st.info("No specific recommendations found for this actor.")
    #################################################################################################################
    st.subheader("24. Create an INFLUENCE BY relationship between directors based on similarities in the genres of the films they have directed.")
    # creates a link between two directors if they share at least three genres in common.
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate influence relationships"):
            query_24 = """
            MATCH (d1:Realisateur)-[:A_REALISE]->(:Film)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(:Film)<-[:A_REALISE]-(d2:Realisateur)
            WHERE d1 <> d2
            WITH d1, d2, count(DISTINCT g) AS sharedGenres
            WHERE sharedGenres >= 3
            MERGE (d1)-[r:INFLUENCE_BY]->(d2)
            SET r.score = sharedGenres
            RETURN count(r) AS rel_created
            """
            res_24 = run_query(query_24)
            if res_24:
                count = res_24[0]['rel_created']
                st.success(f"Done! {count} 'INFLUENCE_BY' relationships created.")
            else:
                st.warning("No relationships created (check if directors share at least 3 genres).")

    with col2:
        # Cleaning up button in case we want to try this feature again
        if st.button(" Clean Influence Relationships", type="secondary"):
            query_clean = "MATCH (:Realisateur)-[r:INFLUENCE_BY]->(:Realisateur) DELETE r"
        
            try:
                run_query(query_clean)
                st.info("Cleanup complete: All 'INFLUENCE_BY' links have been removed.")
            except Exception as e:
                st.error(f"Error during cleanup: {e}")

    #################################################################################################################

    st.subheader("25. What is the shortest ‘path’ between two given actors (e.g. Tom Hanks and Scarlett Johansson)?")
    if all_actors:
        col1, col2 = st.columns(2)
        with col1:
            a_1 = st.selectbox("Actor A:", all_actors, key="path_a")
        with col2:
            a_2 = st.selectbox("Actor B:", all_actors, key="path_b")

        if st.button("Visualise Shortest Path"):
            query = """
            MATCH (a1:Actor {name: $name1}), (a2:Actor {name: $name2})
            MATCH p = shortestPath((a1)-[:A_JOUE*..10]-(a2))
            RETURN p
            """
            res = run_query(query, parameters={"name1": a_1, "name2": a_2})

            if res:
                path = res[0]['p']
                nodes = []
                edges = []
                node_ids = set()

                for node in path.nodes:
                    nid = node.element_id # ou node.id selon ta version
                    if nid not in node_ids:
                        label = node['name'] if "Actor" in node.labels else node['title']
                        color = "#FF4B4B" if "Actor" in node.labels else "#1c83e1"
                        nodes.append(Node(id=nid, label=label, size=20, color=color))
                        node_ids.add(nid)

                for rel in path.relationships:
                    edges.append(Edge(source=rel.start_node.element_id, 
                                    target=rel.end_node.element_id, 
                                    label="A_JOUE"))

                config = Config(width=700, height=400, directed=False, physics=True, hierarchical=False)
                agraph(nodes=nodes, edges=edges, config=config)
            else:
                st.warning("No path found.")
    #################################################################################################################
    st.subheader("26. Analyse actor communities: Which groups of actors tend to work together? (Using community detection algorithms such as Louvain.)")
    query_drop = "CALL gds.graph.drop('actorGraph', false) YIELD graphName"

    query_project = """
    CALL gds.graph.project(
        'actorGraph',
        ['Actor', 'Film'],
        'A_JOUE'
    ) YIELD graphName;
    """

    query_louvain = """
    CALL gds.louvain.stream('actorGraph')
    YIELD nodeId, communityId
    WITH gds.util.asNode(nodeId) AS n, communityId
    WHERE n:Actor
    RETURN communityId, collect(n.name) AS actors
    ORDER BY size(actors) DESC
    LIMIT 5
    """

    if st.button("Run Community Detection"):
        try:
            # 1. Cleaning up in order to avoid jam from an previously created graph
            run_query(query_drop)
            
            # 2. Build new projection
            run_query(query_project) 
            
            # 3. Run the Louvain algo
            res_26 = run_query(query_louvain)
            
            if res_26:
                for row in res_26:
                    with st.expander(f"👥 Community {row['communityId']} ({len(row['actors'])} actors)"):
                        st.write(", ".join(row['actors'][:20]) + ("..." if len(row['actors']) > 20 else ""))
            else:
                st.info("No communities detected. Ensure your graph has A_JOUE relationships.")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.info("Make sure the GDS plugin is installed and that your database has enough memory.")