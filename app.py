import os
from flask import Flask, jsonify
import pandas as pd
import datetime
import zipfile
import io
from google.cloud import storage

app = Flask(__name__)

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

@app.route('/', methods=['GET'])
def get_lindy_scores():
    """
    HTTP Cloud Function to fetch the latest graft data, calculate Lindy scores,
    and return them as a JSON response.
    """
    try:
        # Initialize the Cloud Storage client
        client = storage.Client()

        # Define your bucket and file
        bucket_name = 'aclgrafts-lindyscore-430915-staging'
        file_name = 'Files.zip'

        # Get the bucket and blob (file)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Download the file content
        zip_content = blob.download_as_bytes()

        # Extract the zip file
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            # Assuming the zip file contains a CSV with graft data
            for file_info in z.infolist():   
                with z.open(file_info) as file:
                    df = pd.read_csv(file)
                    break  # Assuming there's only one file in the zip

        # Set index and calculate scores
        df.set_index('graft_type', inplace=True)
        scores = calculate_lindy_scores(df)

        # Return results as JSON
        return jsonify(scores)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

