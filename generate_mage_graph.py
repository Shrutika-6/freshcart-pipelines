import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_c1_pipeline():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')

    blocks = [
        {"name": "load_iris\n(data_loader)", "test": "@test: test_output\n(len=150, cols=5)", "x": 0.08, "y": 0.5, "color": "#E3F2FD", "border": "#1976D2"},
        {"name": "validate_iris\n(transformer)", "test": "@test: test_no_missing\n@test: test_three_classes", "x": 0.32, "y": 0.5, "color": "#FFF3E0", "border": "#F57C00"},
        {"name": "prepare_data\n(transformer)", "test": "@test: test_output\n(split col present)", "x": 0.56, "y": 0.5, "color": "#FFF3E0", "border": "#F57C00"},
        {"name": "train_model\n(transformer)", "test": "@test: test_accuracy\n(acc >= 0.90 gate)", "x": 0.80, "y": 0.5, "color": "#E8F5E9", "border": "#388E3C"},
        {"name": "save_results\n(data_exporter)", "test": "@test: test_file_exists\n(iris_predictions.csv)", "x": 0.95, "y": 0.75, "color": "#FCE4EC", "border": "#C2185B"},
        {"name": "evaluate_model\n(transformer)", "test": "@test: test_evaluation\n(cm & metrics table)", "x": 0.95, "y": 0.25, "color": "#EDE7F6", "border": "#512DA8"},
    ]

    for b in blocks:
        # Draw block box
        rect = patches.FancyBboxPatch(
            (b["x"] - 0.09, b["y"] - 0.12), 0.18, 0.24,
            boxstyle="round,pad=0.03", ec=b["border"], fc=b["color"], lw=2.5
        )
        ax.add_patch(rect)
        ax.text(b["x"], b["y"] + 0.03, b["name"], ha="center", va="center", fontsize=10, weight="bold")
        ax.text(b["x"], b["y"] - 0.06, b["test"], ha="center", va="center", fontsize=8, style="italic", color="#333333")

    # Connect arrows
    arrow_props = dict(facecolor='#424242', edgecolor='#424242', width=1.5, headwidth=8)
    ax.annotate('', xy=(0.23, 0.5), xytext=(0.17, 0.5), arrowprops=arrow_props)
    ax.annotate('', xy=(0.47, 0.5), xytext=(0.41, 0.5), arrowprops=arrow_props)
    ax.annotate('', xy=(0.71, 0.5), xytext=(0.65, 0.5), arrowprops=arrow_props)

    # Branch arrows from train_model
    ax.annotate('', xy=(0.87, 0.72), xytext=(0.85, 0.58), arrowprops=arrow_props)
    ax.annotate('', xy=(0.87, 0.28), xytext=(0.85, 0.42), arrowprops=arrow_props)

    plt.title("Mage Iris Machine Learning Orchestration Pipeline Graph (Part C1 & C3)", fontsize=14, weight="bold", pad=20)
    plt.tight_layout()
    plt.savefig("c:/Users/Asus/Desktop/DE/freshcart-pipelines/mage_pipeline_graph.png", dpi=300)
    print("Saved pipeline graph to mage_pipeline_graph.png")

if __name__ == '__main__':
    draw_c1_pipeline()
