import pandas as pd
import requests

API = "http://127.0.0.1:8000"

agreement = pd.read_csv("data/agreement_details.csv")

results = []

for ag in agreement["agreement_no"]:
    master = requests.post(f"{API}/get_master", json={"agreement_no": ag}).json()
    bounce = requests.post(f"{API}/get_bounce", json={"agreement_no": ag}).json()["bounce_count"]
    dpd = requests.post(f"{API}/get_dpd", json={"agreement_no": ag}).json()["dpd"]

    if dpd > 30:
        risk, action = "HIGH", "Legal Notice"
    elif dpd > 10 or bounce >= 2:
        risk, action = "MEDIUM", "Reminder Mail"
    else:
        continue

    results.append({
        "agreement_no": ag,
        "dpd": dpd,
        "bounce": bounce,
        "risk": risk,
        "action": action
    })

if results:
    df = pd.DataFrame(results)
    df.to_csv("daily_risk_output.csv", index=False)
    print("✅ Daily risk file generated")
else:
    print("ℹ No risky agreements today")
