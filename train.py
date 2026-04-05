import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# ── 1. LOAD DATA ──────────────────────────────────────────────
df = pd.read_csv("gd.csv")

# We only keep rows where the player WON
# Because we want to learn "what actions lead to winning"
winning_moves = df[df["win"] == 1]

# ── 2. FEATURES & LABEL ───────────────────────────────────────
# Features = everything the player can SEE during their turn
# Label    = what action they took (that eventually won)

features = [
    "my_char",
    "enemy_char",
    "my_hp",
    "enemy_hp",
    "my_cd",
    "enemy_cd",
    "my_ability3",
    "enemy_ability3"
]

X = winning_moves[features]
y = winning_moves["action"]

# ── 3. SPLIT ──────────────────────────────────────────────────
# 80% for training, 20% for testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training on {len(X_train)} winning moves")
print(f"Testing  on {len(X_test)} winning moves")

# ── 4. TRAIN ──────────────────────────────────────────────────
model = DecisionTreeClassifier(
    max_depth=6,       # not too deep = not too overfit
    random_state=42
)
model.fit(X_train, y_train)

# ── 5. EVALUATE ───────────────────────────────────────────────
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {acc*100:.2f}%")
for name, val in zip(features, model.feature_importances_):
    print(name, ":", round(val, 3))
# ── 6. SAVE MODEL ─────────────────────────────────────────────
with open("model_v1.pkl", "wb") as f:
    pickle.dump(model, f)

print("\nModel saved as model_v1.pkl")
import pickle, pandas as pd
with open("model_v1.pkl", "rb") as f:
    model = pickle.load(f)

# simulate politician's typical game state
test = pd.DataFrame([{
    "my_char": 2, "enemy_char": 1,
    "my_hp": 10, "enemy_hp": 8,
    "my_cd": 0, "enemy_cd": 0,
    "my_ability3": 0, "enemy_ability3": 1
}])

print(model.predict(test))

