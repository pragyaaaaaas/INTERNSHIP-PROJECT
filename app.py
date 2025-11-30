import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="IBM ML Prediction App", layout="wide")

# ----------------------------
# UI HEADER
# ----------------------------
st.markdown("""
    <h1 style="text-align:center; color:#4B8BBE;">IBM Cloud Machine Learning Predictor</h1>
    <p style="text-align:center; font-size:18px;">
        Enter API Key • Provide Input Values • Generate Predictions • Visualize Results
    </p>
""", unsafe_allow_html=True)

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.header("Configuration")
API_KEY = st.sidebar.text_input("IBM Cloud API Key:ErdbRSV4ipow4JGN_1An_FMv_pL7_C4aNsC2hIJvfPgE", type="password")

fields = st.sidebar.text_area("Input Fields (comma separated):", "field1, field2")

num_inputs = st.sidebar.number_input("How many input rows?", min_value=1, max_value=10, value=1)
st.sidebar.markdown("---")
st.sidebar.markdown("Built with ❤️ using Streamlit")

# Convert fields to list
field_list = [f.strip() for f in fields.split(",") if f.strip()]

# ----------------------------
# MAIN INPUT TABLE
# ----------------------------
st.subheader("Enter Input Values")

# Create dataframe for input
input_df = pd.DataFrame(
    [[0]*len(field_list)] * num_inputs,
    columns=field_list
)

edited_df = st.data_editor(input_df, num_rows="dynamic")

# ----------------------------
# API CALL
# ----------------------------
if st.button("Get Prediction", use_container_width=True):

    if not API_KEY:
        st.error("❌ Please enter your IBM Cloud API Key in the sidebar.")
        st.stop()

    try:
        # STEP 1: Get IAM Token
        token_response = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            data={"apikey": API_KEY, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"}
        )
        mltoken = token_response.json().get("access_token")

        if not mltoken:
            st.error("❌ Authentication failed! Check your API key.")
            st.stop()

        st.success("🔐 Authenticated Successfully!")

        # STEP 2: Prepare Payload
        payload_scoring = {
            "input_data": [
                {
                    "fields": field_list,
                    "values": edited_df.values.tolist()
                }
            ]
        }

        # STEP 3: Call ML Deployment
        response = requests.post(
            "https://private.jp-tok.ml.cloud.ibm.com/ml/v4/deployments/3b6164a3-4b3c-4c99-9c25-cbed57fab291/predictions?version=2021-05-01",
            json=payload_scoring,
            headers={"Authorization": "Bearer " + mltoken}
        )

        try:
            result = response.json()
        except ValueError:
            st.error("❌ Invalid response from server.")
            st.write(response.text)
            st.stop()

        st.subheader("📌 Prediction Response")
        st.json(result)

        # ----------------------------
        # GRAPH VISUALIZATION
        # ----------------------------
        st.subheader("📊 Visualization")

        # Attempt to extract predictions from JSON
        try:
            preds = result["predictions"][0]["values"]
            pred_df = pd.DataFrame(preds, columns=["Prediction"])
            
            st.write("### Prediction Table")
            st.dataframe(pred_df)

            # Plot chart
            st.write("### Prediction Chart")
            st.line_chart(pred_df)

        except Exception:
            st.warning("⚠ Unable to visualize predictions (unexpected format).")

    except Exception as e:
        st.error(f"❌ Error: {e}")
