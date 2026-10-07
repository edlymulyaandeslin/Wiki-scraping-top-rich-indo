from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
from mongodb import db



def extract(url, year):
    headers = {
        "User-Agent": "WikiScraper/1.0 (personal learning project; contact: your-email@example.com)"
    }
    page = requests.get(url, headers=headers).text
    data = BeautifulSoup(page, "html.parser")

    section = data.find("section", attrs={"aria-labelledby": year})
    tables = section.find_all("table", class_=["wikitable"])
    if len(tables) == 0:
        return [[], year], False

    table = tables[-1]
    rows = table.find_all("tr")[1:-1]

    header_column = [th.text.strip() for th in table.find("tr").find_all(["th", "td"]) if th.text.strip()]

    df = pd.DataFrame(columns=header_column)

    for row in rows:
        values = [td.text.strip() for td in row.find_all("td")]

        data_dict = dict(zip(header_column, values))

        df2 = pd.DataFrame([data_dict])
        df = pd.concat([df,df2], ignore_index=True)

    return [df.to_dict("records"), year], True

def load_bronze(data, year):
    collection = db[f"bronze.top_rich_indo_{year}"]
    collection.delete_many({})
    collection.insert_many(data)

def read_bronze():
    collection = db["top_rich_indo_2025"]
    data = [doc for doc in collection.find()]
    return data

def log_progress(message):
    timestamp = f"%Y-%m-%d %H:%M:%S"
    now = datetime.now()
    date_format = now.strftime(timestamp)
    with open("./log.txt", "a") as outfile:
         outfile.write(f"{date_format}: {message}\n")
         print(f"{date_format}: {message}")


target_url = "https://id.wikipedia.org/wiki/Daftar_tokoh_Indonesia_menurut_kekayaan"
log_progress(f"Extracting data from {target_url}")

for year in range(2006, 2026):
    log_progress(f"Processing year - {year}")
    [extracted_data, year], success = extract(target_url, year)

    if not success:
        log_progress(f"Data {year} not found")
        log_progress("--------------------")
        continue

    log_progress(f"Load {year} to bronze layer")
    load_bronze(extracted_data, year)
    log_progress("--------------------")

log_progress("Extracting Done")
