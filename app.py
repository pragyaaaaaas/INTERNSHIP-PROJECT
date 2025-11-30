 

import streamlit as st
import requests
import pandas as pd
import numpy as np

st.set_page_config(page_title="Predictive Maintenance – IBM ML App", layout="wide")

st.title("🔧 Predictive Maintenance – IBM ML Deployment")

st.sidebar.header("Configuration")
API_KEY = st.sidebar.text_input("IBM Cloud API Key:ErdbRSV4ipow4JGN_1An_FMv_pL7_C4aNsC2hIJvfPgE", type="password")

DEPLOYMENT_URL = (
    "https://private.jp-tok.ml.cloud.ibm.com/ml/v4/deployments/"
    "3b6164a3-4b3c-4c67-92dc-b50faad9285d/predictions?version=2021-05-01"
)

# -------------------------------------
# FIXED FIELD NAMES (no brackets!)
# -------------------------------------
fields = [
    "UDI",
    "Product ID",
    "Type",
    "Air temperature K",
    "Process temperature K",
    "Rotational speed rpm",
    "Torque Nm",
    "Tool wear min"
]

st.subheader("Enter Input Values")

default_df = pd.DataFrame({
    "UDI": [1],
    "Product ID": ["M14860"],
    "Type": ["M"],
    "Air temperature K": [298.1],
    "Process temperature K": [308.6],
    "Rotational speed rpm": [1551],
    "Torque Nm": [42.8],
    "Tool wear min": [0]
})

df = st.data_editor(default_df, num_rows="dynamic")

# -------------------------------------
# FIX JSON PAYLOAD
# -------------------------------------
def sanitize_dataframe(df):
    df = df.copy()

    # Convert numeric columns
    numeric_cols = [
        "UDI", "Air temperature K", "Process temperature K",
        "Rotational speed rpm", "Torque Nm", "Tool wear min"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Convert NaN → None for JSON safety
    df = df.replace({np.nan: None})

    return df

# -------------------------------------
# PREDICT BUTTON
# -------------------------------------
if st.button("Predict", use_container_width=True):

    if not API_KEY:
        st.error("❌ Enter API Key in the sidebar!")
        st.stop()

    # STEP 1 – Authenticate
    token_response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={"apikey": API_KEY, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"}
    )

    try:
        mltoken = token_response.json()["access_token"]
    except:
        st.error("❌ Authentication failed")
        st.write(token_response.text)
        st.stop()

    # STEP 2 – sanitize data
    safe_df = sanitize_dataframe(df)

    payload = {
        "input_data": [
            {
                "fields": fields,
                "values": safe_df.values.tolist()
            }
        ]
    }

    st.write("Generated JSON payload:", payload)

    # STEP 3 – Send prediction request
    response = requests.post(
        DEPLOYMENT_URL,
        json=payload,
        headers={"Authorization": f"Bearer {mltoken}"}
    )

    try:
        result = response.json()
        st.json(result)
    except:
        st.error("❌ Could not parse JSON response")
        st.write(response.text)
        st.stop()

    # Extract predictions
    try:
        preds = result["predictions"][0]["values"]
        pred_df = pd.DataFrame(preds, columns=["Prediction"])
        st.subheader("Prediction Table")
        st.dataframe(pred_df)
        st.subheader("Prediction Chart")
        st.line_chart(pred_df)
    except Exception as e:
        st.warning("⚠ Could not extract prediction values")
        st.write(e)

