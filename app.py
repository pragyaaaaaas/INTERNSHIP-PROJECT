import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# IBM CLOUD CREDENTIALS
# -----------------------------
API_KEY = "ErdbRSV4ipow4JGN_1An_FMv_pL7_C4aNsC2hIJvfPgE"
DEPLOYMENT_URL = "https://jp-tok.ml.cloud.ibm.com/ml/v4/deployments/3b6164a3-4b3c-4c99-9c25-cbed57fab291/predictions?version=2021-05-01"

# -----------------------------
# Helper Functions
# -----------------------------
def get_token(api_key):
    """Get IBM Cloud IAM token"""
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"apikey": api_key, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"}

    resp = requests.post(iam_url, headers=headers, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]

def encode_type(m_type):
    """Encode Type to numeric value matching training"""
    type_map = {"M": 0, "L": 1, "H": 2}  # Update if model used different encoding
    return type_map.get(m_type, 0)

def predict(input_values):
    """Send prediction request to IBM Watson ML"""
    token = get_token(API_KEY)
    payload = {
        "input_data": [
            {
                "fields": [
                    "UDI",
                    "Product ID",
                    "Type",
                    "Air temperature [K]",
                    "Process temperature [K]",
                    "Rotational speed [rpm]",
                    "Torque [Nm]",
                    "Tool wear [min]"
                ],
                "values": [input_values]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(DEPLOYMENT_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Predictive Maintenance", layout="wide")
st.title("🔧 Predictive Maintenance System")
st.write("Enter machine parameters to predict failure.")

with st.form("input_form"):
    UDI = st.number_input("UDI", min_value=1, value=1)
    
    # Use exact numeric Product IDs from your dataset
    product_id = st.number_input("Product ID", min_value=14860, max_value=15000, value=14860)
    
    m_type = st.selectbox("Type", ["M", "L", "H"])
    air_temp = st.number_input("Air Temperature [K]", value=298.1)
    process_temp = st.number_input("Process Temperature [K]", value=308.6)
    rpm = st.number_input("Rotational Speed [rpm]", value=1551)
    torque = st.number_input("Torque [Nm]", value=42.8)
    tool_wear = st.number_input("Tool Wear [min]", value=0)

    submitted = st.form_submit_button("Predict Failure")

if submitted:
    type_encoded = encode_type(m_type)

    # Prepare input array with **exact numeric values**
    input_values = [
        UDI,
        product_id,
        type_encoded,
        air_temp,
        process_temp,
        rpm,
        torque,
        tool_wear
    ]

    with st.spinner("Predicting..."):
        try:
            result = predict(input_values)
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            st.stop()
        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error: {e}")
            st.stop()

    st.success("Prediction Received!")
    st.write("### 🔍 Raw Response")
    st.json(result)

    # Extract prediction
    try:
        prediction = result["predictions"][0]["values"][0][0]
        st.write(f"### ⚠️ Failure Prediction: **{prediction}**")
    except (KeyError, IndexError):
        st.error("Error reading response from model.")

    # -----------------------------
    # Graph: Input Parameter Visualization
    # -----------------------------
    st.write("### 📊 Input Parameter Plot")
    df = pd.DataFrame({
        "Parameter": ["Air Temp", "Process Temp", "RPM", "Torque", "Tool Wear"],
        "Value": [air_temp, process_temp, rpm, torque, tool_wear]
    })
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df["Parameter"], df["Value"], color='skyblue')
    ax.set_title("Machine Input Parameters")
    ax.set_xlabel("Parameter")
    ax.set_ylabel("Value")
    st.pyplot(fig)



 

 
