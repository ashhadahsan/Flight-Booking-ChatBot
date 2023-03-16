english = False
verbose = False
energy = 300
dynamic_energy = False
pause = 0.8

import pandas as pd

df = pd.read_csv("airport-codes.csv")
df = df.dropna(subset=["iata_code"])

df["municipality"] = df["municipality"].astype(str)
cities = df["municipality"].unique().tolist()
cities = ", ".join([x for x in cities])
