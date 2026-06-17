import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="Zero-Touch IT Operations Platform",
    page_icon="⚙️",
    layout="wide"
)

st.title("Zero-Touch IT Operations Platform")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "HR Onboarding Portal",
        "HR Offboarding Portal",
        "Fleet Reliability & Compliance",
        "Observability & Data Integrity",
        "Tier 3 Escalation & SOPs",
        "JumpCloud Automation",
        "SentinelOne Security Operations",
    ]
)
with tab7:
    st.header("SentinelOne Security Operations")

    st.info(
        "SentinelOne integration is API-ready. "
        "If credentials are missing, the backend returns not_configured safely."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Get SentinelOne Agents"):
            response = requests.get(f"{API_URL}/sentinelone/agents")
            if response.status_code == 200:
                st.success("Agent inventory loaded")
                st.json(response.json())
            else:
                st.error(response.text)

    with col2:
        if st.button("Get Threats"):
            response = requests.get(f"{API_URL}/sentinelone/threats")
            if response.status_code == 200:
                st.success("Threats loaded")
                st.json(response.json())
            else:
                st.error(response.text)

    with col3:
        if st.button("Get Activities"):
            response = requests.get(f"{API_URL}/sentinelone/activities")
            if response.status_code == 200:
                st.success("Activities loaded")
                st.json(response.json())
            else:
                st.error(response.text)

    st.divider()

    st.subheader("Endpoint Protection Summary")

    if st.button("Generate SentinelOne Security Summary"):
        response = requests.get(f"{API_URL}/sentinelone/summary")
        if response.status_code == 200:
            st.success("Security summary generated")
            st.json(response.json())
        else:
            st.error(response.text)

    st.divider()

    st.subheader("Check Agent Status")

    s1_hostname = st.text_input(
        "Device Hostname",
        value="LAPTOP-7UU6G70R",
        key="s1_hostname",
    )

    if st.button("Check SentinelOne Agent Status"):
        response = requests.get(f"{API_URL}/sentinelone/agents/{s1_hostname}")
        if response.status_code == 200:
            st.success("Agent status lookup completed")
            st.json(response.json())
        else:
            st.error(response.text)

    st.divider()

    st.subheader("Endpoint Isolation Guardrail")

    isolate_hostname = st.text_input(
        "Hostname to isolate",
        value="LAPTOP-7UU6G70R",
        key="s1_isolate_hostname",
    )

    if st.button("Request Endpoint Isolation"):
        response = requests.post(
            f"{API_URL}/sentinelone/isolate/{isolate_hostname}"
        )

        if response.status_code == 200:
            st.success("Isolation request evaluated")
            st.json(response.json())
        else:
            st.error(response.text)