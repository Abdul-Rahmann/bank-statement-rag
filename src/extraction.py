"""
PDF Extraction Module
Extracts transaction data from bank statement PDFs
"""

import os
import re
import pandas as pd
import pdfplumber
import wordninja

DEPOSIT_TRIGGERS = ['Deposit', 'MB-Transferfrom']

def split_concatenated_text(text):
    """Splits concatenated text into readable words using wordninja."""
    return " ".join(wordninja.split(text))

def extract_year(lines):
    """
    Extracts the year from lines of text in a PDF.
    Returns the first valid 4-digit year found or None if no year is detected.
    """
    for line in lines:
        year_match = re.search(r'\b(20\d{2})\b', line)
        if year_match:
            return year_match.group(1)
    return None

def extract_transactions_from_page(lines, extracted_year):
    """
    Extracts transaction records from lines of text on a single page.
    Returns a list of structured transactions.
    """
    transactions = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for line in lines:
        line = line.strip()
        if any(line.startswith(month) for month in months):
            parts = line.split()
            if not parts[-1].isdigit() and parts[-1].isalpha():
                del parts[-1]

            date = parts[0]
            if extracted_year:
                date = f"{date}{extracted_year}"
                try:
                    date = pd.to_datetime(date, format='%b%d%Y').strftime('%b %d, %Y')
                except ValueError:
                    continue

            balance = parts[-1]
            if any(tag in parts for tag in DEPOSIT_TRIGGERS):
                deposit = parts[-2]
                withdrawal = None
            else:
                deposit = None
                withdrawal = parts[-2]

            description = ' '.join([part for part in parts[1:-2] if not re.match(r'^\d+(\.\d{1,2})?$', part)])
            description = split_concatenated_text(description)
            transactions.append([date, description, withdrawal, deposit, balance])
        elif transactions:
            transactions[-1][1] += ' ' + split_concatenated_text(line)

    return transactions

def process_single_pdf(file_path):
    """
    Processes a single PDF file and extracts all transactions from it.
    Returns a DataFrame of all transactions in the file.
    """
    transactions = []

    with pdfplumber.open(file_path) as pdf:
        extracted_year = None

        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split('\n')

            if not extracted_year:
                extracted_year = extract_year(lines)

            transactions.extend(extract_transactions_from_page(lines, extracted_year))

    columns = ['Date', 'Description', 'Withdrawals ($)', 'Deposits ($)', 'Balance ($)']
    return pd.DataFrame(transactions, columns=columns)

def extract_all_pdfs(pdf_directory):
    """
    Reads all PDF files in a specified directory and extracts transactions.
    Returns a single consolidated DataFrame of all transactions.
    """
    all_transactions = pd.DataFrame()

    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

    if not pdf_files:
        raise ValueError(f"No PDF files found in {pdf_directory}")

    print(f"\nFound {len(pdf_files)} PDF files to process...")

    for file_name in pdf_files:
        file_path = os.path.join(pdf_directory, file_name)
        print(f"   Processing: {file_name}")
        try:
            transactions = process_single_pdf(file_path)
            all_transactions = pd.concat([all_transactions, transactions], ignore_index=True)
            print(f"✓ Extracted {len(transactions)} transactions")
        except Exception as e:
            print(f"✗ Error processing {file_name}: {e}")

    return all_transactions

if __name__ == "__main__":
    # Test extraction
    import sys
    if len(sys.argv) > 1:
        pdf_dir = sys.argv[1]
        df = extract_all_pdfs(pdf_dir)
        print(f"\nTotal transactions extracted: {len(df)}")
        print(df.head())
