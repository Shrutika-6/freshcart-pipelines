import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_end_to_end_architecture():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')

    # Color palette
    c_git = "#E0F2FE"
    c_ci = "#F0FDF4"
    c_elt = "#FEF3C7"
    c_ml = "#F3E8FF"
    c_stream = "#FEE2E2"

    # Box 1: Git & GitHub
    rect1 = patches.FancyBboxPatch((0.05, 0.65), 0.25, 0.28, boxstyle="round,pad=0.03", ec="#0284C7", fc=c_git, lw=2)
    ax.add_patch(rect1)
    ax.text(0.175, 0.88, "Part A: Git & CI/CD", ha="center", weight="bold", fontsize=11, color="#0369A1")
    ax.text(0.175, 0.77, "• freshcart-pipelines repo\n• pytest suite\n• GitHub Actions CI\n(Green/Red quality gates)", ha="center", fontsize=9)

    # Box 2: Stream (RabbitMQ)
    rect2 = patches.FancyBboxPatch((0.05, 0.15), 0.25, 0.35, boxstyle="round,pad=0.03", ec="#DC2626", fc=c_stream, lw=2)
    ax.add_patch(rect2)
    ax.text(0.175, 0.44, "Part D: RabbitMQ Stream", ha="center", weight="bold", fontsize=11, color="#B91C1C")
    ax.text(0.175, 0.30, "• Topic Exchange (rapido-dispatch)\n• Driver private queues (* and #)\n• ACK / NACK handling\n• Lakehouse Consumer (1-min batch)", ha="center", fontsize=9)

    # Box 3: FreshCart Snowflake ELT
    rect3 = patches.FancyBboxPatch((0.40, 0.25), 0.28, 0.60, boxstyle="round,pad=0.03", ec="#D97706", fc=c_elt, lw=2)
    ax.add_patch(rect3)
    ax.text(0.54, 0.80, "Part B: Snowflake ELT Pipeline", ha="center", weight="bold", fontsize=11, color="#B45309")
    ax.text(0.54, 0.52, "• Bronze (raw_orders, 8 rows)\n  └─ PUT + COPY INTO\n• Silver (clean, dedup, quarantine)\n  └─ currency & SCD-2 checks\n• Gold (fct_orders)\n  └─ row_hash & MERGE (idempotent)\n• quality_checks() validation", ha="center", fontsize=9)

    # Box 4: Mage ML Pipeline
    rect4 = patches.FancyBboxPatch((0.76, 0.25), 0.22, 0.60, boxstyle="round,pad=0.03", ec="#7E22CE", fc=c_ml, lw=2)
    ax.add_patch(rect4)
    ax.text(0.87, 0.80, "Part C: Mage ML Pipeline", ha="center", weight="bold", fontsize=11, color="#6B21A8")
    ax.text(0.87, 0.52, "• load_iris & validate_iris\n• prepare_data (80/20)\n• train_model (DecisionTree)\n• @test gates (acc >= 90%)\n• save_results (predictions.csv)\n• evaluate_model (metrics & CM)", ha="center", fontsize=9)

    # Arrows connecting the pieces
    arrow_props = dict(facecolor='#374151', edgecolor='#374151', width=1.5, headwidth=7)
    
    # Git -> ELT & Mage (deploys/tests code)
    ax.annotate('CI Verified Code', xy=(0.40, 0.72), xytext=(0.30, 0.75), arrowprops=arrow_props, fontsize=8, weight="bold")
    
    # Stream -> ELT (Bonus: lands batch raw orders into bronze)
    ax.annotate('Stream Landing\n(write_landing -> load_file)', xy=(0.40, 0.35), xytext=(0.30, 0.30), arrowprops=arrow_props, fontsize=8, weight="bold")

    # ELT -> ML (Gold tables feed curated feature datasets)
    ax.annotate('Curated Gold Data\nfor Training & Inference', xy=(0.76, 0.55), xytext=(0.68, 0.55), arrowprops=arrow_props, fontsize=8, weight="bold")

    plt.title("End-to-End Enterprise Data Platform Architecture (Part E2)", fontsize=14, weight="bold", pad=15)
    plt.tight_layout()
    plt.savefig("c:/Users/Asus/Desktop/DE/freshcart-pipelines/end_to_end_architecture.png", dpi=300)
    print("Saved end-to-end architecture diagram to end_to_end_architecture.png")

if __name__ == '__main__':
    draw_end_to_end_architecture()
