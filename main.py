import requests
import pandas as pd
from io import BytesIO
import time
import sys

# Constants for SEC API
BASE_URL = 'https://data.sec.gov/submissions/'
HEADERS = {
    'User-Agent': 'Mohammed Khaleel (mo7amd.khaled@gmail.com)',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'data.sec.gov'
}
DOWNLOAD_HEADERS = {
    'User-Agent': 'Mohammed Khaleel (mo7amd.khaled@gmail.com)',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.sec.gov'
}
CIK = '0000051143'  # TransMedics Group, Inc. CIK


def get_company_data(cik):
    """Fetch company submission data from SEC for a given CIK."""
    url = f'{BASE_URL}CIK{cik}.json'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def find_q3_10q(filings, cik):
    """Search through filings to find the Q3 2024 10-Q filing."""
    for i, form in enumerate(filings['form']):
        if filings['filingDate'][i].startswith('2024-10'):
            # Construct the link to the specific 10-Q report if found
            file_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{filings['accessionNumber'][i].replace('-', '')}/Financial_Report.xlsx"
            return file_url
    return None


def download_excel(url):
    """Download Excel file from a URL."""
    response = requests.get(url, headers=DOWNLOAD_HEADERS)
    response.raise_for_status()  # Check for successful download
    return BytesIO(response.content)


def extract_financial_data(file_content):
    """Extract EPS, Net Income, and Revenue for the 3-month period from the Excel file."""
    # Load the specific rows and columns to avoid full sheet parsing and ensure correct targeting
    income_statement_df = pd.read_excel(
        file_content,
        sheet_name='CONSOLIDATED STATEMENTS OF OPER',
        usecols="B",
        skiprows=2,  # Adjusted to start reading where the data table begins
        nrows=20     # Limit rows to capture all necessary fields up to net income and EPS
    )

    # Map indices based on verified row positions in the DataFrame for revenue, net income, and EPS
    try:
        revenue = pd.to_numeric(income_statement_df.iloc[0, 0], errors='coerce') / 1000  # Row for revenue
        net_income = pd.to_numeric(income_statement_df.iloc[16, 0], errors='coerce') / 1000  # Row for net income
        eps_basic = pd.to_numeric(income_statement_df.iloc[17, 0], errors='coerce')  # Row for basic EPS
    except IndexError:
        print("Error: Check that rows match expected layout in the Excel sheet.")
        return

    # Print the final required output if values are valid
    print(f"R: ${revenue:.2f} million")
    print(f"NI: ${net_income:.2f} million")
    print(f"EPS: ${eps_basic}")




def main():
    start_time = time.time()  # Record the start time

    try:
        # Fetch the company data
        data = get_company_data(CIK)
        filings = data.get('filings', {}).get('recent', {})

        # Find the Q3 2024 10-Q filing
        file_url = find_q3_10q(filings, data['cik'])
        print(file_url)
        if file_url:
            # Download and analyze the Excel file
            file_content = download_excel(file_url)
            extract_financial_data(file_content)
        else:
            print("No Q3 2024 10-Q filing found.")

    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
    end_time = time.time()  # Record the end time
    print(f"Script running time: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
