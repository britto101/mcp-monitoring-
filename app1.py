import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000"

agreement = pd.read_csv("C:/Users/ANTHONY SAMY/Downloads/agreement_details.csv")
product = pd.read_csv("C:/Users/ANTHONY SAMY/Downloads/product_details.csv")
dealer = pd.read_csv("C:/Users/ANTHONY SAMY/Downloads/dealer_details.csv")
employee = pd.read_csv("C:/Users/ANTHONY SAMY/Downloads/employee_details.csv")

st.set_page_config(page_title="Customer MCP Automation", layout="centered")
st.title("📊 Customer MCP Automation Table View")

user_input = st.text_input(
    "Enter anything related to customer (name, agreement no, product, dealer):"
)

if st.button("Search") and user_input:
    matches = set()

    # Agreement no
    if user_input.isdigit():
        matches.add(int(user_input))

    # Customer name
    if "customer_name" in agreement.columns:
        matches.update(
            agreement[
                agreement["customer_name"]
                .str.contains(user_input, case=False, na=False)
            ]["agreement_no"].tolist()
        )

    # Product
    prod_ids = product[
        product["product_name"].str.contains(user_input, case=False, na=False)
    ]["product_id"]
    matches.update(
        agreement[agreement["product_id"].isin(prod_ids)]["agreement_no"]
    )

    # Dealer
    dealer_ids = dealer[
        dealer["dealer_name"].str.contains(user_input, case=False, na=False)
    ]["dealer_id"]
    matches.update(
        agreement[agreement["dealer_id"].isin(dealer_ids)]["agreement_no"]
    )

    # Employee
    emp_ids = employee[
        employee["employee_name"].str.contains(user_input, case=False, na=False)
    ]["employee_id"]
    matches.update(
        agreement[agreement["employee_id"].isin(emp_ids)]["agreement_no"]
    )

    if matches:
        output_list = []

        for ag_no in matches:
            try:
                master = requests.post(
                    f"{API_URL}/get_master",
                    json={"agreement_no": ag_no}
                ).json()

                bounce = requests.post(
                    f"{API_URL}/get_bounce",
                    json={"agreement_no": ag_no}
                ).json()["bounce_count"]

                dpd = requests.post(
                    f"{API_URL}/get_dpd",
                    json={"agreement_no": ag_no}
                ).json()["dpd"]

                if dpd > 30:
                    risk = "HIGH RISK"
                    action = "Legal Notice Triggered"
                elif dpd > 10 or bounce >= 2:
                    risk = "MEDIUM RISK"
                    action = "Reminder Mail Triggered"
                else:
                    risk = "LOW RISK"
                    action = "No Mail Required"

                master.update({
                    "Bounce Count": bounce,
                    "DPD": dpd,
                    "Risk Level": risk,
                    "Action Taken": action
                })

                output_list.append(master)

            except Exception as e:
                st.error(f"Error for agreement {ag_no}: {e}")

        st.subheader("Matching Agreements")
        st.dataframe(pd.DataFrame(output_list))
    else:
        st.warning("No matching agreements found.")
