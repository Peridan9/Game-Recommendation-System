import pymongo
import bcrypt
import ast
import pandas as pd
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LoginManager:

    def __init__(self) -> None:
        # MongoDB connection
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["project"]
        self.collection = self.db["users"]
        self.salt = b"$2b$12$ezgTynDsK3pzF8SStLuAPO"  # TODO: if not working, generate a new salt

    def register_user(self, username: str, password: str) -> None:
        try:
            #Check if the username and password are not empty strings. If either is empty, raise "Username and password are required." ValueError.
            if(username == "" or password == ""):
                raise ValueError("Username and password are required.")
            #Check if the length of both username and password is at least 3 characters. If not, raise "Username and password must be at least 3 characters." ValueError.
            if(len(username) < 3 or len(password) < 3):
                raise ValueError("Username and password must be at least 3 characters.")
            #Check if the username already exists in the database. If it does, raise "User already exists: {username}." ValueError.
            user_query = {"Username": username}
            user = self.collection.find_one(user_query) 
            if(user != None):
                raise ValueError("User already exists: {}.".format(username))
            #If the validation above has not failed, hash the provided password using bcrypt and create a new user in the database.
            bytes_pwd = password.encode('utf-8')
            hashed_pwd = bcrypt.hashpw(bytes_pwd, self.salt)
            user_dict = { "Username": username, "Password": hashed_pwd, "Rented_Games":[]}
            self.collection.insert_one(user_dict)
        except ValueError as v:
            print(v)


    def login_user(self, username: str, password: str) -> object:
        try:
            if(username == "" or password == ""):
                raise ValueError("Username and password are required.")
            #1. Hash the provided password using bcrypt (with same salt as before).
            bytes_pwd = password.encode('utf-8')
            hashed_pwd = bcrypt.hashpw(bytes_pwd, self.salt)
            #2. Query the MongoDB collection to find a user with the provided username and hashed password.
            user_query = {"Username": username}
            user = self.collection.find_one(user_query)
            #3. If a user is found, print "Logged in successfully as: {username}" and return the user object.
            #4. If no user is found or the password doesn't match, raise "Invalid username or password" ValueError.
            if(user!=None and user['Password'] == hashed_pwd):
                print("Logged in successfully as:",username)
                return user
            else:
                raise ValueError("Invalid username or password")
        except ValueError as v:
            print(v)



class DBManager:

    def __init__(self) -> None:
        # MongoDB connection
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["project"]
        self.user_collection = self.db["users"]
        self.game_collection = self.db["games"]

    def load_csv(self) -> None:
        df = pd.read_csv("NintendoGames.csv")
        df['genres'] = df['genres'].apply(ast.literal_eval)
        df['is_rented'] = False
        for _,row in df.iterrows():
            query = {"title": row["title"]}
            existing_game = self.game_collection.find_one(query)
            if not existing_game:
                self.game_collection.insert_one(row.to_dict())

    def recommend_games_by_genre(self, user: dict) -> str:
        user_query = {"Username": user["Username"]}
        user = self.user_collection.find_one(user_query)
        user_rented_games = user["Rented_Games"]
        if(user_rented_games == []):
            return "No games rented"
        game_genres = []
        for game_title in user_rented_games:
            game_query = {"title": game_title}
            game_genre = self.game_collection.find_one(game_query)["genres"]
            game_genres.extend(game_genre)
        # Calculate the frequency of each genre
        genre_frequency = {}
        for genre in game_genres:
            genre_frequency[genre] = genre_frequency.get(genre, 0) + 1
        # Calculate the probability distribution of genres
        total_games = len(game_genres)
        genre_probabilities = {genre: count / total_games for genre, count in genre_frequency.items()}
        # Select a genre based on the probability distribution
        selected_genre = random.choices(list(genre_probabilities.keys()), weights=list(genre_probabilities.values()))[0]
        # Query the game collection to find 5 random games with the chosen genre
        recommended_games = []
        while len(recommended_games) < 5:
            games_with_genre = list(self.game_collection.find({"genres": selected_genre}))
            if games_with_genre:
                recommended_game = random.choice(games_with_genre)
                if recommended_game["title"] not in user_rented_games:
                    recommended_games.append(recommended_game["title"])
                
        return "\n".join(recommended_games)


        

    def recommend_games_by_name(self, user: dict) -> str:
    #1. Get the list of games rented by the user from the user object.
        user_query = {"Username": user["Username"]}
        user = self.user_collection.find_one(user_query)
        user_rented_games = user["Rented_Games"]
    #2. If no games are rented, return "No games rented".
        if(user_rented_games == []):
            return "No games rented"
    #3. Choose a random game from the rented games.
        chosen_game_title = random.choice(user_rented_games)
    #4. Compute TF-IDF vectors for all game titles and the chosen title (u can use TfidfVectorizer from sklearn library).
        all_game_titles = [game["title"] for game in self.game_collection.find({}, {"title": 1})]
        print(all_game_titles)
        all_game_titles = [title for title in all_game_titles if title not in user_rented_games]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(all_game_titles + [chosen_game_title])
     #5. Compute cosine similarity between the TF-IDF vectors of the chosen title and all other games (u can use cosine_similarity from sklearn library).
        cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
    #6. Sort the titles based on cosine similarity and return the top 5 recommended titles as a string separated with "\n".
        sorted_indices = cosine_similarities.argsort()[::-1]
        recommended_titles = [all_game_titles[i] for i in sorted_indices[:5]]
        return "\n".join(recommended_titles)


    def rent_game(self, user: dict, game_title: str) -> str:
        #1. Query the game collection to find the game with the provided title.
        game_query = {"title": game_title}
        game = self.game_collection.find_one(game_query)
        user_query = {"Username": user["Username"]}
        user = self.user_collection.find_one(user_query)
        user_rented_games = user["Rented_Games"]
        #2. If the game is found: Check if the game is not already rented. If not rented, mark the game as rented in the game collection and add it to the user's rented games list. Return "{game_title} rented successfully".
        #If the game is not found, return "{game_title} not found".
        if(game is None):
             return "{} not found".format(game_title)
        #If the game is already rented, return "{game_title} is already rented
        else:
            if(game["is_rented"] == True):
                return "{} is already rented".format(game_title)
            else:
                newrentvalues = {"$set":{"is_rented":True}}
                self.game_collection.update_one(game_query,newrentvalues)
                user_rented_games.append(game_title)
                newrentedvalues = {"$set":{"Rented_Games":user_rented_games}}
                self.user_collection.update_one(user_query,newrentedvalues)        
        return "{} rented successfully".format(game_title)
        
        

    def return_game(self, user: dict, game_title: str) -> str:
        #1. Get the list of games rented by the user from the user object.
        user_query = {"Username": user["Username"]}
        user = self.user_collection.find_one(user_query)
        user_rented_games = user["Rented_Games"]
        game_query = {"title": game_title}
        #2. If the game with the provided title is rented by the user: Remove the game from the user's rented games list. Mark the game as not rented in the game collection.Return "{game_title} returned successfully".
        for game in user_rented_games:
            if game == game_title:
                user_rented_games.remove(game)
                newrentedvalues = {"$set":{"Rented_Games":user_rented_games}}
                self.user_collection.update_one(user_query,newrentedvalues)
                newrentvalues = {"$set":{"is_rented":False}}
                self.game_collection.update_one(game_query,newrentvalues)
                return "{} returned successfully".format(game_title)
        return "{} was not rented by you".format(game_title)
        #3. If the game is not rented by the user, return "{game_title} was not rented by you"
        

def main():
    lm = LoginManager()
    # lm.register_user("test_user1","Huy")
    lm.register_user("test_user2","Huy")
    # lm.register_user("test_user3", "Huy")
    # lm.register_user("test_user4", "Huy")
    # lm.login_user("test_user1","aaa")
    # lm.login_user("test_user2","Huy")
    # lm.login_user("tt_user3", "Huy")
    dbm = DBManager()
    user = lm.login_user("test_user2","Huy")
    # print(dbm.rent_game(user, "Fae Farm"))
    print(dbm.rent_game(user,"Yo-kai Watch 4"))
    # print(dbm.return_game(user,"Fae Farm"))
    print(dbm.recommend_games_by_genre(user))
    # print(dbm.recommend_games_by_name(user))





if __name__ == "__main__":
    main()