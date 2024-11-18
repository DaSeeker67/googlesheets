import streamlit as st
import pandas as pd
import requests
import json
import time
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# API configuration
SERPER_API_KEY = 'd5902a17c8fb566a6ace5d9a1436da142f1bb8e4'
HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/distilbert/distilbert-base-uncased-distilled-squad"
HUGGING_FACE_HEADERS = {"Authorization": "Bearer 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"}

# Google Sheets API scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def authenticate_google_sheets():
    """
    Authenticate and return Google Sheets service
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    except FileNotFoundError:
        st.error("Token file not found. Please run the authorization process first.")
        return None

    # Refresh the token if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    try:
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

def fetch_google_sheet_data(sheet_id, range_name='Sheet1'):
    """
    Fetch data from a Google Sheet
    """
    service = authenticate_google_sheets()
    if not service:
        return None

    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])
        
        if not values:
            st.warning("No data found in the sheet.")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    except Exception as e:
        st.error(f"Error fetching Google Sheet data: {e}")
        return None

def search_serper(query: str) -> str:
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code != 200:
        return f"Error: Unable to fetch search results (status code {response.status_code})"
    
    results = response.json().get('organic', [])
    if not results:
        return "No results found for the query."
    
    # Collect snippets or fallback to titles if snippets are missing
    snippets = [result.get('snippet', result.get('title', 'No snippet available')) for result in results]
    return "\n".join(snippets)

def query_llm(text: str):
    response = requests.post(HUGGING_FACE_API_URL, headers=HUGGING_FACE_HEADERS, json={"inputs": text})
    if response.status_code != 200:
        return {"generated_text": f"Error: LLM request failed (status code {response.status_code})"}
    
    try:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return {"generated_text": data[0].get('generated_text', 'No response')}
        elif isinstance(data, dict):
            return {"generated_text": data.get('generated_text', 'No response')}
        else:
            return {"generated_text": "Unexpected response format from LLM."}
    except Exception as e:
        return {"generated_text": f"Error: {str(e)}"}

def process_entities(entities: list, prompt_template: str) -> list:
    results = []
    for entity in entities:
        try:
            # Search
            search_results = search_serper(prompt_template.format(entity=entity))
            query = "short 1 or 2 word response "+prompt_template+entity +"from this text"+search_results

            # Get LLM response
            llm_response = query_llm(query)
            
            # Extract text from response
            if isinstance(llm_response, list):
                generated_text = llm_response[0].get('generated_text', 'No response')
            else:
                generated_text = llm_response.get('generated_text', 'No response')
            
            results.append({
                'entity': entity,
                'extracted_info': generated_text
            })
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            results.append({
                'entity': entity,
                'extracted_info': f"Error: {str(e)}"
            })
    
    return results

def main():
    st.title("AI-Enhanced Data Processing System")
    
    # Data source selection
    data_source = st.radio("Select Data Source:", 
                           ["Upload CSV", "Google Sheets"])
    
    df = None
    
    if data_source == "Upload CSV":
        # File upload
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
    
    else:  # Google Sheets
        sheet_id = st.text_input("Enter Google Sheet ID:")
        sheet_range = st.text_input("Sheet Range (optional, default is Sheet1)", "Sheet1")
        
        if st.button("Fetch Google Sheet"):
            if sheet_id:
                df = fetch_google_sheet_data(sheet_id, sheet_range)
    
    # Process data if DataFrame is available
    if df is not None:
        st.write("Data Preview:")
        st.dataframe(df.head())
        
        # Select column
        selected_column = st.selectbox("Select column to process:", df.columns)
        
        # Prompt template
        prompt_template = st.text_area(
            "Enter your prompt template:",
            "ex find the name of the ceo "
        )
        
        if st.button("Process Data"):
            with st.spinner("Processing..."):
                entities = df[selected_column].head(5).dropna().tolist()
                
                # Process entities
                results = process_entities(entities, prompt_template)
                
                # Display results
                results_df = pd.DataFrame(results)
                st.write("Results:")
                st.dataframe(results_df)
                
                # Download button
                st.download_button(
                    "Download Results",
                    results_df.to_csv(index=False),
                    "results.csv",
                    "text/csv"
                )

if __name__ == "__main__":
    main()