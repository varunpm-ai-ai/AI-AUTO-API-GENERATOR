"""
Unit Tests for Data Cleaning Strategies (Strategy Pattern).
"""
import pandas as pd
import numpy as np
from app.strategies.deduplication import DeduplicationStrategy
from app.strategies.imputation import NullImputationStrategy
from app.strategies.sanitization import WhitespaceSanitizationStrategy
from app.strategies.outlier import OutlierStrategy
from app.schemas.job import ImputationMethod


def test_deduplication_strategy():
    strategy = DeduplicationStrategy()
    df = pd.DataFrame({
        "id": [1, 2, 2, 3],
        "name": ["A", "B", "B", "C"]
    })
    cleaned = strategy.apply(df, {})
    assert len(cleaned) == 3
    assert list(cleaned["id"]) == [1, 2, 3]


def test_whitespace_sanitization_strategy():
    strategy = WhitespaceSanitizationStrategy()
    df = pd.DataFrame({
        " First Name ": [" Alice \t", " Bob\n"],
        "AGE-GROUP": [" young ", " senior "]
    })
    cleaned = strategy.apply(df, {"normalize_column_names": True, "sanitize_strings": True})
    
    # Assert column headers became snake_case
    assert "first_name" in cleaned.columns
    assert "age_group" in cleaned.columns
    
    # Assert values were trimmed
    assert cleaned["first_name"].iloc[0] == "Alice"
    assert cleaned["first_name"].iloc[1] == "Bob"


def test_null_imputation_mean_and_drop():
    strategy = NullImputationStrategy()
    df = pd.DataFrame({
        "num": [10.0, 20.0, np.nan, 30.0],
        "txt": ["a", "b", np.nan, "d"]
    })
    
    # Test MEAN imputation
    cleaned_mean = strategy.apply(df.copy(), {"null_imputation": ImputationMethod.MEAN})
    assert cleaned_mean["num"].isnull().sum() == 0
    assert cleaned_mean["num"].iloc[2] == 20.0  # Mean of 10, 20, 30 is 20
    assert cleaned_mean["txt"].iloc[2] == ""  # String null replaced with empty string


def test_outlier_handling_strategy():
    strategy = OutlierStrategy()
    # 1000 is an extreme outlier
    df = pd.DataFrame({
        "values": [10.0, 12.0, 11.0, 13.0, 12.0, 11.0, 1000.0]
    })
    cleaned = strategy.apply(df, {"handle_outliers": True, "outlier_threshold_iqr": 1.5})
    assert cleaned["values"].max() < 1000.0
