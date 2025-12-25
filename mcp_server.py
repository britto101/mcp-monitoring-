import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MCP Server")

# Load CSVs once
agreement = pd.read_csv("C:/Users/ANTHONY SAMY/Downloads/agreement_details.csv")
product = pd.read_csv("C:/Users/ANTHONY SAMY/Downloads/product_details.csv")
dealer = pd.read_csv("C:/Users/ANTHONY SAMY/Downloads/dealer_details.csv")
employee = pd.read_csv("C:/Users/ANTHONY SAMY/Downloads/employee_details.csv")
bounce = pd.read_csv("C:/Users/ANTHONY SAMY/Downloads/bounce_details.csv")
payment = pd.read_csv("C:/Users/ANTHONY SAMY/Downloads/payment_details.csv")

# Request model
class AgreementQuery(BaseModel):
    agreement_no: int

# MCP Endpoint: get master
@app.post("/get_master")
def get_master(query: AgreementQuery):
    a = agreement[agreement["agreement_no"] == query.agreement_no]
    m = a.merge(product, on="product_id", how="left") \
         .merge(dealer, on="dealer_id", how="left") \
         .merge(employee, on="employee_id", how="left")
    return m.to_dict(orient="records")[0]

# MCP Endpoint: get bounce count
@app.post("/get_bounce")
def get_bounce(query: AgreementQuery):
    count = len(bounce[bounce["agreement_no"] == query.agreement_no])
    return {"agreement_no": query.agreement_no, "bounce_count": count}

# MCP Endpoint: get DPD
@app.post("/get_dpd")
def get_dpd(query: AgreementQuery):
    row = payment[payment["agreement_no"] == query.agreement_no].iloc[0]
    due = pd.to_datetime(row["due_date"])
    paid = pd.to_datetime(row["payment_date"])
    dpd = (paid - due).days
    return {"agreement_no": query.agreement_no, "dpd": dpd}
