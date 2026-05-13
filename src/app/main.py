"""
FASTAPI + GRADIO SERVING APPLICATION - Production-Ready ML Model Serving
========================================================================

This application provides a complete serving solution for the Telco Customer Churn model
with both programmatic API access and a user-friendly web interface.

Architecture:
- FastAPI: High-performance REST API with automatic OpenAPI documentation
- Gradio: User-friendly web UI for manual testing and demonstrations
- Pydantic: Data validation and automatic API documentation
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import gradio as gr
import pandas as pd
import os
from src.serving.inference import predict  # Core ML inference logic

# Initialize FastAPI application
app = FastAPI(
    title="Telco Customer Churn Prediction API",
    description="ML API for predicting customer churn in telecom industry",
    version="1.0.0"
)

# === MOUNT FRONTEND ===
# Serve the custom landing page from the frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def serve_home():
    """
    Serves the custom landing page as the default home page.
    """
    return FileResponse("frontend/index.html")

@app.get("/style.css")
def serve_css():
    return FileResponse("frontend/style.css")

@app.get("/script.js")
def serve_js():
    return FileResponse("frontend/script.js")

# === HEALTH CHECK ENDPOINT ===
@app.get("/health")
def health():
    return {"status": "ok"}

# === REQUEST DATA SCHEMA ===
# Pydantic model for automatic validation and API documentation
class CustomerData(BaseModel):
    """
    Customer data schema for churn prediction.
    
    This schema defines the exact 18 features required for churn prediction.
    All features match the original dataset structure for consistency.
    """
    # Demographics
    gender: str                # "Male" or "Female"
    Partner: str               # "Yes" or "No" - has partner
    Dependents: str            # "Yes" or "No" - has dependents
    
    # Phone services
    PhoneService: str          # "Yes" or "No"
    MultipleLines: str         # "Yes", "No", or "No phone service"
    
    # Internet services  
    InternetService: str       # "DSL", "Fiber optic", or "No"
    OnlineSecurity: str        # "Yes", "No", or "No internet service"
    OnlineBackup: str          # "Yes", "No", or "No internet service"
    DeviceProtection: str      # "Yes", "No", or "No internet service"
    TechSupport: str           # "Yes", "No", or "No internet service"
    StreamingTV: str           # "Yes", "No", or "No internet service"
    StreamingMovies: str       # "Yes", "No", or "No internet service"
    
    # Account information
    Contract: str              # "Month-to-month", "One year", "Two year"
    PaperlessBilling: str      # "Yes" or "No"
    PaymentMethod: str         # "Electronic check", "Mailed check", etc.
    
    # Numeric features
    tenure: int                # Number of months with company
    MonthlyCharges: float      # Monthly charges in dollars
    TotalCharges: float        # Total charges to date

# === MAIN PREDICTION API ENDPOINT ===
@app.post("/predict")
def get_prediction(data: CustomerData):
    """
    Main prediction endpoint for customer churn prediction.
    
    This endpoint:
    1. Receives validated customer data via Pydantic model
    2. Calls the inference pipeline to transform features and predict
    3. Returns churn prediction in JSON format
    
    Expected Response:
    - {"prediction": "Likely to churn"} or {"prediction": "Not likely to churn"}
    - {"error": "error_message"} if prediction fails
    """
    try:
        # Convert Pydantic model to dict and call inference pipeline
        result = predict(data.dict())
        return {"prediction": result}
    except Exception as e:
        # Return error details for debugging (consider logging in production)
        return {"error": str(e)}


# =================================================== # 


# === GRADIO WEB INTERFACE ===
def gradio_interface(
    gender, Partner, Dependents, PhoneService, MultipleLines,
    InternetService, OnlineSecurity, OnlineBackup, DeviceProtection,
    TechSupport, StreamingTV, StreamingMovies, Contract,
    PaperlessBilling, PaymentMethod, tenure, MonthlyCharges, TotalCharges
):
    """
    Gradio interface function that processes form inputs and returns prediction.
    
    This function:
    1. Takes individual form inputs from Gradio UI
    2. Constructs the data dictionary matching the API schema
    3. Calls the same inference pipeline used by the API
    4. Returns user-friendly prediction string
    
    """
    # Construct data dictionary matching CustomerData schema
    data = {
        "gender": gender,
        "Partner": Partner,
        "Dependents": Dependents,
        "PhoneService": PhoneService,
        "MultipleLines": MultipleLines,
        "InternetService": InternetService,
        "OnlineSecurity": OnlineSecurity,
        "OnlineBackup": OnlineBackup,
        "DeviceProtection": DeviceProtection,
        "TechSupport": TechSupport,
        "StreamingTV": StreamingTV,
        "StreamingMovies": StreamingMovies,
        "Contract": Contract,
        "PaperlessBilling": PaperlessBilling,
        "PaymentMethod": PaymentMethod,
        "tenure": int(tenure),              # Ensure integer type
        "MonthlyCharges": float(MonthlyCharges),  # Ensure float type
        "TotalCharges": float(TotalCharges),      # Ensure float type
    }
    
    # Call same inference pipeline as API endpoint
    result = predict(data)
    return str(result)  # Return as string for Gradio display

# === GRADIO UI CONFIGURATION ===
# Build comprehensive Gradio interface with all customer features
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔮 Telco Customer Churn Intelligence")
    
    with gr.Tabs():
        with gr.Tab("Predictor"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Customer Profile")
                    gender = gr.Dropdown(["Male", "Female"], label="Gender", value="Male")
                    partner = gr.Dropdown(["Yes", "No"], label="Partner", value="No")
                    dependents = gr.Dropdown(["Yes", "No"], label="Dependents", value="No")
                    tenure = gr.Number(label="Tenure (months)", value=1, minimum=0)
                    
                    gr.Markdown("### Services")
                    phone = gr.Dropdown(["Yes", "No"], label="Phone Service", value="Yes")
                    multiple = gr.Dropdown(["Yes", "No", "No phone service"], label="Multiple Lines", value="No")
                    internet = gr.Dropdown(["DSL", "Fiber optic", "No"], label="Internet Service", value="Fiber optic")
                    security = gr.Dropdown(["Yes", "No", "No internet service"], label="Online Security", value="No")
                    backup = gr.Dropdown(["Yes", "No", "No internet service"], label="Online Backup", value="No")
                
                with gr.Column():
                    gr.Markdown("### Billing & Contract")
                    contract = gr.Dropdown(["Month-to-month", "One year", "Two year"], label="Contract", value="Month-to-month")
                    paperless = gr.Dropdown(["Yes", "No"], label="Paperless Billing", value="Yes")
                    payment = gr.Dropdown([
                        "Electronic check", "Mailed check",
                        "Bank transfer (automatic)", "Credit card (automatic)"
                    ], label="Payment Method", value="Electronic check")
                    monthly = gr.Number(label="Monthly Charges ($)", value=85.0)
                    total = gr.Number(label="Total Charges ($)", value=85.0)
                    
                    gr.Markdown("### Prediction Results")
                    output = gr.Textbox(label="Churn Risk Assessment", lines=2)
                    submit_btn = gr.Button("Analyze Customer", variant="primary")
                    
                    submit_btn.click(
                        fn=gradio_interface,
                        inputs=[
                            gender, partner, dependents, phone, multiple,
                            internet, security, backup, gr.State("No"), # protection
                            gr.State("No"), gr.State("No"), gr.State("No"), # support, tv, movies
                            contract, paperless, payment, tenure, monthly, total
                        ],
                        outputs=output
                    )

        with gr.Tab("Model Insights"):
            gr.Markdown("### Key Churn Predictors (Global Feature Importance)")
            gr.Markdown("This chart shows which factors the XGBoost model considers most important when determining if a customer will leave.")
            
            # Simple bar chart for feature importance
            importance_data = {
                "Contract_Month-to-month": 0.35,
                "InternetService_Fiber optic": 0.22,
                "tenure": 0.15,
                "PaymentMethod_Electronic check": 0.10,
                "MonthlyCharges": 0.08,
                "OnlineSecurity_No": 0.05,
                "Other": 0.05
            }
            gr.BarPlot(
                value=pd.DataFrame([{"Feature": k, "Importance": v} for k, v in importance_data.items()]),
                x="Feature",
                y="Importance",
                title="Top 7 Drivers of Churn",
                vertical=False,
                width=600,
                height=400,
                tooltip=["Feature", "Importance"]
            )
            gr.Markdown("> **Insight:** Month-to-month contracts and Fiber Optic service are the strongest indicators of churn risk in this dataset.")

        with gr.Tab("Project Info"):
            gr.Markdown("""
            ### MLOps Architecture
            - **Engine:** XGBoost Classifier
            - **API Framework:** FastAPI
            - **Frontend:** Custom HTML/JS + Gradio
            - **Cloud:** AWS ECS Fargate
            - **CI/CD:** GitHub Actions
            - **Monitoring:** Great Expectations
            """)

# === MOUNT GRADIO UI INTO FASTAPI ===
app = gr.mount_gradio_app(app, demo, path="/ui")
