import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MCP Server")

DATA_PATH = "data/"

agreement = pd.read_csv(DATA_PATH + "agreement_details.csv")
product = pd.read_csv(DATA_PATH + "product_details.csv")
dealer = pd.read_csv(DATA_PATH + "dealer_details.csv")
employee = pd.read_csv(DATA_PATH + "employee_details.csv")
bounce = pd.read_csv(DATA_PATH + "bounce_details.csv")
payment = pd.read_csv(DATA_PATH + "payment_details.csv")

class AgreementQuery(BaseModel):
    agreement_no: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/get_master")
def get_master(q: AgreementQuery):
    a = agreement[agreement["agreement_no"] == q.agreement_no]
    m = (
        a.merge(product, on="product_id", how="left")
         .merge(dealer, on="dealer_id", how="left")
         .merge(employee, on="employee_id", how="left")
    )
    return m.to_dict(orient="records")[0]

@app.post("/get_bounce")
def get_bounce(q: AgreementQuery):
    return {
        "agreement_no": q.agreement_no,
        "bounce_count": len(bounce[bounce["agreement_no"] == q.agreement_no])
    }

@app.post("/get_dpd")
def get_dpd(q: AgreementQuery):
    row = payment[payment["agreement_no"] == q.agreement_no].iloc[0]
    dpd = (pd.to_datetime(row["payment_date"]) -
           pd.to_datetime(row["due_date"])).days
    return {"agreement_no": q.agreement_no, "dpd": dpd}
