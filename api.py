from fastapi import FastAPI
import pickle
import numpy as np
import csv
import os

app = FastAPI()

with open("model_v1.pkl", "rb") as f:
    model = pickle.load(f)

game_log = []

@app.get("/")
def home():
    return {"message": "API is running"}

@app.post("/predict")
def predict(data: dict):
    features = [
        data["my_char"],
        data["enemy_char"],
        data["my_hp"],
        data["enemy_hp"],
        data["my_cd"],
        data["enemy_cd"],
        data["my_ability3"],
        data["enemy_ability3"]
    ]

    X = np.array(features).reshape(1, -1)
    prediction = int(model.predict(X)[0])

    if prediction == 1 and data["my_cd"] == 1:
        prediction = 2
    if prediction == 3 and data["my_ability3"] == 0:
        prediction = 2

    game_log.append({**data, "action": prediction})

    return {"action": prediction}

@app.post("/end_game")
def end_game(result: dict):
    win = result["win"]
    moves_saved = len(game_log)

    file_exists = os.path.isfile("new_data.csv")
    with open("new_data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["my_char","enemy_char","my_hp","enemy_hp",
                             "my_cd","enemy_cd","my_ability3","enemy_ability3",
                             "action","win"])
        for move in game_log:
            writer.writerow([
                move["my_char"], move["enemy_char"],
                move["my_hp"], move["enemy_hp"],
                move["my_cd"], move["enemy_cd"],
                move["my_ability3"], move["enemy_ability3"],
                move["action"],  # this is missing
                win
            ])

    game_log.clear()
    return {"message": "logged", "moves_saved": moves_saved}
