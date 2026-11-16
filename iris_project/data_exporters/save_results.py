import os
import pandas as pd

if 'data_exporter' not in globals():
    try:
        from mage_ai.data_preparation.decorators import data_exporter
    except ImportError:
        def data_exporter(fn):
            return fn
if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ImportError:
        def test(fn):
            return fn


@data_exporter
def export_data(data: dict, *args, **kwargs):
    """
    Saves predictions to iris_predictions.csv.
    Only executes if all upstream blocks and @tests passed!
    """
    test_results = data['test_results']
    file_path = 'iris_predictions.csv'
    test_results.to_csv(file_path, index=False)
    print(f"[save_results] Successfully saved predictions to {file_path}")
    return file_path


@test
def test_file_exists(output, *args) -> None:
    """
    Ensure the predictions file was successfully created on disk.
    """
    assert os.path.exists(output), f"File {output} does not exist!"
    assert os.path.getsize(output) > 0, f"File {output} is empty!"
