import pandas as pd
from sklearn.tree import DecisionTreeClassifier

if 'transformer' not in globals() and 'data_exporter' not in globals():
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
def train(df: pd.DataFrame, *args, **kwargs) -> dict:
    """
    Trains DecisionTreeClassifier on Iris train split.
    Takes runtime parameter max_depth (default 3).
    """
    max_depth = kwargs.get('max_depth', 3)
    if max_depth is not None:
        max_depth = int(max_depth)

    feature_cols = [c for c in df.columns if c not in ['target', 'split']]
    train_df = df[df['split'] == 'train']
    test_df = df[df['split'] == 'test']

    X_train = train_df[feature_cols]
    y_train = train_df['target']
    X_test = test_df[feature_cols]
    y_test = test_df['target']

    clf = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    clf.fit(X_train, y_train)

    train_acc = float(clf.score(X_train, y_train))
    test_acc = float(clf.score(X_test, y_test))

    preds = clf.predict(X_test)
    test_results = test_df.copy()
    test_results['prediction'] = preds

    print(f"[train_model] max_depth={max_depth} | Train Acc: {train_acc:.4f} | Test Acc: {test_acc:.4f}")

    return {
        'model': clf,
        'feature_names': feature_cols,
        'max_depth': max_depth,
        'train_accuracy': train_acc,
        'test_accuracy': test_acc,
        'test_results': test_results
    }


@test
def test_accuracy(output, *args) -> None:
    """
    Quality gate: Model test accuracy must be at least 0.90 (90%).
    If accuracy < 0.90, this test fails and stops downstream blocks (save_results).
    """
    acc = output['test_accuracy']
    assert acc >= 0.90, f"Model test accuracy {acc:.4f} is below required threshold 0.90!"
