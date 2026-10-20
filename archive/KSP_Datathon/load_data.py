import sqlite3
import pandas as pd
import os

# Connect to your main database vault
db_path = "karnataka_police_fir.db"
conn = sqlite3.connect(db_path)

# Map the table names to the CSV files we just generated
files_to_load = {
    "CaseMaster": "synthetic_data/CaseMaster.csv",
    "Victim": "synthetic_data/Victim.csv",
    "Accused": "synthetic_data/Accused.csv",
    "ComplainantDetails": "synthetic_data/ComplainantDetails.csv",
    "ArrestSurrender": "synthetic_data/ArrestSurrender.csv"
}

print("Opening the vault and injecting realistic KSP data...\n" + "-"*50)

# Loop through the files and push them into the database
for table_name, csv_path in files_to_load.items():
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # We use if_exists='replace' so if you run this multiple times, it refreshes the data cleanly
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f" -> Successfully loaded {len(df)} records into the '{table_name}' table.")
    else:
        print(f" -> ERROR: Could not find {csv_path}. Did the generation script fail?")

conn.close()
print("-"*50 + "\n✅ SUCCESS: All hyper-realistic data is now live inside the database vault!")