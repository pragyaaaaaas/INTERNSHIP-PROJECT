
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Predictive Maintenance - ML App", layout="wide")

st.markdown("""
<h1 style="text-align:center; color:#4B8BBE;">Predictive Maintenance – IBM ML Deployment</h1>
<p style="text-align:center; font-size:18px;">
Enter machine sensor data → Get machine failure prediction → Visualize results
</p>
""", unsafe_allow_html=True)

# ----------------------------
# SIDEBAR SETTINGS
# ----------------------------
st.sidebar.header("Configuration")

API_KEY = st.sidebar.text_input("IBM Cloud API Key:ErdbRSV4ipow4JGN_1An_FMv_pL7_C4aNsC2hIJvfPgE", type="password")

DEPLOYMENT_URL = (
    "https://jp-tok.ml.cloud.ibm.com/ml/v4/deployments/3b6164a3-4b3c-4c99-9c25-cbed57fab291/predictions?version=2021-05-01"
)

# ----------------------------
# INPUT FIELDS
# ----------------------------

fields = [
    "UDI",
    "Product ID",
    "Type",
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]"
]

st.subheader("Enter Input Values")

# Create editable table
default_df = pd.DataFrame({
    "UDI": [1],
    "Product ID": ["M14860"],
    "Type": ["M"],
    "Air temperature [K]": [298.1],
    "Process temperature [K]": [308.6],
    "Rotational speed [rpm]": [1551],
    "Torque [Nm]": [42.8],
    "Tool wear [min]": [0]
})

df = st.data_editor(default_df, num_rows="dynamic")

# ----------------------------
# PREDICT BUTTON
# ----------------------------
if st.button("Predict", use_container_width=True):

    if not API_KEY:
        st.error("❌ Please enter your IBM API Key in the sidebar")
        st.stop()

    # STEP 1: Authentication
    token_response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={"apikey": API_KEY, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"}
    )

    try:
        mltoken = token_response.json()["access_token"]
    except:
        st.error("❌ Authentication failed. Check your API key.")
        st.stop()

    st.success("🔐 Authentication successful!")

    # STEP 2: Prepare Watson Payload
    payload = {
        "input_data": [
            {
                "fields": fields,
                "values": df.values.tolist()
            }
        ]
    }

    # STEP 3: Predict
    response = requests.post(
        DEPLOYMENT_URL,
        json=payload,
        headers={"Authorization": f"Bearer {mltoken}"}
    )

    # TRY reading JSON
    try:
        result = response.json()
        st.subheader("🔎 Prediction Response (Raw JSON)")
        st.json(result)
    except:
        st.error("❌ Failed to parse response")
        st.write(response.text)
        st.stop()

    # Extract prediction column
    try:
        prediction_values = result["predictions"][0]["values"]
        pred_df = pd.DataFrame(prediction_values, columns=["Predicted Target"])

        st.subheader("📊 Prediction Table")
        st.dataframe(pred_df)

        st.subheader("📈 Prediction Chart")
        st.line_chart(pred_df)

    except Exception as e:
        st.warning("⚠ Could not extract prediction values from API")
        st.write(e)
