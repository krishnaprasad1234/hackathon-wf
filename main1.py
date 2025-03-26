import google.generativeai as genai
import pandas as pd
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure Gemini API
genai.configure(api_key="AIzaSyCrvP1pCVWzHJyHu0AQpibXmh43kRIfmt4")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
def generate_rules(columns):
    columns = [
    {"Field Name": "Identifier Type", "Description": "Report the identifier type for an investment security..."},
    {"Field Name": "Identifier Value", "Description": "Report the identifier value for an investment security..."},
    {"Field Name": "Amortized Cost (USD Equivalent)", "Description": "Report the amortized cost (USD equivalent)..."},
    {"Field Name": "Market Value (USD Equivalent)", "Description": "Report the market value (USD equivalent)..."},
    {"Field Name": "Accounting Intent", "Description": "Indicate whether the security being hedged is AFS, HTM, or EQ..."},
    {"Field Name": "Type of Hedge(s)", "Description": "Report the type of hedge: Fair Value or Cash Flow Hedge..."},
    {"Field Name": "Hedged Risk", "Description": "Indicate the risk being hedged among various risk categories..."},
    {"Field Name": "Hedge Interest Rate", "Description": "For hedges of interest rate risk, indicate the benchmark rates..."},
    {"Field Name": "Hedge Percentage", "Description": "Indicate the portion of the asset being hedged in decimal format..."},
    {"Field Name": "Hedge Horizon", "Description": "Report the latest date of the remaining effectiveness horizon..."},
    {"Field Name": "Hedged Cash Flow", "Description": "Indicate the type of cash flow associated with the hedge..."},
    {"Field Name": "Sidedness", "Description": "Indicate whether the hedging instrument provides a one-sided offset..."},
    {"Field Name": "Hedging Instrument at Fair Value", "Description": "Indicate the USD-equivalent fair value of the hedging instrument..."},
    {"Field Name": "Effective Portion of Cumulative Gains and Losses", "Description": "Indicate the effective portion of the gains and losses..."},
    {"Field Name": "ASU 2017-12 Hedge Designations", "Description": "Indicate if ASU 2017-12 hedge designations are applicable..."}
    ]
    
    prompt = f"""
    Generate validation rules for the following dataset columns based on their descriptions:
    {json.dumps(columns, indent=2)}
    Provide the rules in JSON format, where each rule includes:
    - Column Name
    - Rule Description
    - Condition (in Python expression format)
    Rules should be in this structure:
    [
      {{
        "Column Name": "column_name_here",
        "Rule Description": "rule_description_here",
        "Condition": "Python_condition_here"
      }},
      ...
    ]

    Return ONLY the JSON, with NO extra text.
    """

    print(columns)
    
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    
    if response and response.candidates:
        rules_text = response.candidates[0].content.parts[0].text
        try:
            rules = json.loads(rules_text)
            return rules
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail="Error parsing JSON response: " + str(e))
    else:
        raise HTTPException(status_code=500, detail="Empty or invalid response from Gemini")

def apply_rules(df, rules):
    results = []  # Store validation status for each row

    print("In apply_rules")

    rules_list = rules.get("rules")
    if not rules_list:
        raise HTTPException(status_code=400, detail="No rules found in the input.")

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        row_status = {"Row": index, "Valid": True, "Violations": []}  # Default as valid

        for rule in rules_list:
            column = rule.get("Column Name")
            condition = rule.get("Condition")

            if column in df.columns:
                try:
                    # Evaluate rule condition for the specific row
                    is_valid = df.loc[[index]].eval(condition).values[0]

                    if not is_valid:  # If condition fails
                        row_status["Valid"] = False
                        row_status["Violations"].append({
                            "Column": column,
                            "Value": row[column],
                            "Violation": rule.get("Rule Description", "No description provided")
                        })

                except Exception as e:
                    print(f"Error applying rule on column {column}: {e}")
                    raise HTTPException(status_code=500, detail=f"Error applying rule on column {column}: {e}")

        results.append(row_status)  # Append row result

    return results

@app.post("/generate-rules")
async def generate_rules_endpoint(data: dict):
    try:
        print("Received data:", data)  # Debugging: Check incoming JSON
        rules = generate_rules(data['json_input'])
        print("Generated rules:", rules)  # Debugging: Check output before sending response
        return {"rules": rules}
    except Exception as e:
        print("Error in backend:", str(e))  # Debugging
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate-dataset")
async def validate_dataset(file: UploadFile = File(...), rules: UploadFile = File(...)):
    print("call made")
    try:
        print(file)
        df = pd.read_csv(file.file)
        print("hello")
        # print(df)
        rules_content = await rules.read()
        print("next")
        rules_data = json.loads(rules_content)
        print(rules_data)
        data_2d = df.values.tolist()
        print(data_2d)
        columns = [
        {"Field Name": "identifier_type", "Description": "Report the identifier type for an investment security..."},
        {"Field Name": "identifier_value", "Description": "Report the identifier value for an investment security..."},
        {"Field Name": "amortized_cost", "Description": "Report the amortized cost (USD equivalent)..."},
        {"Field Name": "market_value (USD Equivalent)", "Description": "Report the market value (USD equivalent)..."},
        {"Field Name": "accounting_intent", "Description": "Indicate whether the security being hedged is AFS, HTM, or EQ..."},
        {"Field Name": "type_of_hedge", "Description": "Report the type of hedge: Fair Value or Cash Flow Hedge..."},
        {"Field Name": "hedged_risk", "Description": "Indicate the risk being hedged among various risk categories..."},
        {"Field Name": "hedge_interest_rate", "Description": "For hedges of interest rate risk, indicate the benchmark rates..."},
        {"Field Name": "hedge_percentage", "Description": "Indicate the portion of the asset being hedged in decimal format..."},
        {"Field Name": "hedge_horizon", "Description": "Report the latest date of the remaining effectiveness horizon..."},
        {"Field Name": "hedged_cash_flow", "Description": "Indicate the type of cash flow associated with the hedge..."},
        {"Field Name": "sidedness", "Description": "Indicate whether the hedging instrument provides a one-sided offset..."},
        {"Field Name": "hedging_instrument_fair_value", "Description": "Indicate the USD-equivalent fair value of the hedging instrument..."},
        {"Field Name": "effective_portion_gains_losses", "Description": "Indicate the effective portion of the gains and losses..."},
        {"Field Name": "asu_2017_12_hedge_designations", "Description": "Indicate if ASU 2017-12 hedge designations are applicable..."}
        ]
        df = pd.DataFrame(data_2d, columns=[col["Field Name"] for col in columns])
        violations = apply_rules(df, rules_data)
        print(violations)
        return {"violations": violations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
