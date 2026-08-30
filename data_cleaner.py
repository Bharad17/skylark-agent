import pandas as pd
import numpy as np

class DataResilience:
    """
    Handles cleaning and normalizing messy real-world data from Monday.com boards.
    """
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
            
        df = df.copy()
        
        # 1. Replace empty strings or pure whitespace with NaN
        df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        
        # 2. Drop rows where all elements (except maybe Item ID/Name) are NaN
        cols_to_check = [col for col in df.columns if col not in ['Item Name', 'Item ID']]
        df.dropna(subset=cols_to_check, how='all', inplace=True)
        
        # 3. Normalize Date Columns
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
        # 4. Normalize Numeric Columns
        num_keywords = ['revenue', 'amount', 'value', 'price', 'cost']
        num_cols = [col for col in df.columns if any(kw in col.lower() for kw in num_keywords)]
        for col in num_cols:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace(r'[$,£€,]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        # 5. Normalize Categorical/Text Columns
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip().str.title()
                df[col].replace({'Nan': np.nan, 'None': np.nan, 'NaT': np.nan}, inplace=True)
                
        return df

    @staticmethod
    def generate_data_quality_report(df: pd.DataFrame, board_name: str) -> str:
        """Generates a summary of data quality issues for a given board."""
        if df.empty:
            return f"Data Quality Report for {board_name}: Board is empty."
            
        total_rows = len(df)
        report = []
        for col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                pct = (missing / total_rows) * 100
                report.append(f"- '{col}': {missing} missing values ({pct:.1f}%)")
                
        if not report:
            return f"Data Quality Report for {board_name}: No significant missing data detected."
            
        report_str = "\n".join(report)
        return f"Data Quality Report for {board_name} (Total rows: {total_rows}):\n{report_str}"
