import streamlit as st
import pandas as pd
import requests
import json
import time

# API configuration
SERPER_API_KEY = 'd5902a17c8fb566a6ace5d9a1436da142f1bb8e4'
HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B"
HUGGING_FACE_HEADERS = {"Authorization": "Bearer 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"}

def search_serper(query: str) -> str:
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    results = response.json().get('organic', [])
    return "\n".join([result.get('snippet', '') for result in results])

def query_llm(text: str):
    response = requests.post(HUGGING_FACE_API_URL, headers=HUGGING_FACE_HEADERS, json={"inputs": text})
    return response.json()

def process_entities(entities: list, prompt_template: str) -> list:
    results = []
    for entity in entities:
        try:
            # Search
            search_results = search_serper(prompt_template.format(entity=entity))
            
            # Get LLM response
            llm_response = query_llm(search_results)
            
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
    
    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Data Preview:")
        st.dataframe(df.head())
        
        # Select column
        selected_column = st.selectbox("Select column to process:", df.columns)
        
        # Prompt template
        prompt_template = st.text_area(
            "Enter your prompt template:",
            "Find information about {entity}"
        )
        
        if st.button("Process Data"):
            with st.spinner("Processing..."):
                entities = df[selected_column].dropna().tolist()
                
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