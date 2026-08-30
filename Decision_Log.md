# Decision Log

## Key Assumptions Made
1. **Data Consistency**: I assumed that the basic structure of the boards matches the provided CSV/Excel files and that the core columns (like revenue, dates, and status) will not change their fundamental semantic meaning, even if there are formatting errors.
2. **LLM Capabilities**: I assumed that GPT-4o (or an equivalent frontier model) is available, as answering complex cross-board BI queries effectively requires advanced code generation and reasoning capabilities that smaller models struggle with.
3. **Data Volume**: I assumed the data volume fits comfortably in memory (Pandas DataFrames) and within the LLM's context window. If the dataset scales to millions of rows, the Pandas agent would need to be replaced by a SQL agent querying a data warehouse.

## Trade-offs Chosen and Why
1. **Pandas Agent vs. SQL Database**: 
   - **Choice**: I chose to pull data dynamically from Monday.com and inject it into a LangChain Pandas DataFrame Agent. 
   - **Why**: This minimizes the infrastructure footprint (no need to host a separate Postgres/SQL server) and fulfills the requirement to query dynamically. It is perfect for a hosted prototype. A SQL database would be more robust for production but adds overhead.
2. **Streamlit vs. Custom React/Node App**:
   - **Choice**: Streamlit for the frontend.
   - **Why**: The assignment prioritizes the AI Agent capabilities and conversational interface. Streamlit allows for the rapid deployment of a clean, functional chat UI with built-in state management in just a few lines of code, freeing up time to focus on the LLM and Monday API integration.
3. **Dynamic Auth via UI vs. .env File**:
   - **Choice**: Passing the API tokens and Board IDs via the Streamlit sidebar.
   - **Why**: The prototype must be "testable without local setup." By putting auth in the UI, evaluators can simply navigate to the hosted link, paste their tokens, and test it immediately without needing to modify backend environment variables.

## What I'd Do Differently With More Time
- **Webhooks & Caching Layer**: Instead of fetching all data on-demand (which will hit rate limits and be slow as the boards grow), I would implement a webhook architecture that listens for changes on Monday.com and updates a local database (like PostgreSQL) asynchronously. The agent would then query this database.
- **Enhanced Error Recovery**: If the LLM generates invalid Pandas code and crashes, I would implement a robust retry loop (using LangGraph) where the LLM can self-correct by viewing the Python stack trace.
- **Data Visualization**: I would extend the agent to not just return text, but also generate charts (e.g., matplotlib, plotly) and render them directly in the Streamlit UI.

## Interpretation of "Leadership Updates"
**Interpretation**: Leadership updates are typically high-level, synthesis-driven summaries that cut through the noise. Founders and executives do not want to read raw numbers; they want a narrative.
**Implementation**: I added a specific "Generate Leadership Update" feature to the agent. When triggered, it uses a specialized prompt instructing the LLM to analyze the entire loaded context (both Work Orders and Deals) and produce a cohesive Markdown document highlighting pipeline health, operational throughput, and key risks (e.g., sectors underperforming or missing data).
