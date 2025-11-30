import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# IBM CLOUD CREDENTIALS
# -----------------------------
API_KEY = "ErdbRSV4ipow4JGN_1An_FMv_pL7_C4aNsC2hIJvfPgE"
DEPLOYMENT_URL = "https://jp-tok.ml.cloud.ibm.com/ml/v4/deployments/3b6164a3-4b3c-4c99-9c25-cbed57fab291/predictions?version=2021-05-01"

# Get IAM token
def get_token(api_key):
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"apikey": api_key, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"}

    resp = requests.post(iam_url, headers=headers, data=data)
    return resp.json()["access_token"]

# Predict function
def predict(values):
    token = get_token(API_KEY)

    payload = {
        "input_data": [
            {
                "fields": [
                    "UDI",
                    "Product ID",
                    "Type",
                    "Air temperature K",
                    "Process temperature K",
                    "Rotational speed rpm",
                    "Torque Nm",
                    "Tool wear min"
                ],
                "values": [values]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(DEPLOYMENT_URL, json=payload, headers=headers, timeout=30)

    return response.json()

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🔧 Predictive Maintenance System")
st.write("Enter machine parameters to predict failure.")

UDI = st.number_input("UDI", min_value=1, value=1)
product_id = st.text_input("Product ID", "M14860")
m_type = st.selectbox("Type", ["M", "L", "H"])
air_temp = st.number_input("Air Temperature (K)", value=298.1)
process_temp = st.number_input("Process Temperature (K)", value=308.6)
rpm = st.number_input("Rotational Speed (rpm)", value=1551)
torque = st.number_input("Torque (Nm)", value=42.8)
tool_wear = st.number_input("Tool Wear (min)", value=0)

if st.button("Predict Failure"):
    input_values = [
        UDI,
        product_id,
        m_type,
        air_temp,
        process_temp,
        rpm,
        torque,
        tool_wear
    ]

    with st.spinner("Predicting..."):
        result = predict(input_values)

    st.success("Prediction Received!")

    st.write("### 🔍 Raw Response")
    st.json(result)

    # Extract prediction
    try:
        prediction = result["predictions"][0]["values"][0][0]
        st.write(f"### ⚠️ Failure Prediction: **{prediction}**")
    except:
        st.error("Error reading response from model.")

    # -----------------------------
    # Graph: Input Parameter Visualization
    # -----------------------------
    st.write("### 📊 Input Parameter Plot")

    df = pd.DataFrame({
        "Parameter": [
            "Air Temp", "Process Temp", "RPM", "Torque", "Tool Wear"
        ],
        "Value": [air_temp, process_temp, rpm, torque, tool_wear]
    })

    fig = plt.figure(figsize=(8, 4))
    plt.bar(df["Parameter"], df["Value"])
    plt.title("Machine Input Parameters")
    plt.xlabel("Parameter")
    plt.ylabel("Value")

    st.pyplot(fig)

 

 
