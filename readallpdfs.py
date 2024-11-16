import os
import csv
import pymupdf

def extract_month_year(filename):
    prefix = filename[:7].lower()
    month = prefix[:3]
    year = prefix[3:]
    if year.endswith('a'):
        year = year.lower().replace('k', '00')[:-1]
    else:
        year = year.lower().replace('k', '0')
    return month, year

def search_keyword_in_pdf(pdf_path, keyword, csv_writer):
    document = pymupdf.open(pdf_path)
    filename = os.path.basename(pdf_path)
    month, year = extract_month_year(filename)
    
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text = page.get_text("text")
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if keyword in line:
                try:
                    value1 = lines[i + 1].strip().replace(',', '')
                    value2 = lines[i + 2].strip().replace(',', '')
                    if value1.isdigit() and value2.isdigit():
                        csv_writer.writerow([year, month, value1, value2])
                    else:
                        print(f"Expected two numbers in lines: {lines[i+1]} and {lines[i+2]} page: {page_num} - {pdf_path}")
                except IndexError:
                    print(f"Insufficient lines after keyword '{keyword}' on page: {page_num} - {pdf_path}")

def process_directory(directory_path, keyword, csv_path):
    with open(csv_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['Year', 'Month', 'Pax', 'PaxLastyr'])
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(directory_path, filename)
                search_keyword_in_pdf(pdf_path, keyword, csv_writer)

if __name__ == "__main__":
    directory_path = "traffic_files/"
    search_term = "VISAKHAPATNAM"
    output_csv_path = "output.csv"
    process_directory(directory_path, search_term, output_csv_path)
