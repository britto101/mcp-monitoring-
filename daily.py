import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# =========================
# LOAD AGREEMENT DATA
# =========================
try:
    agreement = pd.read_csv(
        "C:/Users/ANTHONY SAMY/Downloads/agreement_details.csv"
    )
    print(f"✓ Loaded {len(agreement)} agreements")
except FileNotFoundError:
    print("✗ Error: agreement_details.csv not found!")
    exit(1)
except Exception as e:
    print(f"✗ Error loading CSV: {e}")
    exit(1)

# Initialize results list
results = []

# =========================
# DATA COLLECTION + RISK LOGIC
# =========================
print("\nProcessing agreements...")
for idx, ag in enumerate(agreement["agreement_no"], 1):
    try:
        print(f"  [{idx}/{len(agreement)}] Processing {ag}...", end=" ")
        
        # Fetch data from APIs
        master = requests.post(
            "http://127.0.0.1:8000/get_master",
            json={"agreement_no": ag},
            timeout=10
        ).json()
        
        bounce = requests.post(
            "http://127.0.0.1:8000/get_bounce",
            json={"agreement_no": ag},
            timeout=10
        ).json()["bounce_count"]
        
        dpd = requests.post(
            "http://127.0.0.1:8000/get_dpd",
            json={"agreement_no": ag},
            timeout=10
        ).json()["dpd"]
        
        # Risk logic
        if dpd > 10 or bounce >= 2:
            if dpd > 30:
                risk = "HIGH RISK"
                action = "Legal Notice Triggered"
            else:
                risk = "MEDIUM RISK"
                action = "Reminder Mail Triggered"
            
            results.append({
                "agreement_no": ag,
                "DPD": dpd,
                "Bounce": bounce,
                "Risk": risk,
                "Action": action
            })
            print(f"✓ {risk}")
        else:
            print("✓ OK")
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection failed - Is API server running?")
    except requests.exceptions.Timeout:
        print(f"✗ Timeout")
    except KeyError as e:
        print(f"✗ Missing key in response: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")

print(f"\n✓ Found {len(results)} risky agreements")

# =========================
# SAVE DAILY CSV
# =========================
output_path = r"C:\Users\ANTHONY SAMY\Downloads\daily_risk_output.csv"

if results:
    try:
        output_df = pd.DataFrame(results)
        output_df.to_csv(output_path, index=False)
        print(f"✓ Saved report to {output_path}")
    except Exception as e:
        print(f"✗ Error saving CSV: {e}")
else:
    print("ℹ No risky agreements found - skipping CSV output")

# =========================
# EMAIL SENDING OPTIONS
# =========================

# OPTION 1: Gmail SMTP (Most Popular)
def send_via_gmail(body, csv_path=None):
    """Send email via Gmail SMTP"""
    
    # Gmail credentials - USE APP PASSWORD, NOT REGULAR PASSWORD
    sender_email = "arokiyabritto307@gmail.com"
    sender_password = "xhsh yoxa cysx mmvq"  # Remove spaces from app password
    receiver_email = "r4102777@gmail.com"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Daily Risk Alert - " + pd.Timestamp.now().strftime("%Y-%m-%d")
    
    # Email body
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach CSV if exists
    if csv_path and os.path.exists(csv_path):
        with open(csv_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(csv_path)}')
            msg.attach(part)
    
    try:
        # Connect to Gmail SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("✓ Mail sent successfully via Gmail")
        return True
    except smtplib.SMTPAuthenticationError:
        print("✗ Authentication failed - Check email/password")
        print("  Tip: Use App Password, not regular password!")
        print("  https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        print(f"✗ Gmail error: {e}")
        return False


# =========================
# SEND EMAIL
# =========================
if results:
    print("\nSending email report...")
    
    # Create email body
    body = f"""Daily Risk Report - {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}

Total Risky Agreements: {len(results)}

Details:
"""
    for r in results:
        body += f"\n• Agreement: {r['agreement_no']}"
        body += f"\n  DPD: {r['DPD']} days"
        body += f"\n  Bounce Count: {r['Bounce']}"
        body += f"\n  Risk Level: {r['Risk']}"
        body += f"\n  Action: {r['Action']}\n"
    
    body += f"\n\nFull report attached: daily_risk_output.csv"
    body += f"\n\n--- Automated Daily Risk Monitoring System ---"
    
    # Choose your email method:
    send_via_gmail(body, output_path)      # ✓ ENABLED - Use Gmail
    # send_via_outlook(body, output_path)    # Use this for Outlook
    # send_via_exchange(body, output_path)   # Use this for corporate email
else:
    print("ℹ No risky agreements - skipping email")

print("\n✓ Script completed!")
