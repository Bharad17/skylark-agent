import requests
import pandas as pd
from typing import List, Dict, Any, Optional

MONDAY_API_URL = "https://api.monday.com/v2"

class MondayAPIClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            "Authorization": self.api_token,
            "API-Version": "2023-10",
            "Content-Type": "application/json"
        }

    def _run_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(MONDAY_API_URL, json=payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.text}")
        
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
            
        return data

    def get_boards(self) -> List[Dict[str, Any]]:
        """Fetch all boards available to the user."""
        query = """
        query {
            boards(limit: 100) {
                id
                name
            }
        }
        """
        response = self._run_query(query)
        return response.get("data", {}).get("boards", [])

    def get_board_items(self, board_id: str) -> List[Dict[str, Any]]:
        """Fetch all items for a given board using pagination."""
        items = []
        
        # Initial query
        query = """
        query($board_id: [ID!]) {
            boards(ids: $board_id) {
                items_page(limit: 100) {
                    cursor
                    items {
                        id
                        name
                        column_values {
                            id
                            type
                            text
                        }
                    }
                }
            }
        }
        """
        variables = {"board_id": [board_id]}
        response = self._run_query(query, variables)
        
        board_data = response.get("data", {}).get("boards", [])
        if not board_data:
            return items
            
        items_page = board_data[0].get("items_page", {})
        current_items = items_page.get("items", [])
        items.extend(current_items)
        cursor = items_page.get("cursor")
        
        # Pagination
        while cursor:
            next_query = """
            query($cursor: String!) {
                next_items_page(limit: 100, cursor: $cursor) {
                    cursor
                    items {
                        id
                        name
                        column_values {
                            id
                            type
                            text
                        }
                    }
                }
            }
            """
            next_vars = {"cursor": cursor}
            next_response = self._run_query(next_query, next_vars)
            
            next_page = next_response.get("data", {}).get("next_items_page", {})
            current_items = next_page.get("items", [])
            items.extend(current_items)
            cursor = next_page.get("cursor")
            
        return items

    def fetch_board_as_dataframe(self, board_id: str) -> pd.DataFrame:
        """Fetch board items and convert to a cleaned Pandas DataFrame."""
        items = self.get_board_items(board_id)
        if not items:
            return pd.DataFrame()
            
        records = []
        for item in items:
            record = {"Item Name": item.get("name", ""), "Item ID": item.get("id", "")}
            for col in item.get("column_values", []):
                record[col["id"]] = col.get("text", "")
            records.append(record)
            
        return pd.DataFrame(records)

    def get_board_columns(self, board_id: str) -> Dict[str, str]:
        """Fetch mapping of column ID to column Title."""
        query = """
        query($board_id: [ID!]) {
            boards(ids: $board_id) {
                columns {
                    id
                    title
                }
            }
        }
        """
        variables = {"board_id": [board_id]}
        response = self._run_query(query, variables)
        boards = response.get("data", {}).get("boards", [])
        if not boards:
            return {}
            
        mapping = {}
        for col in boards[0].get("columns", []):
            mapping[col["id"]] = col["title"]
        return mapping
        
    def fetch_clean_dataframe(self, board_id: str) -> pd.DataFrame:
        """Fetch data and rename columns using actual titles."""
        df = self.fetch_board_as_dataframe(board_id)
        if df.empty:
            return df
            
        col_mapping = self.get_board_columns(board_id)
        rename_dict = {k: v for k, v in col_mapping.items() if k in df.columns}
        df.rename(columns=rename_dict, inplace=True)
        
        return df
