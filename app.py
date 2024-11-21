from shiny import App, ui, render, reactive
import pandas as pd
import joblib

# Load the saved model
model = joblib.load("xgb_pipeline_model.pkl")

# Extract all required features from the model
preprocessor = model.named_steps['preprocessor']
numerical_features = preprocessor.transformers_[0][2]
categorical_features = preprocessor.transformers_[1][2]
all_features = numerical_features + list(preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features))

# Selected user-friendly features for the UI
USER_FRIENDLY_FEATURES = [
    "taxAssessedValue",  # Tax-assessed value of the property
    "restimateHighPercent",  # Estimate of the highest price
    "bathrooms",  # Number of bathrooms
    "adTargets/bd",  # Number of bedrooms
    "resoFacts/highSchoolDistrict",  # High school district
    "resoFacts/fireplaceFeatures/0"  # Fireplace feature
]

# User Interface
app_ui = ui.page_fluid(
    ui.h2("Real Estate Price Prediction Tool", style="background-color: #6180c2; color: white; padding: 10px; border-radius: 5px;"),
    ui.row(
        # Input fields for address and user-friendly features
        ui.column(
            6,
            ui.div(
                ui.h3("Input Details", style="background-color: #6180c2; color: white; padding: 10px; border-radius: 5px 5px 0 0; margin: 0;"),
                ui.input_text("address", "Enter Address", ""),
                ui.input_text("city", "Enter City", ""),
                ui.input_text("state", "Enter State", ""),
                ui.input_text("zip_code", "Enter Zipcode", ""),
                ui.input_text_area("bathrooms", "Number of Bathrooms", ""),
                ui.input_text_area("bedrooms", "Number of Bedrooms", ""),
                ui.input_text_area("tax_value", "Tax-Assessed Value (in dollars)", ""),
                ui.input_text_area("price_high", "Estimated High Price (in percentage)", ""),
                ui.input_text("school_district", "High School District", ""),
                ui.input_select("fireplace", "Has Fireplace?", {"Yes": "Yes", "No": "No"}),
                ui.input_action_button("predict_btn", "Predict Price"),
                style="background-color: white; border: 2px solid #6180c2; padding: 15px; border-radius: 0 0 5px 5px;"
            ),
        ),
        # Output for the predicted price
        ui.column(
            6,
            ui.div(
                ui.h3("Prediction Output", style="background-color: #6180c2; color: white; padding: 10px; border-radius: 5px 5px 0 0; margin: 0;"),
                ui.h4("Predicted Price:"),
                ui.output_text_verbatim("score_output"),
                style="background-color: white; border: 2px solid #6180c2; padding: 15px; border-radius: 0 0 5px 5px;"
            ),
        ),
    ),
)

# Server function
def server(input, output, session):
    @output
    @render.text
    def score_output():
        # Initialize all features with default values
        input_features = {feature: 0 for feature in all_features}  # Default values

        # Update input features based on user inputs
        user_inputs = {
            "taxAssessedValue": float(input.tax_value()) if input.tax_value().strip() else 0,
            "restimateHighPercent": float(input.price_high()) if input.price_high().strip() else 0,
            "bathrooms": float(input.bathrooms()) if input.bathrooms().strip() else 0,
            "adTargets/bd": float(input.bedrooms()) if input.bedrooms().strip() else 0,
            "resoFacts/highSchoolDistrict": 1 if input.school_district().lower() == "salinas union high" else 0,
            "resoFacts/fireplaceFeatures/0": 0 if input.fireplace() == "No" else 1,
        }

        # Add user inputs to the input features
        input_features.update(user_inputs)

        # Convert to DataFrame for prediction
        input_df = pd.DataFrame([input_features])

        # Ensure all required columns exist
        for feature in all_features:
            if feature not in input_df.columns:
                input_df[feature] = 0  # Default value for missing features

        try:
            # Predict price using the model
            prediction = model.predict(input_df)[0]
            return f"Predicted Price: ${prediction:,.2f}"
        except Exception as e:
            return f"Error predicting price: {e}"

# Create the Shiny app
app = App(app_ui, server)