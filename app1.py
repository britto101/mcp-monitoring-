import streamlit as st
import pandas as pd
import requests

API = "http://localhost:8000"

st.set_page_config("Customer MCP Automation")
st.title("📊 Customer MCP Automation")

query = st.text_input("Enter agreement no / name / dealer")

if st.button("Search") and query:
    agreement = pd.read_csv("data/agreement_details.csv")

    matches = agreement["agreement_no"].astype(str).str.contains(query)

    for ag in agreement[matches]["agreement_no"]:
        master = requests.post(f"{API}/get_master", json={"agreement_no": ag}).json()
        bounce = requests.post(f"{API}/get_bounce", json={"agreement_no": ag}).json()["bounce_count"]
        dpd = requests.post(f"{API}/get_dpd", json={"agreement_no": ag}).json()["dpd"]

        master["Bounce"] = bounce
        master["DPD"] = dpd

        st.json(master)
