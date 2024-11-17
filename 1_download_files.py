import requests
from os import path, makedirs
import time
import random
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = "https://www.aai.aero/sites/default/files/traffic-news/"
output_directory = "traffic_files"
years = range(2006, 2025)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
month_full_names = {
    "Jan": "January",
    "Feb": "February",
    "Mar": "March",
    "Apr": "April",
    "May": "May",
    "Jun": "June",
    "Jul": "July",
    "Aug": "August",
    "Sep": "September",
    "Oct": "October",
    "Nov": "November",
    "Dec": "December"
}
if not path.exists(output_directory):
    makedirs(output_directory)

def download_pdf(url, output_path):
    try:
        response = requests.get(url, verify=False) #certificate expired
        response.raise_for_status()
        with open(output_path, 'wb') as file:
            file.write(response.content)
        # print(f"Downloaded: {url}")
        return True
    except requests.exceptions.RequestException as e:
        # print(f"Failed to download {url}. Error: {e}")
        pass
    except Exception as e:
        # print(e)
        pass

def main():
    for year in years:
        for month in months:
            if year < 2015:
                month = month.lower()
            if year < 2010:
                filename = f"{month}2k{str(year)[-1:]}annex3.pdf"
            elif year <= 2018:
                filename = f"{month}2k{str(year)[-2:]}annex3.pdf"
            else:
                filename = f"{month}2k{str(year)[-2:]}Annex3.pdf"
            url = base_url + filename
            output_path = path.join(output_directory, filename)
            if not path.exists(output_path):                
                if not download_pdf(url, output_path):
                    print(year, month)
                    continue
                    # other_filenames_try(year, month)
            else:
                # print(f"File already exists: {output_path}")
                continue
            sleep_time = random.uniform(4, 12)
            # print(f"Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

def other_filenames_try(year, month):
    # for missing files
    # bruteforcing patterns from wayback, llm and google search
    suffixes = ["Annex3.pdf", "Annex3_1.pdf", "Annex3-rev.pdf", "Annex3updated.pdf", "annex3.pdf", "annex3_1.pdf", "annex3-rev.pdf", "annex3updated.pdf"]
    month_try = (month, month_full_names[month])
    for k in ["k", "K"]:
        year_suffix = f"2{k}{str(year)[-2:]}"
        for suffix in suffixes:
            for month_ in month_try:
                filename = f"{month_}{year_suffix}{suffix}"
                url = base_url + filename
                output_path = path.join(output_directory, filename)
                if not path.exists(output_path):
                    sleep_time = random.uniform(4, 8)
                    time.sleep(sleep_time)
                    if download_pdf(url, output_path):
                        return True
                        
    print(f"error in {month}, {year}")
if __name__ == "__main__":
    main()
    
