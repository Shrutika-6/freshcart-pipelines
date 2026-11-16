import os
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

def run_experiment():
    df = load_iris(as_frame=True).frame
    results = []
    
    for depth in [1, 2, 3, 4, 5]:
        pred_file = "iris_predictions.csv"
        if os.path.exists(pred_file):
            os.remove(pred_file)
            
        train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['target'])
        
        feature_cols = [c for c in df.columns if c not in ['target', 'split']]
        clf = DecisionTreeClassifier(max_depth=depth, random_state=42)
        clf.fit(train_df[feature_cols], train_df['target'])
        
        test_acc = float(clf.score(test_df[feature_cols], test_df['target']))
        
        # Test gate: accuracy >= 0.90
        passed = test_acc >= 0.90
        if passed:
            test_df_copy = test_df.copy()
            test_df_copy['prediction'] = clf.predict(test_df[feature_cols])
            test_df_copy.to_csv(pred_file, index=False)
            file_created = os.path.exists(pred_file)
        else:
            file_created = False
            
        results.append({
            "max_depth": depth,
            "test_accuracy": round(test_acc, 4),
            "test_accuracy_passed": "Yes" if passed else "No (Fails gate)",
            "csv_created": "Yes" if file_created else "No"
        })
        
    print("| max_depth | Test accuracy | test_accuracy passed? | iris_predictions.csv created? |")
    print("|---|---|---|---|")
    for r in results:
        print(f"| {r['max_depth']} | {r['test_accuracy']:.2%} | {r['test_accuracy_passed']} | {r['csv_created']} |")

if __name__ == '__main__':
    run_experiment()
