"""
PDF Extraction Module
Extracts transaction data from bank statement PDFs
"""

import logging
import os
import re

import pandas as pd
import pdfplumber
import wordninja

from src.config import get_config_value

logger = logging.getLogger(__name__)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

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

def extract_transactions_from_page(lines, current_year):
    """
    Extracts transaction records from lines of text on a single page.
    Returns (transactions, last_month_idx).
    """
    transactions = []
    last_month_idx = -1
    deposit_triggers = get_config_value('EXTRACTION.DEPOSIT_TRIGGERS', ['Deposit', 'MB-Transferfrom'])

    for line in lines:
        line = line.strip()
        if any(line.startswith(month) for month in MONTHS):
            parts = line.split()
            if not parts[-1].isdigit() and parts[-1].isalpha():
                del parts[-1]

            date = parts[0]
            month_idx = MONTHS.index(date[:3])
            last_month_idx = month_idx

            if current_year:
                date = f"{date}{current_year}"
                try:
                    date = pd.to_datetime(date, format='%b%d%Y').strftime('%b %d, %Y')
                except ValueError:
                    continue

            balance = parts[-1]
            if any(tag in parts for tag in deposit_triggers):
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

    return transactions, last_month_idx

def process_single_pdf(file_path):
    """
    Processes a single PDF file and extracts all transactions from it.
    Returns a DataFrame of all transactions in the file.
    """
    transactions = []

    with pdfplumber.open(file_path) as pdf:
        current_year = None
        last_month_idx = -1

        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split('\n')

            if not current_year:
                current_year = extract_year(lines)

            page_transactions, page_last_month = extract_transactions_from_page(lines, current_year)

            # Detect year rollover (e.g., Dec -> Jan)
            if last_month_idx == 11 and page_last_month == 0 and current_year:
                current_year = str(int(current_year) + 1)
                # Re-process this page with the new year
                page_transactions, page_last_month = extract_transactions_from_page(lines, current_year)

            if page_last_month >= 0:
                last_month_idx = page_last_month

            transactions.extend(page_transactions)

    columns = ['Date', 'Description', 'Withdrawals ($)', 'Deposits ($)', 'Balance ($)']
    return pd.DataFrame(transactions, columns=columns)

def extract_all_pdfs(pdf_directory):
    """
    Reads all PDF files in a specified directory and extracts transactions.
    Returns a single consolidated DataFrame of all transactions.
    """
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

    if not pdf_files:
        raise ValueError(f"No PDF files found in {pdf_directory}")

    logger.info("Found %d PDF files to process...", len(pdf_files))

    dataframes = []
    for file_name in pdf_files:
        file_path = os.path.join(pdf_directory, file_name)
        logger.info("Processing: %s", file_name)
        try:
            transactions = process_single_pdf(file_path)
            dataframes.append(transactions)
            logger.info("Extracted %d transactions from %s", len(transactions), file_name)
        except Exception as e:
            logger.error("Error processing %s: %s", file_name, e)

    if dataframes:
        all_transactions = pd.concat(dataframes, ignore_index=True)
    else:
        all_transactions = pd.DataFrame(columns=['Date', 'Description', 'Withdrawals ($)', 'Deposits ($)', 'Balance ($)'])

    return all_transactions

if __name__ == "__main__":
    # Test extraction
    import sys
    if len(sys.argv) > 1:
        pdf_dir = sys.argv[1]
        df = extract_all_pdfs(pdf_dir)
        print(f"\nTotal transactions extracted: {len(df)}")
        print(df.head())
