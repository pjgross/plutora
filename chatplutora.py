import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType
from langchain_ollama import Ollama
import io

# -------------------------------
# STEP 1: Prepare example DataFrames
# -------------------------------
sales = pd.DataFrame({
    "region": ["North", "South", "East", "West"],
    "sales": [1000, 1500, 800, 1200]
})

customers = pd.DataFrame({
    "region": ["North", "South", "East", "West"],
    "customers": [40, 55, 30, 45]
})

inventory = pd.DataFrame({
    "region": ["North", "South", "East", "West"],
    "stock": [300, 250, 400, 350]
})

datastore = {
    "sales": sales,
    "customers": customers,
    "inventory": inventory
}

# -------------------------------
# STEP 2: Define Tools
# -------------------------------

@tool("get_table_summary", return_direct=False)
def get_table_summary(table_name: str) -> str:
    """Return the first few rows and summary stats of a specific table."""
    if table_name not in datastore:
        return f"Table '{table_name}' not found. Available: {list(datastore.keys())}"
    df = datastore[table_name]
    summary = df.describe(include="all").to_string()
    head = df.head().to_string()
    return f"Table: {table_name}\n\nHead:\n{head}\n\nSummary:\n{summary}"


@tool("analyze_data", return_direct=False)
def analyze_data(code: str) -> str:
    """
    Execute user-provided Python code using the DataFrames (sales, customers, inventory).
    If a Matplotlib figure is created, it will be displayed in Streamlit.
    """
    local_env = {"sales": sales, "customers": customers, "inventory": inventory, "pd": pd, "plt": plt, "io": io}
    try:
        exec(code, {}, local_env)

        # If the code created a matplotlib figure, show it
        fig = plt.gcf()
        if fig.get_axes():
            st.pyplot(fig)
            plt.clf()

        result = local_env.get("result", "No result variable found.")
        return str(result)
    except Exception as e:
        return f"Error executing code: {e}"

# -------------------------------
# STEP 3: Initialize Ollama agent
# -------------------------------

llm = Ollama(model="llama3")  # You can switch to mistral or phi3 if preferred
tools = [get_table_summary, analyze_data]

agent = initialize_agent(
    tools,
    llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# -------------------------------
# STEP 4: Streamlit UI
# -------------------------------
st.set_page_config(page_title="Ollama + Pandas AI", layout="wide")

st.title("🦙 Ollama + LangChain + Pandas Visual Analyzer")
st.write("Ask questions about your datasets — charts and analysis will appear below.")

# Display available datasets
st.sidebar.header("Available DataFrames")
for name, df in datastore.items():
    st.sidebar.write(f"**{name}** ({len(df)} rows)")
    st.sidebar.dataframe(df)

# User input
user_query = st.text_area("Enter your question or analysis prompt:", height=120)

if st.button("Run Analysis"):
    with st.spinner("Thinking..."):
        response = agent.run(user_query)
        st.subheader("🧩 Result")
        st.write(response)