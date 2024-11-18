# AI-Enhanced Data Processing System

An advanced Streamlit application that extracts and processes information from CSV files or Google Sheets using AI-powered search and language model capabilities.

## Features
- **CSV File Upload**: Easily upload CSV files for processing.
- **Google Sheets Integration**: Fetch data directly from Google Sheets.
- **AI-Powered Entity Extraction**: Extract meaningful entities using cutting-edge AI models.
- **Search-Based Information Retrieval**: Perform web searches for context enrichment.
- **Customizable Prompt Templates**: Define prompts to guide the AI in processing data.

---

## Prerequisites
- Python 3.8+
- Google Cloud Project with Sheets API enabled
- Serper API key
- Hugging Face API key

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ai-data-processing.git
   cd ai-data-processing ```
Create a virtual environment:

```bash

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate` ```
```
Install dependencies:

```bash
pip install -r requirements.txt
```

# Required Setup

## Google Sheets API
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the **Google Sheets API**.
4. Create **OAuth 2.0 credentials**.
5. Download `credentials.json` and place it in the project root.
6. Run the initial authorization script to generate `token.json`:

```bash
   Streamlit run app.py
```





