
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")

if not DATA_DIR.exists():
    print("ERROR: data folder not found.")
else:
    for file in sorted(DATA_DIR.glob("*.csv")):
        print("\n" + "=" * 60)
        print("FILE:", file.name)

        try:
            df = pd.read_csv(file, nrows=5)
            print("Columns:", df.columns.tolist())
            print("Sample rows:")
            print(df.head(3).to_string(index=False))
        except Exception as e:
            print("Could not read file:", e)
