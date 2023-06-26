import datetime
import sys
import unittest
from unittest import TestCase

import pandas as pd

sys.path.append("../..")
sys.path.append("..")
from etl_helpers import utils
import config


class Test(TestCase):
    def test_split_list(self):
        start_date = datetime.datetime(2011, 1, 1)
        end_date = datetime.datetime(2017, 1, 1)
        range_of_dates = pd.date_range(
            start_date, end_date
        )
        for c in range(2, 20):
            chunked_dates = utils.split_list(range_of_dates, c)
            self.assertTrue(
                len(range_of_dates == sum((len(l) for l in chunked_dates)))
            )


class AsyncFunctionTest(TestCase):

    def setUp(self):
        import asyncio
        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        self.loop.close()

    def test_async_function(self):
        async def start_google_chrome():
            from pyppeteer import launch
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
            page = await browser.newPage()
            await page.goto(
                'https://www.mercatoelettrico.org/It/download/DownloadDati.aspx?val=MGPGAS_SintesiScambio',

            )
            await page.waitForSelector('#ContentPlaceHolder1_CBAccetto1')
            await browser.close()
            # Add assertions to test the behavior of the async function

        try:
            self.loop.run_until_complete(start_google_chrome())
        except Exception as e:
            self.fail(f"Failed ot launch google-chrome with {e}")


if __name__ == '__main__':
    unittest.main()
