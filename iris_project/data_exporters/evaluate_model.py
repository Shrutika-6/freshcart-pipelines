import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

if 'data_exporter' not in globals() and 'transformer' not in globals():
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
def evaluate(data: dict, *args, **kwargs) -> dict:
    """
    Evaluates trained model: computes confusion matrix and classification report metrics table.
    """
    test_results = data['test_results']
    y_true = test_results['target']
    y_pred = test_results['prediction']

    cm = confusion_matrix(y_true, y_pred)
    report_dict = classification_report(y_true, y_pred, output_dict=True)
    report_df = pd.DataFrame(report_dict).transpose()

    print("\n--- Confusion Matrix ---")
    print(cm)
    print("\n--- Classification Metrics Report ---")
    print(report_df)

    return {
        'confusion_matrix': cm.tolist(),
        'metrics_table': report_df.to_dict()
    }


@test
def test_evaluation(output, *args) -> None:
    assert 'confusion_matrix' in output, "Missing confusion matrix in evaluation output"
    assert 'metrics_table' in output, "Missing metrics table in evaluation output"
