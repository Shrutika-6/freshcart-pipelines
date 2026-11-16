import pandas as pd

if 'transformer' not in globals():
    try:
        from mage_ai.data_preparation.decorators import transformer
    except ImportError:
        def transformer(fn):
            return fn
if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ImportError:
        def test(fn):
            return fn


@transformer
def validate_data(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    """
    Custom block (Part C4):
    Validates that there are no missing/null values and that exactly 3 distinct classes exist.
    """
    null_count = df.isnull().sum().sum()
    unique_classes = df['target'].nunique() if 'target' in df.columns else 0

    print(f"[validate_iris] Total null values: {null_count}, Unique target classes: {unique_classes}")
    return df


@test
def test_no_missing_values(output, *args) -> None:
    assert output.isnull().sum().sum() == 0, "Data contains missing/null values!"


@test
def test_three_classes(output, *args) -> None:
    assert 'target' in output.columns, "Target column missing"
    assert output['target'].nunique() == 3, f"Expected exactly 3 target classes, found {output['target'].nunique()}"
