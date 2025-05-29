# 🏗 Odisha RERA Scraper with Streamlit UI

A Python-based web scraper built using Selenium and BeautifulSoup to extract **real estate project** and **promoter information** from the official [Odisha RERA website](https://rera.odisha.gov.in). The data is displayed through a modern **Streamlit interface** with options to **preview and download CSV** files.

---

## 🔍 Features

- Extracts:
  - Project Name
  - RERA Registration Number
  - Promoter Name
  - Promoter Address
  - GST Number
- Intuitive UI built using Streamlit
- Download scraped data as a CSV file
- Fully automated using Selenium WebDriver
- Anti-bot evasion using custom Chrome options
- Cleanly refactored and modular codebase

---

## 🛠 Tech Stack

- **Python 3.8+**
- **Selenium** (for browser automation)
- **BeautifulSoup4** (for HTML parsing)
- **Streamlit** (for UI)
- **pandas** (for data storage/export)
- **ChromeDriverManager** (automatic driver management)

---
## 🚀 How to Run the Project

### ✅ Run from Terminal

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd odisha <directory>

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the Streamlit App:
   ```bash
    streamlit run scraper.py
    ```


