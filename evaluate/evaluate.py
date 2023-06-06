import pandas as pd
from argilla.client.api import load, log
from argilla.client.datasets import DatasetForTextClassification
from argilla.client.models import TextClassificationRecord
from sklearn.metrics import classification_report
from tabulate import tabulate

from ingest.notion import database_id, notion_client, notion_db_to_df
from utils import logger

DATASET_NAME = "tech_classification_validation"


def format_metadata(record):
    meta_cols = set(record.keys()) - {"text", "vector"}
    return {k: v for k, v in record.to_dict().items() if k in meta_cols}


def format_classification_record(record):
    record = TextClassificationRecord(
        prediction=[(record.is_tech_related, 1.0)],
        text=record.text,
        multi_label=False,
        metadata=format_metadata(record),
    )
    return record


def log_notion_db_to_argilla():
    classification_records = (
        notion_db_to_df(notion_client, database_id)
        .pipe(lambda x: x[x.text.apply(lambda y: len(y.split(" ")) > 5)])
        .apply(format_classification_record, axis=1)
        .tolist()
    )
    logger.info(f"Logging {len(classification_records)} records to Argilla")
    dataset_rg = DatasetForTextClassification(classification_records)
    log(
        records=dataset_rg,
        name=DATASET_NAME,
        tags={"overview": "Verify zero-shot LLM classifications"},
        background=False,
        verbose=True,
    )


def evaluate_argilla_dataset():
    # after some annotations, load in dataset
    labelled = (
        load(DATASET_NAME)
        .to_pandas()
        .pipe(lambda x: x[~x.annotation.isna()])
        .assign(prediction=lambda x: x.prediction.apply(lambda y: y[0][0]))
    )
    cr = classification_report(
        labelled.annotation, labelled.prediction, output_dict=True
    )
    cr = pd.DataFrame(cr).T
    print(tabulate(cr, headers="keys", tablefmt="psql"))


if __name__ == "__main__":
    # log_notion_db_to_argilla()
    evaluate_argilla_dataset()
