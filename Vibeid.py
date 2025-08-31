# app.py
import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="VibeID Prototype", page_icon="🔐", layout="wide")

# ---------- Helpers ----------
def seed_logs():
    """Create some seed logs for demo (only first run)."""
    if "logs" not in st.session_state:
        st.session_state["logs"] = []
        sample = [
            {"timestamp":"2025-08-01 09:23:00","username":"rahul","device":"Trusted Device","location":"Ujjain","ip":"103.23.12.5",
             "amount":250,"time":"09:23","typing":85,"pattern":"consistent","network":"normal","risk":22,"status":"GRANTED","reason":"Low-risk"},
            {"timestamp":"2025-08-01 02:12:00","username":"sara","device":"New Device","location":"Delhi","ip":"89.12.98.1",
             "amount":15000,"time":"02:12","typing":42,"pattern":"erratic","network":"proxy","risk":78,"status":"BLOCKED","reason":"Unusual location + high amount"},
            {"timestamp":"2025-08-01 23:50:00","username":"amit","device":"Suspicious Device","location":"Ujjain","ip":"103.23.12.5",
             "amount":5000,"time":"23:50","typing":55,"pattern":"slower","network":"normal","risk":48,"status":"VERIFY","reason":"New device + odd hour"},
        ]
        st.session_state["logs"].extend(sample)

def compute_risk(params):
    """Compute an interpretable risk score (0-100) from params dict."""
    score = 10  # base
    # device trust
    if params["device"] == "New Device":
        score += 15
    elif params["device"] == "Suspicious Device":
        score += 28
    # location / IP anomalies
    if params["location_match"] == "Unusual":
        score += 20
    if params["network"] in ["vpn","tor","proxy"]:
        score += 25
    # typing behavior
    if params["typing_speed"] < 40 or params["typing_speed"] > 110:
        score += 10
    if params["typing_pattern"] == "erratic":
        score += 12
    # transaction amount
    if params["amount"] > 10000:
        score += 12
    elif params["amount"] > 5000:
        score += 6
    # login time (odd hours)
    if params["login_hour"] < 6 or params["login_hour"] > 23:
        if not params["usual_hours"]:
            score += 10
    # frequency (if many tx in short time) - simulated flag
    if params.get("freq_anomaly"):
        score += 15
    # cap
    return min(score, 100)

def decision_from_score(score):
    if score < 40:
        return "GRANTED"
    if 40 <= score <= 69:
        return "VERIFY"
    return "BLOCKED"

def nice_reason(params, score):
    reasons = []
    if params["device"] != "Trusted Device":
        reasons.append(params["device"])
    if params["location_match"] == "Unusual":
        reasons.append("Location mismatch")
    if params["network"] in ["vpn","proxy","tor"]:
        reasons.append("Network anomaly")
    if params["typing_pattern"] == "erratic":
        reasons.append("Typing pattern anomaly")
    if params["amount"] > 10000:
        reasons.append("High amount")
    if score >= 70:
        reasons.append("High risk score")
    return " • ".join(reasons) if reasons else "No major anomaly"

# ---------- UI ----------
seed_logs()
st.title("🔐 VibeID — PS09 Prototype (User + Admin)")

mode = st.sidebar.radio("Choose view", ["User (Simulate Transaction)", "Admin Dashboard", "About / Readme"])

if mode == "User (Simulate Transaction)":
    st.header("User Simulation — Transaction & Behavioral Capture")
    with st.form("tx_form"):
        col1, col2 = st.columns([2,1])
        with col1:
            username = st.text_input("👤 Username")
            merchant = st.text_input("🏪 Merchant (optional)")
            amount = st.number_input("💰 Transaction Amount (₹)", min_value=1, value=500, step=100)
            location = st.selectbox("📍 Location (reported by device)", ["Ujjain","Indore","Bhopal","Delhi","Mumbai","Other"])
        with col2:
            device = st.selectbox("📱 Device Confidence", ["Trusted Device","New Device","Suspicious Device (jailbroken/emulator)"])
            network = st.selectbox("🌐 Network", ["normal","vpn","proxy","tor"])
            login_time = st.time_input("⏱ Login Time", value=datetime.now().time())
            usual_hours = st.checkbox("🕘 This is within user's usual login hours?", value=True)
            typing_speed = st.slider("⌨️ Typing speed (keystrokes/min)", min_value=10, max_value=200, value=random.randint(40,100))
            typing_pattern = st.selectbox("✍️ Typing pattern", ["consistent","slower","erratic"])
            freq_anom = st.checkbox("⚡ Simulate high-frequency transactions recently?", value=False)
        submit = st.form_submit_button("Simulate Transaction")

    if submit:
        if not username:
            st.warning("Enter username to simulate")
        else:
            # prepare params
            params = {
                "username": username,
                "amount": amount,
                "device": device,
                "network": network,
                "location": location,
                "typing_speed": typing_speed,
                "typing_pattern": typing_pattern,
                "login_hour": login_time.hour,
                "usual_hours": usual_hours,
                "location_match": "Normal" if location in ["Ujjain","Indore","Bhopal"] else "Unusual",
                "freq_anomaly": freq_anom
            }

            # compute risk
            risk = compute_risk(params)
            status = decision_from_score(risk)
            reason = nice_reason(params, risk)
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # store in logs
            entry = {
                "timestamp": ts,
                "username": username,
                "device": device,
                "location": location,
                "ip": f"{random.randint(20,220)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "amount": amount,
                "time": login_time.strftime("%H:%M"),
                "typing": typing_speed,
                "typing_pattern": typing_pattern,
                "network": network,
                "risk": risk,
                "status": status,
                "reason": reason
            }
            st.session_state["logs"].insert(0, entry)  # newest first

            # Display to user
            st.markdown("### 🔎 Risk Analysis Result")
            colA, colB = st.columns([2,1])
            with colA:
                st.write(f"**Username:** {username}")
                st.write(f"**Device:** {device}")
                st.write(f"**Network:** {network}")
                st.write(f"**Location:** {location} ({params['location_match']})")
                st.write(f"**Typing (kpm):** {typing_speed} — {typing_pattern}")
                st.write(f"**Transaction Amount:** ₹{amount}")
                st.write(f"**Reason:** {reason}")
            with colB:
                st.metric("Risk Score", f"{risk}/100")
                st.progress(int(risk))
                if status == "GRANTED":
                    st.success("✅ Transaction Approved")
                elif status == "VERIFY":
                    st.warning("🔑 Secondary Verification Required")
                    otp = st.text_input("Enter OTP (demo)", type="password")
                    if otp:
                        st.success("✅ OTP Verified — Transaction Approved (demo)")
                        # update log entry status to GRANTED after otp
                        st.session_state["logs"][0]["status"] = "GRANTED"
                else:
                    st.error("🚫 Transaction Blocked — Cyber Alert Triggered")
                    st.warning("This event has been flagged in Admin dashboard (demo).")

            st.info("Note: This is a demo simulation. Real system will capture signals silently and with privacy.")

elif mode == "Admin Dashboard":
    st.header("Admin — Control Room / Fraud Monitoring Console")
    logs = st.session_state.get("logs", [])
    df = pd.DataFrame(logs)
    # metrics
    total = len(df)
    blocked = df[df["status"] == "BLOCKED"].shape[0] if not df.empty else 0
    verify = df[df["status"] == "VERIFY"].shape[0] if not df.empty else 0
    granted = df[df["status"] == "GRANTED"].shape[0] if not df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Attempts", total)
    col2.metric("Blocked (🚫)", blocked)
    col3.metric("Verify Required (🔑)", verify)
    col4.metric("Granted (✅)", granted)

    # Alerts banner if any blocked
    if blocked > 0:
        st.error(f"🚨 ALERT: {blocked} blocked suspicious session(s) detected — immediate review recommended")

    st.subheader("Recent Logs")
    if not df.empty:
        # show a concise table for admins
        display_df = df[["timestamp","username","ip","device","location","amount","risk","status","reason"]].copy()
        display_df["risk"] = display_df["risk"].astype(int)
        st.dataframe(display_df, height=300)

        # charts
        st.subheader("Risk Distribution (sample)")
        fig, ax = plt.subplots(1,2, figsize=(10,4))
        # bar of risk buckets
        buckets = [
            ("Normal <40", df[df["risk"] < 40].shape[0]),
            ("Suspicious 40-69", df[(df["risk"] >= 40) & (df["risk"] <=69)].shape[0]),
            ("Blocked 70+", df[df["risk"] >= 70].shape[0])
        ]
        names = [b[0] for b in buckets]
        vals = [b[1] for b in buckets]
        ax[0].bar(names, vals, color=["#4CAF50","#FFC107","#F44336"])
        ax[0].set_ylabel("Count")
        ax[0].set_title("Risk Buckets")

        # time-series: attempts by hour
        if "timestamp" in df.columns:
            df_ts = df.copy()
            df_ts["hour"] = pd.to_datetime(df_ts["timestamp"]).dt.hour
            hourly = df_ts.groupby("hour").size()
            ax[1].plot(hourly.index, hourly.values, marker="o")
            ax[1].set_title("Attempts by Hour")
            ax[1].set_xlabel("Hour")
        st.pyplot(fig)

    else:
        st.info("No logs yet. Simulate some transactions from User view.")

    # Admin actions: mark resolved or export
    st.subheader("Admin Actions")
    if not df.empty:
        idx = st.number_input("Select log index to mark resolved (0 = newest)", min_value=0, max_value=max(0,len(df)-1), value=0)
        if st.button("Mark as Resolved"):
            st.session_state["logs"][idx]["status"] = "RESOLVED"
            st.success("Marked resolved.")
    if st.button("Export logs as CSV"):
        df.to_csv("vibeid_logs.csv", index=False)
        with open("vibeid_logs.csv","rb") as f:
            st.download_button("Download CSV", data=f, file_name="vibeid_logs.csv", mime="text/csv")

else:
    st.header("About VibeID Prototype")
    st.markdown(
        """**VibeID** is a demo prototype for Hackathon PS-09: AI Model for Flagging Suspicious Transactions.

This prototype demonstrates:
- Behavioral & contextual signal capture (simulated).
- Real-time risk scoring & decisioning.
- Admin dashboard with logs, metrics & charts.
- OTP flow for medium-risk transactions (simulated).

How to deploy:
1. Push this `app.py` to a GitHub repo.
2. Add `requirements.txt` containing:
   streamlit
   matplotlib
   pandas
   numpy
3. Connect repo to Streamlit Cloud (https://share.streamlit.io) and deploy.

Notes:
- This is a simulation for demo. Real system will rely on real signals (keystroke streams, device fingerprinting, secure telemetry) and privacy-preserving storage.
- Admin and user interfaces will be separated in production with secure APIs and access control.

Contact: Atharva Dubey — Team VibeID
"""
        )
