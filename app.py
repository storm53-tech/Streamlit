import pandas as pd
import zipfile
import io
from google.cloud import storage

def fetch_latest_data():
    """
    Fetch data from Google Cloud Storage and return it as a DataFrame.
    """
    try:
        client = storage.Client()
        bucket_name = 'lindyscore'  # Update with your actual bucket name
        file_name = 'Files.zip'
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        zip_content = blob.download_as_bytes()

        # Extract the zip file
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            for file_info in z.infolist():
                print(f"Extracting file: {file_info.filename}")
                with z.open(file_info) as file:
                    # Debug: Print first few lines to check content
                    content = file.read().decode('utf-8')
                    print("File content:\n", content)  # Print the content of the file
                    
                    # Use StringIO to convert string data into a file-like object
                    csv_file = io.StringIO(content)
                    df = pd.read_csv(csv_file, delimiter=',', engine='python', on_bad_lines='skip')
                    break  # Assuming there's only one file in the zip

        print("Columns in DataFrame:", df.columns)
        print("DataFrame preview:\n", df.head())
        
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()



def calculate_lindy_scores(graft_data):
    """
    Calculate Lindy scores for each graft type based on various factors.
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
        
def main():
    st.title("Lindy Score Calculator")
        
    # Fetch and display data
    df = fetch_latest_data()
    if not df.empty:
        st.write("Graft Data", df)
            
        # Set index and calculate scores
        df.set_index('graft_type', inplace=True)
        scores = calculate_lindy_scores(df)

        # Display scores
        st.write("Lindy Scores", scores)
    else:
        st.write("No data available.")

if __name__ == "__main__":
    main()

