import streamlit as st
import pandas as pd
import plotly.express as px
from mongo_manager import get_mongo_client
from neo4j_manager import run_query

# Page setting up
st.set_page_config(page_title="Mon Dashboard Multi-NoSQL", layout="wide")
st.title("🎬 Analysing with Mongo")

# --- MONGODB SECTION---
st.header("📊 Global statistics")
client = get_mongo_client()

if client:
    try : 
        db = client.entertainment  #DB name on mongo
        collection = db.films #to reduce writing in queries 

        filter_query = {"_id": {"$regex": "^[0-9]{1,3}$"}}  
        total_films = db.films.count_documents(filter_query)
        st.metric("Total des films", total_films)
           
        
        st.subheader("1. Display the year in which the highest number of films were released.")
        qOne = collection.aggregate([
            {"$group": {"_id": "$year", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$limit": 1}
        ]).next()
        st.metric("Highest number of films were released in : ", qOne["_id"], f"{qOne['total']} films")

        #################################################################################################################

        st.subheader("2. How many films were released after 1999?")
        qTwo = collection.aggregate([
            {"$match":{"year" : {"$gt" : 1999}}},
            {"$group":{"_id": None, "total": {"$sum":1}}}]).next()
        st.metric("Number of movies released after 1999 : ", qTwo["total"])

        st.subheader("3. What is the average rating for films released in 2007?")
        qThree = db.films.aggregate([
                {"$match": {"year": 2007}},
                {"$group": {"_id": None, "avgVoteValue": {"$avg": "$Votes"}}}
            ]).next()
        st.metric("Average number of votes in 2007", f"{qThree['avgVoteValue']:.0f}")

        #################################################################################################################

        st.subheader("4. Display a bar chart showing the number of films per year.")
        pipeline = [
            {"$group": {"_id": "$year", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}} # On trie par année (1990, 1991...)
        ]
        results = list(collection.aggregate(pipeline))
        # turning dictionnaries into tables
        df = pd.DataFrame(results)

        #Renaming the columns
        df.rename(columns={"_id": "Year", "count": "Number of Films"}, inplace=True)

        fig = px.bar(
            df, 
            x="Year", 
            y="Number of Films",
            title="Distribution of Films by Year",
            color_discrete_sequence=['#00CC96'] 
        )
        st.plotly_chart(fig, use_container_width=True)

        #################################################################################################################

        st.subheader("5. What film genres are available in the database?")
        pipeline = [
            # 1.Turn strings lists into tables
            {"$project": {"genre_list": {"$split": ["$genre", ","]}}},
            
            # 2. Turning them into documents
            {"$unwind": "$genre_list"},
            
            # 3. Grouping by names
            {"$group": {"_id": "$genre_list"}},
        ]
        genres_cursor = collection.aggregate(pipeline)
        genres = [doc["_id"] for doc in genres_cursor]
        st.write(f"Genres available :  \n {', '.join(genres)}")

        #################################################################################################################


        st.subheader("6. Which film generated the most revenue?")
        top_revenue_movie = collection.find_one(
            {
                "Revenue (Millions)": {"$exists": True, "$ne": None, "$gt": 0}#Precise so we don't get Paris Pieds nus without any revenue
            }, 
            sort=[("Revenue (Millions)", -1)]
        )

        
        st.write(f"Highest revenue movie: {top_revenue_movie['title']}")
        st.metric(
            label="Total Revenue", 
            value=f"${top_revenue_movie['Revenue (Millions)']}M",
            delta=f"Released in {top_revenue_movie.get('year', 'N/A')}"
        )

        #################################################################################################################

        st.subheader("7. Which directors have made more than 5 films in the database?")
        pipeline_q7 = [
            {"$group": {"_id": "$Director", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 5}}},
            {"$sort": {"count": -1}}
        ]
        directors = list(collection.aggregate(pipeline_q7))
        if directors:
            for d in directors:
                # Making sure we manage the case were director is smissing
                name = d['_id'] if d['_id'] else "Unknown Director"
                st.write(f"- **{name}** : {d['count']} films")
        else:
            st.info("Aucun réalisateur n'a plus de 5 films dans cette base de données.")

        #################################################################################################################

        st.subheader("8. Which film genre generates the highest average revenue?")
        pipeline_q8 = [
            {"$match": {"Revenue (Millions)": {"$gt": 0}}},
            {"$project": {"revenue": "$Revenue (Millions)", "genre_list": {"$split": ["$genre", ","]}}},
            {"$unwind": "$genre_list"},
            {"$group": {"_id": {"$trim": {"input": "$genre_list"}}, "avg_rev": {"$avg": "$revenue"}}},
            {"$sort": {"avg_rev": -1}},
            {"$limit": 1}
        ]
        res_q8 = list(collection.aggregate(pipeline_q8))
        if res_q8:
            st.write(f"The highest grossing genre is : **{res_q8[0]['_id']}** (Moyenne: {res_q8[0]['avg_rev']:.2f}M$)")

        #################################################################################################################


        st.subheader("9. Which are the 3 highest-rated films for each decade (1990–1999, 2000–2009, etc.)?")
        pipeline_q9 = [
        # 1.We sort out movies without year or rating
        {"$match": {
            "year": {"$type": "number"},
            "rating": {"$ne": "unrated"}
        }},
        # 2. Computing decade
        {"$project": {
            "title": 1,
            "rating": 1,
            "decade": {
                "$concat": [
                    {"$toString": {"$subtract": ["$year", {"$mod": ["$year", 10]}]}},
                    "s"
                ]
            }
        }},
        # 3. sort descending way before grouping
        {"$sort": {"rating": -1}},
        # 4. group by decade and push movies into lists
        {"$group": {
            "_id": "$decade",
            "top_films": {"$push": {"title": "$title", "rating": "$rating"}}
        }},
        # 5. We keep only the first 3 movies from each list
        {"$project": {
            "decade": "$_id",
            "top_films": {"$slice": ["$top_films", 3]}
        }},
        # 6. Sort by decade
        {"$sort": {"_id": 1}}
        ]
        results_q9 = list(collection.aggregate(pipeline_q9))

        if results_q9:
            for doc in results_q9:
                with st.expander(f"Decade: {doc['_id']}"):
                    for i, movie in enumerate(doc['top_films'], 1):
                        st.write(f"{i}. **{movie['title']}** — {movie['rating']}")
        else:
            st.info("No data available regarding decades.")

        #################################################################################################################
        
        st.subheader("10. Which is the longest film (Runtime) by genre?")
        pipeline_q10 = [
            {"$match": {"Runtime (Minutes)": {"$gt": 0}}},
            {"$project": {"title": 1, "runtime": "$Runtime (Minutes)", "genre_list": {"$split": ["$genre", ","]}}},
            {"$unwind": "$genre_list"},
            {"$project": {"title": 1, "runtime": 1, "genre": {"$trim": {"input": "$genre_list"}}}},
            {"$sort": {"runtime": -1}},
            {"$group": {"_id": "$genre", "longest_movie": {"$first": "$title"}, "duration": {"$first": "$runtime"}}},
            {"$sort": {"_id": 1}}
        ]
        res_q10 = list(collection.aggregate(pipeline_q10))
        if res_q10:
            # display as a Panda table 
            df_q10 = pd.DataFrame(res_q10).rename(columns={"_id": "Genre", "longest_movie": "Film", "duration": "Runtime (min)"})
            st.table(df_q10) 

        #################################################################################################################

        st.subheader("11. Create a MongoDB view displaying only films with a rating higher than 80 (Metascore) and have grossed over $50 million.")
        query_q11 = {
            "Metascore": {"$gt": 80},
            "Revenue (Millions)": {"$gt": 50}
        }
        #Keeping only interesting columns
        films_q11 = list(collection.find(query_q11, {"title": 1, "Metascore": 1, "Revenue (Millions)": 1, "_id": 0}))

        if films_q11:
            st.dataframe(pd.DataFrame(films_q11), use_container_width=True)
        else:
            st.info("Aucun film ne remplit ces critères de succès critique et commercial.")

        #################################################################################################################

        st.subheader("12. Calculate the correlation between film duration (Runtime) and box office revenue (Revenue). (Carry out a statistical analysis.)")
        
        data_q12 = list(collection.find(
            {"Runtime (Minutes)": {"$gt": 0}, "Revenue (Millions)": {"$gt": 0}},
            {"Runtime (Minutes)": 1, "Revenue (Millions)": 1, "_id": 0}
        ))

        if data_q12:
            df_corr = pd.DataFrame(data_q12)
            corr_value = df_corr.corr().iloc[0, 1]
            
            col1, col2 = st.columns([1, 2])
            col1.metric("Correlation Coefficient", f"{corr_value:.2f}")
            

            # Explanation
            if corr_value > 0.5:
                col2.write("Analysis : Strong positive correlation: feature films are more profitable.")
            elif corr_value > 0:
                col2.write("Analysis : Weak positive correlation.")
            else:
                col2.write("Analysis : There is no significant correlation between duration and income.")
                
            # Dots cloud as illustration
            fig_corr = px.scatter(df_corr, x="Runtime (Minutes)", y="Revenue (Millions)", trendline="ols")
            st.plotly_chart(fig_corr)
            #We explained this next part as it seems to be the result
            st.write("Positive: This means that, generally speaking, as running time increases, revenue tends to increase as well.  \n " \
                "Weak: The link is not automatic. We are a long way from 1 (perfect correlation). This shows that a film’s running time is " \
                "not the main factor in its financial success.  \n The wide scatter of the data points shows that runtime is not a reliable predictor of box office performance")

        #################################################################################################################
        st.subheader("13. Is there a trend in the average film duration by decade?")
        pipeline_q13 = [
            {"$match": {"Runtime (Minutes)": {"$gt": 0}, "year": {"$gt": 0}}},
            {"$project": {
                "runtime": "$Runtime (Minutes)",
                "decade": {"$subtract": ["$year", {"$mod": ["$year", 10]}]}
            }},
            {"$group": {"_id": "$decade", "avg_runtime": {"$avg": "$runtime"}}},
            {"$sort": {"_id": 1}}
        ]

        res_q13 = list(collection.aggregate(pipeline_q13))
        if res_q13:
            df_trend = pd.DataFrame(res_q13).rename(columns={"_id": "Decade", "avg_runtime": "Avg Duration"})
            # Chart to show results
            fig_trend = px.line(df_trend, x="Decade", y="Avg Duration", markers=True, title="Evolution of Movie Length")
            st.plotly_chart(fig_trend)
            st.write("Yes, there does seem to be a trend, but it is not linear. We saw a significant trend towards shorter" \
            " durations between 2000 and 2010, before returning to shorter standards (around two hours).")

    except Exception as e:
        st.error(f"Error when executing queries : {e}")
    finally:
        client.close() # Good practice, free resources 
else:
    st.error("Can't connect to MongoDB, check Secrets.")


