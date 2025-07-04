import pandas as pd
import os

# Path to the full reviews file
FULL_PATH = "Data/goodreads_reviews.csv"
# Path to the sample output file
SAMPLE_PATH = "Data/goodreads_reviews_sample.csv"

# Number of rows to sample (adjust as needed for Streamlit Cloud)
N_SAMPLE = 5000

if not os.path.exists(FULL_PATH):
    print(f"Full reviews file not found at {FULL_PATH}. Please make sure it exists.")
else:
    print(f"Loading full reviews file from {FULL_PATH}...")
    df = pd.read_csv(FULL_PATH, low_memory=False)
    print(f"Full reviews file has {len(df):,} rows.")

    print(f"Sampling {N_SAMPLE} random rows...")
    sample_df = df.sample(N_SAMPLE, random_state=42)
    sample_df.to_csv(SAMPLE_PATH, index=False)
    print(f"Sample saved to {SAMPLE_PATH} ({len(sample_df):,} rows).")

