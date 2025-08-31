import streamlit as st
import random
import matplotlib.pyplot as plt

st.set_page_config(page_title="VibeID Prototype", page_icon="🔐", layout="centered")

st.title("🔐 VibeID – AI Adaptive Authentication Prototype")
st.write("Demo prototype for **Hackathon 2025** – Problem Statement 09")

# User Input
username = st.text_input("👤 Enter Username")
transaction_amount = st.number_input("💰 Enter Transaction Amount (₹)", min_value=1, value=500)

if st.button("Login Attempt"):
    if not username:
        st.warning("⚠️ Please enter username")
    else:
        # Mock behavioral parameters
        typing_speed = random.randint(30, 120)  # keystrokes/min
        device_trust = random.choice(["Trusted Device", "New Device", "Suspicious Device"])
        location_match = random.choice(["Normal Location", "Unusual Location"])

        # Risk score logic
        base_score = random.randint(10, 60)
        if device_trust == "New Device":
            base_score += 15
        if device_trust == "Suspicious Device":
            base_score += 25
        if location_match == "Unusual Location":
            base_score += 20
        if transaction_amount > 10000:
            base_score += 10

        risk_score = min(base_score, 100)

        # Display results
        st.subheader("📊 Risk Analysis")
        st.write(f"**Username:** {username}")
        st.write(f"**Typing Speed:** {typing_speed} keystrokes/min")
        st.write(f"**Device Status:** {device_trust}")
        st.write(f"**Location Check:** {location_match}")
        st.write(f"**Transaction Amount:** ₹{transaction_amount}")

        # Risk Meter
        st.progress(risk_score / 100)
        st.metric("Risk Score", f"{risk_score}/100")

        # Decision
        if risk_score < 40:
            st.success("✅ Access Granted")
        elif 40 <= risk_score <= 69:
            st.warning("🔑 Secondary Verification Required (OTP/Biometric)")
            otp = st.text_input("Enter OTP for Verification", type="password")
            if otp:
                st.success("✅ OTP Verified – Access Granted")
        else:
            st.error("🚫 Session Blocked & Cyber Alert Triggered")

        # Visualization - Pie Chart
        st.subheader("📈 Transaction Risk Distribution (Sample Data)")
        labels = ["Normal (<40)", "Suspicious (40–69)", "Blocked (70+)"]
        values = [
            random.randint(10, 30),
            random.randint(5, 20),
            random.randint(1, 10)
        ]
        colors = ["#4CAF50", "#FFC107", "#F44336"]

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
# Online Python - IDE, Editor, Compiler, Interpreter

def sum(a, b):
    return (a + b)

a = int(input('Enter 1st number: '))
b = int(input('Enter 2nd number: '))

print(f'Sum of {a} and {b} is {sum(a, b)}')
