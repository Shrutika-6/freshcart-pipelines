import pandas as pd
from sklearn.model_selection import train_test_split

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
def transform(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    """
    Prepares iris dataset by adding train/test split column.
    Accepts runtime variable 'test_size' (default 0.2).
    """
    test_size = kwargs.get('test_size', 0.2)
    # Ensure float conversion if passed as string or float
    test_size = float(test_size)

    # Deterministic split with random_state=42
    train_idx, test_idx = train_test_split(
        df.index,
        test_size=test_size,
        random_state=42,
        stratify=df['target'] if 'target' in df.columns else None
    )

    out = df.copy()
    out['split'] = 'train'
    out.loc[test_idx, 'split'] = 'test'
    return out


@test
def test_output(output, *args) -> None:
    """
    Test output is not None and has split column
    """
    assert output is not None, 'The output is undefined'
    assert 'split' in output.columns, "Output dataframe must contain 'split' column"
