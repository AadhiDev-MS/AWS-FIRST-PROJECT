import great_expectations as ge
import pandas as pd
from typing import Tuple, List

def validate_telco_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validates the incoming customer data using Great Expectations.
    Ensures data quality before inference to prevent model degradation.
    """
    # Convert to GE DataFrame
    ge_df = ge.from_pandas(df)
    
    results = []
    
    # 1. Check for critical column presence
    required_cols = ['tenure', 'MonthlyCharges', 'Contract', 'InternetService']
    for col in required_cols:
        res = ge_df.expect_column_to_exist(col)
        if not res.success:
            results.append(f"Missing column: {col}")

    # 2. Validate numeric ranges
    res_tenure = ge_df.expect_column_values_to_be_between('tenure', min_value=0, max_value=120)
    if not res_tenure.success:
        results.append("Tenure out of valid range (0-120)")

    res_charges = ge_df.expect_column_values_to_be_between('MonthlyCharges', min_value=0, max_value=500)
    if not res_charges.success:
        results.append("MonthlyCharges out of valid range (0-500)")

    # 3. Validate categorical values
    res_contract = ge_df.expect_column_values_to_be_in_set(
        'Contract', ['Month-to-month', 'One year', 'Two year']
    )
    if not res_contract.success:
        results.append("Invalid Contract type")

    is_valid = len(results) == 0
    
    if is_valid:
        print("✅ Data validation PASSED: All Great Expectations criteria met.")
    else:
        print(f"❌ Data validation FAILED: {', '.join(results)}")
        
    return is_valid, results

if __name__ == "__main__":
    # Test case
    test_data = pd.DataFrame([{
        "tenure": 10,
        "MonthlyCharges": 70.0,
        "Contract": "One year",
        "InternetService": "Fiber optic"
    }])
    validate_telco_data(test_data)
