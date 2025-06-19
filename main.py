import logging
import logging.handlers
import os
from lxml import etree
from lxml import html
from requests_ntlm import HttpNtlmAuth
import getpass  # To get your Windows username and password
import csv

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)


if __name__ == "__main__":
    url = "http://mchpweb/dms/specindex/MCHPSearch.aspx?Spec%20Status=Current&Spec%20Num%20Disp=PI-24069"

    username = "A78133"
    password = "09614215898Asd."
    r = requests.get(url,  auth=HttpNtlmAuth(username, password))
    


    if r.status_code == 200:
        print("Request was successful.")
        tree = html.fromstring(r.content)
        target_prefix = "/dms/specindex/specindexlib/PI/"

        # XPath with starts-with()
        new_hrefs = ["http://mchpweb"+a.get("href") for a in tree.xpath(f'//a[starts-with(@href, "{target_prefix}")]')]
        print(new_hrefs)

        csv_file = "dms_link.csv"
        existing_hrefs = set()

        if os.path.exists(csv_file):
            with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header if present
                for row in reader:
                    if row:  # Avoid empty rows
                        existing_hrefs.add(row[0])

        # Step 3: Filter new hrefs
        unique_new_hrefs = [href for href in new_hrefs if href not in existing_hrefs]

        # Step 4: Append only new, unique hrefs
        if unique_new_hrefs:
            file_exists = os.path.isfile(csv_file)
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Href"])  # Add header if file didn't exist
                for href in unique_new_hrefs:
                    writer.writerow([href])

        print(f"{len(unique_new_hrefs)} new unique href(s) added to {csv_file}")
        logger.info(unique_new_hrefs)

