import pandas as pd
import zipfile
import io
import requests  # Ensure requests is imported
import streamlit as st  # Ensure Streamlit is imported
import datetime

def fetch_latest_data():
    """
    Fetch data from a publicly accessible Google Cloud Storage URL and return it as a DataFrame.
    """
    try:
        # Public URL of the file
        public_url = 'https://storage.googleapis.com/lindyscore/Files.zip'
        
        # Download the zip file from the public URL
        response = requests.get(public_url)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        
        # Extract the zip file
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # List of files in the ZIP
            files = [file_info for file_info in z.infolist() if file_info.filename.endswith('.csv')]
            
            if not files:
                print("No CSV file found in the ZIP archive.")
                return pd.DataFrame()

            if len(files) > 1:
                print("Multiple CSV files found in the ZIP archive.")
                return pd.DataFrame()
            
            # Extract the CSV file
            csv_file_info = files[0]
            print(f"Extracting file: {csv_file_info.filename}")
            with z.open(csv_file_info) as file:
                # Read CSV data directly from the file object
                try:
                    # Read CSV data
                    df = pd.read_csv(file, delimiter=',', engine='python')
                    df.columns = df.columns.str.strip()  # Remove any extra spaces from column names
                    print("Columns in DataFrame:", df.columns)  # Debug print for columns
                    print("DataFrame preview:\n", df.head())
                    
                    # Check if DataFrame is empty
                    if df.empty:
                        print("DataFrame is empty.")
                    
                except pd.errors.EmptyDataError:
                    print("No data found in CSV file.")
                except pd.errors.ParserError:
                    print("Error parsing CSV file.")
                except Exception as e:
                    print(f"General error: {e}")
                
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

        # Ensure 'graft_type' is a valid column and set index
        if 'graft_type' in df.columns:
            df.set_index('graft_type', inplace=True)
            # Calculate and display scores
            scores = calculate_lindy_scores(df)
            st.write("Lindy Scores", scores)
        else:
            st.error("Column 'graft_type' not found in the CSV data.")
    else:
        st.write("No data available.")

# Run the Streamlit app
if __name__ == "__main__":
    main()

