import streamlit as st
import pandas as pd
import datetime
import zipfile
import io
from google.cloud import storage

def fetch_latest_data():
    """
    Fetch data from sources (this is a placeholder for actual data fetching logic).
    Returns a DataFrame with graft data.
    """
    data = {
        "graft_type": ["hamstring", "quadricep", "patellar", "achilles_allograft"],
        "introduced": [1990, 2000, 1980, 2010],
        "PRO": [85, 80, 90, 75],
        "lysholm_score": [90, 85, 95, 80],
        "LSI": [92, 88, 95, 85],
        "RTS": [80, 75, 85, 70],
        "long_term_success": [88, 85, 92, 80],
        "complications": [5, 7, 6, 10],
        "biomechanical_studies": [2500, 2400, 2600, 2300],
        "citation_count": [150, 120, 200, 100]
    }
    return pd.DataFrame(data)

def calculate_lindy_scores(graft_data):
    """
    Calculate Lindy scores for each graft type based on various factors.
    Returns a dictionary with graft types as keys and their Lindy scores as values.
    """
    current_year = datetime.datetime.now().year

    def lindy_score(graft):
        age = current_year - graft["introduced"]
        clinical_assessment = (graft["PRO"] + graft["lysholm_score"] + graft["LSI"]) / 3
        success_metrics = (graft["RTS"] + graft["long_term_success"]) / 2
        complication_factor = 1 / (1 + graft["complications"])
        biomechanical_factor = graft["biomechanical_studies"] / 1000
        citation_factor = graft["citation_count"] / 100

        score = (age * clinical_assessment * success_metrics * complication_factor *
                 biomechanical_factor * citation_factor)
        return score

    scores = {index: lindy_score(row) for index, row in graft_data.iterrows()}
    return scores

def fetch_data_from_gcs():
    """
    Fetch data from Google Cloud Storage, process it, and return a DataFrame.
    """
    client = storage.Client()
    bucket_name = 'aclgrafts-lindyscore-430915-staging'
    file_name = 'Files.zip'

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    zip_content = blob.download_as_bytes()

    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        for file_info in z.infolist():
            with z.open(file_info) as file:
                df = pd.read_csv(file)
                break  # Assuming there's only one file in the zip

    df.set_index('graft_type', inplace=True)
    return df

st.title("ACL Grafts Lindy Scores")

st.write("Fetching the latest Lindy scores for ACL graft choices...")

try:
    df = fetch_data_from_gcs()
    scores = calculate_lindy_scores(df)
    st.dataframe(pd.DataFrame.from_dict(scores, orient='index', columns=['Lindy Score']))
except Exception as e:
    st.error(f"Error fetching data: {e}")

