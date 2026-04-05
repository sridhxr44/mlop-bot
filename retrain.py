import pandas as pd
import pickle
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

# 1. merge new_data into gd.csv
if os.path.isfile("new_data.csv"):
    old = pd.read_csv("gd.csv")
    new = pd.read_csv("new_data.csv")
    
    if len(new) > 0:
        combined = pd.concat([old, new], ignore_index=True)
        combined.to_csv("gd.csv", index=False)
        # clear new_data.csv after merging
        new.head(0).to_csv("new_data.csv", index=False)
        print(f"Merged {len(new)} new rows into gd.csv")
    else:
        print("No new data to merge")
        combined = old
else:
    combined = pd.read_csv("gd.csv")

# 2. retrain
features = [
    "my_char", "enemy_char",
    "my_hp", "enemy_hp",
    "my_cd", "enemy_cd",
    "my_ability3", "enemy_ability3"
]

winning = combined[combined["win"] == 1]
X = winning[features]
y = winning["action"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(max_depth=6, random_state=42)
model.fit(X_train, y_train)

acc = accuracy_score(y_test, model.predict(X_test))
print(f"New accuracy: {acc*100:.2f}%")

# 3. save
with open("model_v1.pkl", "wb") as f:
    pickle.dump(model, f)
print("Model saved")
