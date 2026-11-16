# FreshCart Pipelines

**Student Name:** Shende Shrutika Ashok  
**Roll Number:** 23bcs232  
**Course:** Data Engineering · Pipeline Orchestration  
**Assignment:** From Git to Gold (Version control, ELT, ML pipelines and event streaming, end to end)

---

## Repository Structure

```
freshcart-pipelines/
├── README.md
├── .gitignore
├── requirements.txt
├── elt/
│   └── freshcart_elt.ipynb
├── iris_project/
│   ├── metadata.yaml
│   ├── data_loaders/
│   │   └── load_iris.py
│   ├── transformers/
│   │   ├── prepare_data.py
│   │   └── validate_iris.py
│   └── data_exporters/
│       ├── train_model.py
│       ├── evaluate_model.py
│       └── save_results.py
├── stream/
│   ├── dispatcher.py
│   ├── driver.py
│   └── lakehouse_consumer.py
├── tests/
│   └── test_prepare_data.py
└── .github/workflows/
    └── ci.yml
```

## Overview of Components
- **Part A (Git & CI/CD):** Version control workflow, branch protection, pytest test suite, and automated GitHub Actions CI pipeline.
- **Part B (FreshCart ELT on Snowflake):** Medallion architecture (Bronze -> Silver -> Gold + Quarantine) with data quality checks, SCD-2 customer dimension, and idempotent upserts.
- **Part C (Mage ML Pipeline):** Modular ML pipeline training an Iris DecisionTreeClassifier with runtime gates, test-driven validation, and an evaluation branch.
- **Part D (RabbitMQ Streaming):** Topic exchange pub/sub event streaming for real-time dispatch with exact binding patterns and ACK/NACK error handling.
- **Bonus:** Streaming orders from RabbitMQ landed and merged into the Snowflake gold table without duplication.
