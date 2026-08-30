# Monday.com Business Intelligence Agent

An AI agent that answers founder-level business intelligence queries by integrating with Monday.com boards containing Work Orders and Deals data.

## Features
- **Conversational Interface**: Built with Streamlit for a user-friendly chat experience.
- **Dynamic Monday.com Integration**: Uses the Monday API (v2) to fetch board data securely on-the-fly. No hardcoded data.
- **Data Resilience**: Gracefully handles missing values, inconsistent text formatting, and date parsing through a preprocessing pipeline before passing data to the LLM agent.
- **Query Understanding**: Leverages LangChain and Google's Gemini 1.5 Pro to analyze data using Pandas. It asks clarifying questions if a user prompt is ambiguous.
- **Leadership Updates**: A dedicated feature to generate high-level pipeline and operational summaries.

## Architecture
1. **Frontend**: Streamlit (`app.py`) provides the UI and session management.
2. **Integration**: `monday_api.py` fetches data dynamically using GraphQL queries with pagination support.
3. **Data Preprocessing**: `data_cleaner.py` handles parsing and normalizes messy business data (e.g., currency strings, dates, and nulls) into clean Pandas DataFrames.
4. **Agent Orchestration**: `agent.py` uses `langchain-experimental`'s `create_pandas_dataframe_agent` to query across the Deals and Work Orders DataFrames simultaneously. 

## Local Setup Instructions

1. **Clone or Download the Repository**
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application**
   ```bash
   streamlit run app.py
   ```
