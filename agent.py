import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from typing import Dict, List, Tuple
from monday_api import MondayAPIClient
from data_cleaner import DataResilience

class BIAgent:
    def __init__(self, api_token: str, work_orders_board_id: str, deals_board_id: str, gemini_api_key: str):
        self.monday_client = MondayAPIClient(api_token)
        self.work_orders_board_id = work_orders_board_id
        self.deals_board_id = deals_board_id
        self.gemini_api_key = gemini_api_key
        
        # Internal state
        self.work_orders_df = pd.DataFrame()
        self.deals_df = pd.DataFrame()
        self.quality_reports = []
        
        # LLM
        self.llm = ChatGoogleGenerativeAI(temperature=0, model="gemini-1.5-pro", google_api_key=self.gemini_api_key)
        self.agent_executor = None

    def fetch_and_prepare_data(self) -> str:
        """Fetches data from Monday, cleans it, and initializes the Pandas agent."""
        try:
            # Fetch
            raw_wo = self.monday_client.fetch_clean_dataframe(self.work_orders_board_id)
            raw_deals = self.monday_client.fetch_clean_dataframe(self.deals_board_id)
            
            # Clean
            self.work_orders_df = DataResilience.clean_dataframe(raw_wo)
            self.deals_df = DataResilience.clean_dataframe(raw_deals)
            
            # Generate quality reports
            wo_report = DataResilience.generate_data_quality_report(self.work_orders_df, "Work Orders")
            deals_report = DataResilience.generate_data_quality_report(self.deals_df, "Deals")
            self.quality_reports = [wo_report, deals_report]
            
            # Setup agent with both dataframes
            self.agent_executor = create_pandas_dataframe_agent(
                self.llm,
                [self.work_orders_df, self.deals_df],
                verbose=True,
                allow_dangerous_code=True,
                prefix="""You are a Founder-level Business Intelligence Agent. 
You have access to two pandas dataframes:
- `df1`: Work Orders Data (Project execution data)
- `df2`: Deals Data (Sales pipeline data)

When answering questions:
1. Always check the column names of both dataframes first using df1.columns and df2.columns.
2. If joining, find the appropriate keys (e.g., matching client names or IDs).
3. Provide context and insights, not just raw numbers. 
4. If a question is ambiguous (e.g. "How is our pipeline?"), ask a clarifying question instead of making assumptions.
5. Consider data quality issues (e.g. missing values) and mention them if they affect the result.
6. The user is a founder; they want concise, actionable, and accurate insights."""
            )
            return "Data successfully loaded and agent initialized."
        except Exception as e:
            return f"Error loading data: {str(e)}"

    def query(self, user_question: str) -> str:
        """Answers a user's question using the agent."""
        if self.agent_executor is None:
            return "Agent is not initialized. Please fetch data first."
            
        try:
            response = self.agent_executor.invoke({"input": user_question})
            return response.get("output", "I could not generate an answer.")
        except Exception as e:
            return f"An error occurred while answering the query: {str(e)}"

    def get_leadership_update(self) -> str:
        """Generates a high-level leadership update from the data."""
        prompt = """
        Generate a 'Leadership Update' executive summary based on the data.
        Include:
        1. Pipeline Health (Total value of deals, breakdown by status/sector if possible).
        2. Operational Metrics (Total work orders, completion status).
        3. Key Risks or Insights based on the data.
        
        Keep it professional, concise, and formatted in Markdown.
        """
        return self.query(prompt)
