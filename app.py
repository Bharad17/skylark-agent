import streamlit as st
import os
from dotenv import load_dotenv
from agent import BIAgent

# Load environment variables from .env file if it exists
load_dotenv()

st.set_page_config(page_title="Monday.com BI Agent", page_icon="📊", layout="wide")

st.title("📊 Monday.com Founder-Level BI Agent")
st.markdown("Ask natural language questions about your Work Orders and Deals data.")

# Check for secrets in environment or Streamlit secrets
def get_secret(key):
    if key in st.secrets:
        return st.secrets[key]
    return os.environ.get(key, "")

env_api_token = get_secret("MONDAY_API_TOKEN")
env_wo_board = get_secret("WORK_ORDERS_BOARD_ID")
env_deals_board = get_secret("DEALS_BOARD_ID")
env_gemini_key = get_secret("GEMINI_API_KEY")

has_all_secrets = bool(env_api_token and env_wo_board and env_deals_board and env_gemini_key)

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    if not has_all_secrets:
        st.info("Please enter your credentials to connect.")
        api_token = st.text_input("Monday.com API Token", type="password")
        wo_board_id = st.text_input("Work Orders Board ID")
        deals_board_id = st.text_input("Deals Board ID")
        gemini_key = st.text_input("Gemini API Key", type="password")
        connect_pressed = st.button("Connect & Load Data")
    else:
        st.success("Connected via Secure Cloud Secrets!")
        api_token = env_api_token
        wo_board_id = env_wo_board
        deals_board_id = env_deals_board
        gemini_key = env_gemini_key
        # Automatically trigger connect if secrets exist and not yet connected
        connect_pressed = "bi_agent" not in st.session_state

    if connect_pressed:
        if not (api_token and wo_board_id and deals_board_id and gemini_key):
            st.error("Please fill in all configuration fields.")
        else:
            with st.spinner("Fetching and preparing data..."):
                agent = BIAgent(api_token, wo_board_id, deals_board_id, gemini_key)
                status = agent.fetch_and_prepare_data()
                if "Error" in status:
                    st.error(status)
                else:
                    st.session_state["bi_agent"] = agent
                    st.success("Successfully connected to Monday.com!")
                    st.session_state["messages"] = [
                        {"role": "assistant", "content": "Hello! I have loaded your Work Orders and Deals data. What business question can I answer for you today?"}
                    ]
                    
    if "bi_agent" in st.session_state:
        st.markdown("---")
        st.subheader("Data Quality Caveats")
        for report in st.session_state["bi_agent"].quality_reports:
            with st.expander(f"Quality Report"):
                st.text(report)
                
        st.markdown("---")
        st.subheader("Export Cleaned Data")
        wo_csv = st.session_state["bi_agent"].work_orders_df.to_csv(index=False).encode('utf-8')
        deals_csv = st.session_state["bi_agent"].deals_df.to_csv(index=False).encode('utf-8')
        
        st.download_button("📥 Download Work Orders (CSV)", data=wo_csv, file_name="clean_work_orders.csv", mime="text/csv")
        st.download_button("📥 Download Deals (CSV)", data=deals_csv, file_name="clean_deals.csv", mime="text/csv")
                
        st.markdown("---")
        if st.button("Generate Leadership Update"):
            with st.spinner("Generating update..."):
                update = st.session_state["bi_agent"].get_leadership_update()
                st.session_state["messages"].append({"role": "user", "content": "Generate a Leadership Update."})
                st.session_state["messages"].append({"role": "assistant", "content": update})
                st.rerun()

# Main Chat Interface
if "messages" not in st.session_state:
    st.info("Please connect to Monday.com using the sidebar to begin.")
else:
    # Display chat messages
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if user_query := st.chat_input("E.g., How's our pipeline looking for the energy sector this quarter?"):
        # Add user message to state
        st.session_state["messages"].append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                agent = st.session_state["bi_agent"]
                response = agent.query(user_query)
                st.markdown(response)
                st.session_state["messages"].append({"role": "assistant", "content": response})
