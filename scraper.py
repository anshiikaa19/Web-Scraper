import time
import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

# ───────────────────────────────────────────────────────────────
# Extract project name and RERA ID from the HTML content
# ───────────────────────────────────────────────────────────────
def get_project_info(html_content):
    parser = BeautifulSoup(html_content, "html.parser")

    proj_label = parser.find("label", string="Project Name")
    proj_wrapper = proj_label.find_parent("div", class_="details-project ms-3") if proj_label else None
    project_title = proj_wrapper.find("strong").text.strip() if proj_wrapper and proj_wrapper.find("strong") else ""

    rera_label = parser.find("label", string="RERA Regd. No.")
    rera_wrapper = rera_label.find_parent("div", class_="details-project ms-3") if rera_label else None
    rera_id = rera_wrapper.find("strong").text.strip() if rera_wrapper and rera_wrapper.find("strong") else ""

    return [project_title, rera_id]

# ───────────────────────────────────────────────────────────────
# Extract promoter details: Name, Address, GST number
# ───────────────────────────────────────────────────────────────
def get_promoter_info(html_block):
    parser = BeautifulSoup(html_block, "html.parser")

    def extract_detail(tag_text):
        # Locate label containing the target text
        field_label = parser.find("label", string=lambda val: val and tag_text in val)
        if not field_label:
            return ""
        # Look for the strong tag next to or inside the same container
        detail_field = field_label.find_next_sibling("strong") or field_label.parent.find("strong")
        return detail_field.text.strip() if detail_field else ""

    entity_name = extract_detail("Propietory Name") or extract_detail("Company Name")
    entity_address = extract_detail("Current Residence Address") or extract_detail("Registered Office Address")
    entity_gst = extract_detail("GST No.")

    return [entity_name, entity_address, entity_gst]

# ───────────────────────────────────────────────────────────────
# Main scraping function: extracts data from the RERA portal
# ───────────────────────────────────────────────────────────────
def fetch_rera_data(item_limit=5):
    # Setup Chrome options to mimic real user behavior
    chrome_config = Options()
    chrome_config.add_argument("user-agent=Mozilla/5.0")
    chrome_config.add_argument("--disable-blink-features=AutomationControlled")
    chrome_config.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_config.add_experimental_option("useAutomationExtension", False)

    # Initialize Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_config)

    # Hide WebDriver detection
    browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    data_records = []
    ui_wait = WebDriverWait(browser, 15)

    try:
        # Open the project list page
        browser.get("https://rera.odisha.gov.in/projects/project-list")
        ui_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.btn.btn-primary")))
        view_buttons = browser.find_elements(By.CSS_SELECTOR, "a.btn.btn-primary")

        for idx in range(min(item_limit, len(view_buttons))):
            # Refresh button list and click the next one
            ui_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.btn.btn-primary")))
            view_buttons = browser.find_elements(By.CSS_SELECTOR, "a.btn.btn-primary")

            browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", view_buttons[idx])
            time.sleep(1)
            view_buttons[idx].click()

            # Wait and grab project info
            time.sleep(3)
            html_project = browser.page_source
            proj_name, rera_code = get_project_info(html_project)

            # Try switching to promoter details tab
            try:
                promoter_tab = ui_wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Promoter Details")))
                browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", promoter_tab)
                time.sleep(1)
                promoter_tab.click()
            except Exception as issue:
                st.warning(f"[{idx + 1}] Unable to access promoter tab: {issue}")
                browser.back()
                continue

            # Grab promoter info
            time.sleep(3)
            html_promoter = browser.page_source
            org_name, org_addr, org_gst = get_promoter_info(html_promoter)

            # Save collected data
            data_records.append([proj_name, rera_code, org_name, org_addr, org_gst])
            browser.back()

    finally:
        # Always close the browser
        browser.quit()

    return data_records

# ───────────────────────────────────────────────────────────────
# Streamlit UI to interact with the scraper
# ───────────────────────────────────────────────────────────────

st.title("Odisha RERA Project Scraper")
st.markdown("Scrapes project and promoter details from [rera.odisha.gov.in](https://rera.odisha.gov.in")

# User input: how many projects to scrape
project_count = st.slider("Select how many projects to retrieve", min_value=1, max_value=20, value=6)

# Button to start scraping
if st.button("Begin Scraping"):
    with st.spinner("Fetching records, please wait..."):
        output = fetch_rera_data(project_count)
        if output:
            df_out = pd.DataFrame(output, columns=["Project Name", "RERA Number", "Promoter Name", "Address", "GST Number"])
            st.success(f"{len(df_out)} project entries collected successfully.")
            st.dataframe(df_out, use_container_width=True)

            # Allow download of data as CSV
            csv_output = df_out.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv_output, "odisha_rera_export.csv", "text/csv")
        else:
            st.error("No records found or an error occurred.")
