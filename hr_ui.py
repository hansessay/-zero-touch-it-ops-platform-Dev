import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Zero-Touch IT Operations Platform",
    page_icon="🧑‍💼",
    layout="wide"
)

st.title("Zero-Touch IT Operations Platform")
st.subheader("HR Offboarding Portal")

with st.form("offboarding_form"):

    email = st.text_input("Employee Email")

    manager_email = st.text_input("Manager Email")

    reason = st.selectbox(
        "Reason",
        [
            "termination",
            "resignation",
            "contract_end"
        ]
    )

    transfer_owner = st.text_input(
        "Transfer ownership to"
    )

    submitted = st.form_submit_button(
        "Start Offboarding"
    )

if submitted:

    payload = {
        "email": email,
        "manager_email": manager_email,
        "reason": reason,
        "transfer_owner": transfer_owner
    }

    response = requests.post(
        f"{API_URL}/offboarding/start",
        json=payload
    )

    if response.status_code == 200:
        st.success("Offboarding completed")
        st.json(response.json())
    else:
        st.error(response.text)

st.divider()

if st.button("Show Workflow History"):

    response = requests.get(
        f"{API_URL}/workflows/history"
    )

    if response.status_code == 200:
        st.json(response.json())

if st.button("Show Audit Log"):

    response = requests.get(
        f"{API_URL}/audit"
    )

    if response.status_code == 200:
        st.json(response.json())