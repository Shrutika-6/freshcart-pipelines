import pandas as pd
from sklearn.datasets import load_iris

if 'data_loader' not in globals():
    try:
        from mage_ai.data_preparation.decorators import data_loader
    except ImportError:
        def data_loader(fn):
            return fn
if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ImportError:
        def test(fn):
            return fn


@data_loader
def load_data(*args, **kwargs) -> pd.DataFrame:
    """
    Loads the Iris dataset into a pandas DataFrame.
    """
    iris = load_iris(as_frame=True)
    df = iris.frame
    return df


@test
def test_output(output, *args) -> None:
    """
    Quality gate: ensure DataFrame is not empty and contains expected 150 rows & 5 columns.
    """
    assert output is not None, 'The output is undefined'
    assert len(output) == 150, f'Expected 150 rows, got {len(output)}'
    assert len(output.columns) == 5, f'Expected 5 columns, got {len(output.columns)}'
