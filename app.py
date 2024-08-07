import pandas as pd
import zipfile
import io
from flask import Flask, jsonify
from google.cloud import storage

app = Flask(__name__)

def fetch_latest_data():
    """
    Fetch data from Google Cloud Storage and return it as a DataFrame.
    """
    try:
        client = storage.Client()
        bucket_name = 'lindyscore'
        file_name = 'Files.zip'
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        zip_content = blob.download_as_bytes()

        # Extract the zip file
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            for file_info in z.infolist():
                with z.open(file_info) as file:
                    df = pd.read_csv(file, engine='python', on_bad_lines='skip')
                    break  # Assuming there's only one file in the zip

        return df
    except Exception as e:
        return None, f"Error fetching data: {e}"

def calculate_lindy_scores(graft_data):
    """
    Calculate Lindy scores for each graft type based on various factors.
    """
    current_year = pd.Timestamp.now().year

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

    graft_data['lindy_score'] = graft_data.apply(lindy_score, axis=1)
    return graft_data

@app.route('/latest_lindy_score', methods=['GET'])
def latest_lindy_score():
    df, error = fetch_latest_data()
    if error:
        return jsonify({"error": error}), 500

    if df is None or df.empty:
        return jsonify({"error": "No data available"}), 404

    # Set index and calculate scores
    try:
        df.set_index('graft_type', inplace=True)
        scores_df = calculate_lindy_scores(df)
        result = scores_df[['lindy_score']].to_dict(orient='index')
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Error processing data: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)





