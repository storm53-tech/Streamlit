import pandas as pd
import zipfile
import io
import requests
import streamlit as st
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
            file_names = z.namelist()
            print("Files in the zip archive:", file_names)
            st.write("Files in the zip archive:", file_names)  # Streamlit debugging

            csv_files = [name for name in file_names if name.endswith('.csv')]
            
            if len(csv_files) != 1:
                raise ValueError(f"Expected exactly one CSV file, but found {len(csv_files)}: {csv_files}")

            csv_file_name = csv_files[0]
            print(f"Processing CSV file: {csv_file_name}")
            st.write(f"Processing CSV file: {csv_file_name}")  # Streamlit debugging
            
            with z.open(csv_file_name) as file:
                # Read CSV data directly from the file object
                try:
                    # Read CSV data
                    df = pd.read_csv(file, delimiter=',', engine='python')
                    df.columns = df.columns.str.strip()  # Remove any extra spaces from column names
                    print("Columns in DataFrame:", df.columns)  # Debug print for columns
                    st.write("Columns in DataFrame:", df.columns)  # Streamlit debugging
                    print("DataFrame preview:\n", df.head())
                    st.write("DataFrame preview:\n", df.head())  # Streamlit debugging
                    
                    # Check if DataFrame is empty
                    if df.empty:
                        print("DataFrame is empty.")
                        st.write("DataFrame is empty.")  # Streamlit debugging
                    
                except pd.errors.EmptyDataError:
                    print("No data found in CSV file.")
                    st.write("No data found in CSV file.")  # Streamlit debugging
                except pd.errors.ParserError:
                    print("Error parsing CSV file.")
                    st.write("Error parsing CSV file.")  # Streamlit debugging
                except Exception as e:
                    print(f"General error: {e}")
                    st.write(f"General error: {e}")  # Streamlit debugging

        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        st.write(f"Error fetching data: {e}")  # Streamlit debugging
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

