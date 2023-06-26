import asyncio
import datetime
import logging
import os
import sys
from multiprocessing import Pool
from pathlib import Path
from typing import List, Tuple, Dict

import pandas as pd
import redis
from pyppeteer import launch
sys.path.append("..")
import config

sys.path.append(".")
from etl_helpers import utils

logger = logging.getLogger()


async def download_historical_files_for_dates(range_of_dates: List[datetime.datetime]):
    """
    Should be used both for historical downloads and daily ones
    TODO -- consider refactor into a lib file
    :param range_of_dates: List[datetime.datetime]
    :return:
    """
    browser = await launch(
        # headless=False,
        executablePath=config.chrome_path,
        # downloadsPath=config.temp_store_path,
        args=[
            '--no-sandbox',  # Disable the sandbox for security reasons
            '--headless=new'  # note the headless here and uses new!
            # f"""--user-data-dir="{config.user_data_dir}" """
        ],
    )
    logger.info("Browser started")
    page = await browser.newPage()
    await page.goto(
        'https://www.mercatoelettrico.org/It/download/DownloadDati.aspx?val=MGPGAS_SintesiScambio',

    )
    logger.info("Got the page")
    # Wait for the page to load
    await page.waitForSelector('#ContentPlaceHolder1_CBAccetto1')
    await page.click('#ContentPlaceHolder1_CBAccetto1')
    # Mark "Accetto" checkbox
    await page.click('#ContentPlaceHolder1_CBAccetto2')
    # Click "Accetto" button
    await page.click('#ContentPlaceHolder1_Button1')
    input_start = await page.waitForSelector('#ContentPlaceHolder1_tbDataStart')
    input_end = await page.waitForSelector('#ContentPlaceHolder1_tbDataStop')
    logger.info("starting data fetch")
    for d in range_of_dates:
        logger.info(f"Getting data for {d}")
        await input_start.click({'clickCount': 3})
        # await input_start.type('\b')
        await input_start.type(
            f"{d.strftime(format='%d/%m/%Y')}"
        )

        await input_end.click({'clickCount': 3})
        # d += datetime.timedelta(days=1)
        await input_end.type(
            f"{d.strftime(format='%d/%m/%Y')}"  # confusing,but already incremented
        )
        await page.click('#ContentPlaceHolder1_btnScarica')
        await asyncio.sleep(2)

        async def handle_dialog(dialog):
            logger.info(f"Date {d} threw an alert")
            # TODO -- add redis records for warmed dates
            await dialog.accept()

        page.on('dialog', handle_dialog)
        await asyncio.sleep(2)

    await browser.close()


def mp_helper(ch_dates):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(
        download_historical_files_for_dates(ch_dates)
    )


def get_list_of_locally_available_files_for_dates(redis=False, include_warned_dates=False) -> List[datetime.datetime]:
    from pathlib import Path
    if redis:
        # TODO -- store files in redis, implement an option for "warned dates" inclusion
        pass
    else:
        # the below section just for a quick prototyping to study behaviour of the site
        downloaded_files = os.listdir(Path(config.temp_store_path))
        locally_available_dates: List[Tuple[str, str]] = [
            (fln[21:29], fln[29:37]) for fln in downloaded_files
        ]
        if not all([d[0] == d[1] for d in locally_available_dates]):
            raise IOError(
                f"Files are not compliant with single-day data files: "
                f"for dates: "
                f"{[d for d in locally_available_dates if not d[0] == d[1]]}"
            )
        else:
            locally_available_dates: List[datetime.datetime] = [
                datetime.datetime(int(d[0][:4]), int(d[0][4:6]), int(d[0][6:]))
                for d in locally_available_dates
            ]
        return locally_available_dates


def download_historical_files_missing_from_local_store():
    start_date = datetime.datetime(2011, 1, 1)
    end_date = datetime.datetime(2017, 1, 1)
    this_range_of_dates = pd.date_range(
        start_date, end_date
    )
    files_downloaded = get_list_of_locally_available_files_for_dates()
    this_range_of_dates = [d for d in this_range_of_dates if d not in files_downloaded]
    logger.info(f"{len(this_range_of_dates)} dates to download....")
    if not config.multiprocessing_data_harvest:
        asyncio.get_event_loop().run_until_complete(
            download_historical_files_for_dates(this_range_of_dates)
        )
    else:
        num_proc = min(config.number_of_processes, len(this_range_of_dates))
        chunked_dates = utils.split_list(
            this_range_of_dates, num_proc
        )

        with Pool(num_proc) as p:
            # this is ofc IO bound, but using processes to avoid overhead, esp
            # memory cloning effect should be negligible here...
            # also some bugs btw threading and signals are known
            p.map(
                mp_helper, chunked_dates
            )


def write_all_local_historical_files_into_redis():
    #  air-redis-datastore-1
    redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)
    downloaded_files = os.listdir(Path(config.temp_store_path))
    locally_available_files_by_dates: Dict[str, str] = {
        fln[21:29]: fln for fln in downloaded_files
        if fln[21:29] == fln[29:37]
    }
    # Read the zip file as binary data
    for f in locally_available_files_by_dates:
        with open(Path(config.temp_store_path) / locally_available_files_by_dates[f], 'rb') as file:
            zip_data = file.read()
        redis_client.hset('available_files_by_date', f, zip_data)
        logger.info(f"loaded {f}")


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
        level=logging.DEBUG
    )
    download_historical_files_missing_from_local_store()
    # write_all_local_historical_files_into_redis()
