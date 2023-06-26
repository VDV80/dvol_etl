import datetime
import io
import logging
import sys
import zipfile
from pathlib import Path
from typing import List

import pandas as pd

sys.path.append(".")
import config

logger = logging.getLogger()


def transform_mgp_data(range_of_dates: List[datetime.datetime], allow_fixes=True):
    data_frames = []
    cols = []
    counter = 0
    for d in range_of_dates:
        logger.info(f"Processing {d}")
        file_mame = f"MGPGAS_SintesiScambio" \
                    f"{d.strftime(format='%Y%m%d')}" \
                    f"{d.strftime(format='%Y%m%d')}" \
                    f".zip"
        file_path = Path(config.temp_store_path) / file_mame
        try:
            test_df = read_xml_from_zip(file_path)
            trimmed_columns = [c.strip() for c in test_df.columns]
            test_df.columns = trimmed_columns
            cols.append(trimmed_columns)
            if all([c in trimmed_columns for c in ["DataSessione", "NomeProdotto", "PrezzoMedio"]]):
                test_df = test_df[
                    ["DataSessione", "NomeProdotto", "PrezzoMedio"]
                ][test_df["DataSessione"].notna()]
                slice_first_record = test_df.sort_values(by="NomeProdotto").iloc[0, :]
                data_frames.append(
                    slice_first_record
                )
                counter += 1
                logger.info(f"Got clean table for date {d} now {counter} records")
            else:
                col_check = [
                    c in trimmed_columns
                    for c in ["DataSessione", "NomeProdotto", "PrezzoMedio"]
                ]
                missing = [
                    r[1] for r in
                    zip(col_check, ["DataSessione", "NomeProdotto", "PrezzoMedio"])
                    if r[0] is False
                ]
                if missing == ["PrezzoMedio"] and allow_fixes:
                    test_df["PrezzoMedio"] = (test_df["PrezzoMinimo"] + test_df["PrezzoMassimo"]) / 2
                    test_df = test_df[
                        ["DataSessione", "NomeProdotto", "PrezzoMedio"]
                    ][test_df["DataSessione"].notna()]
                    slice_first_record = test_df.sort_values(by="NomeProdotto").iloc[0, :]
                    data_frames.append(
                        slice_first_record
                    )
                    counter += 1
                    logger.info(f"Got clean table for date {d} now {counter} records -- DERIVED")

                logger.info(f"Missing table {d} due to {missing} columns", exc_info=True)
        except Exception as e:
            logger.warning(f"Failed to process date {d} with {e}")
    res_df = pd.DataFrame(data_frames)
    res_df["DataSessione"] = [
        datetime.datetime.strptime(str(int(dt)), '%Y%m%d') for dt in res_df["DataSessione"]
    ]
    # TODO -- write a check that it is always 1d forward
    logger.info(f"Found {counter} eligible records")
    return res_df


def read_xml_from_zip(zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        xml_file_name = zip_ref.namelist()[0]  # Assuming the XML file is always the first file in the ZIP
        with zip_ref.open(xml_file_name) as xml_file:
            xml_content = xml_file.read()
            df = pd.read_xml(io.BytesIO(xml_content))
    return df


def transform_and_upload_historical():
    start_date = datetime.datetime(2011, 1, 1)
    end_date = datetime.datetime(2017, 1, 1)
    this_range_of_dates = pd.date_range(
        start_date, end_date
    )

    # TODO -- move the below into the config file
    db_user = "airflow"
    db_password = "airflow"
    db_host = "air-pg-datastore-1"
    db_port = 5432
    db_name = "postgres"
    from sqlalchemy import create_engine
    # Create the SQLAlchemy engine
    engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    res = transform_mgp_data(this_range_of_dates)
    logger.info(f"Type for 'DataSessione': {type(res['DataSessione'].dtype)}")
    logger.info(f"Uploading {res.shape} df into the db")
    res.columns = ["dates", "product", "mid_price"]
    res.to_sql("hist_data", engine, if_exists="replace", index=False)
    engine.dispose()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
        level=logging.DEBUG
    )
    transform_and_upload_historical()
