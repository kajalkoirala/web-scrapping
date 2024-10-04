import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Case numbers and their corresponding URLs
case_urls = {
    "080-CR-0096": "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno=278473",
    "080-CR-0123": "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno=278797",
    "080-CR-0199": "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno=279673",
    "080-CR-0187": "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno=279599",
    "080-CR-0190": "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno=279607",
    "080-CR-0202": "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno=279741",
    "080-CR-0212": "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno=279991",
    "080-CR-0001": "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno=276885",
    "080-CR-0002": "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details&num=1&mode=view&caseno=276893"
}

def fetch_case_data(case_number):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up the Chrome Driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Get the URL for the provided case number
    url = case_urls.get(case_number)

    if url:
        # Navigate to the URL
        driver.get(url)

        # Give the page some time to load
        time.sleep(3)

        # Initialize the data structure
        case_data = {
            case_number: {
                "मुद्दाको विवरण": {},
                "लगाब मुद्दाहरुको विवरण": [],
                "तारेख विवरण": [],
                "मुद्दाको स्थितीको बिस्तृत विवरण": [],
                "पेशी को विवरण": []
            }
        }

        # Extract "मुद्दाको विवरण"
        try:
            details_rows = driver.find_elements(By.XPATH, "/html/body/div[3]/div/table/tbody/tr[position() <= 15 and position() != 12]")
            for row in details_rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 2:
                    key = cols[0].text.strip().replace(':', '').strip()
                    value = cols[1].text.strip() if cols[1].text.strip() else None  # Set to None if empty
                    if key and value:  # Only add if both key and value exist
                        case_data[case_number]["मुद्दाको विवरण"][key] = value
        except Exception as e:
            print(f"Error extracting मुद्दाको विवरण: {e}")

        # Extract "लगाब मुद्दाहरुको विवरण"
        try:
            rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'table-bordered')][1]/tbody/tr[td]")  # Assuming this is the first table for linked cases
            for row in rows[1:]:  # Skip the header row
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 6:
                    linked_case = {
                        "दर्ता नँ .": cols[0].text.strip(),
                        "दर्ता मिती": cols[1].text.strip(),
                        "मुद्दा": cols[2].text.strip(),
                        "वादीहरु": cols[3].text.strip(),
                        "प्रतिवादीहरु": cols[4].text.strip(),
                        "हालको स्थिती": cols[5].text.strip()
                    }
                    case_data[case_number]["लगाब मुद्दाहरुको विवरण"].append(linked_case)
        except Exception as e:
            print(f"Error extracting लगाब मुद्दाहरुको विवरण: {e}")

        # Extract "तारेख विवरण"
        try:
            rows = driver.find_elements(By.XPATH, "//tbody/tr[td[1][text()='तारेख मिती']]/following-sibling::tr[td]")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 3:
                    date_detail = {
                        "तारेख मिती": cols[0].text.strip(),
                        "विवरण": cols[1].text.strip() or "",
                        "तारेखको किसिम": cols[2].text.strip()
                    }
                    case_data[case_number]["तारेख विवरण"].append(date_detail)
        except Exception as e:
            print(f"Error extracting तारेख विवरण: {e}")

        try:
            rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'table-bordered')][2]/tbody/tr[td]")  # Assuming this is the second table
            for row in rows[1:]:  # Skip the header row
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 3:
                    status_detail = {
                        "मिती": cols[0].text.strip(),
                        "विवरण": cols[1].text.strip(),
                        "स्थिती": cols[2].text.strip()
                    }
                    case_data[case_number]["मुद्दाको स्थितीको बिस्तृत विवरण"].append(status_detail)
        except Exception as e:
            print(f"Error extracting मुद्दाको स्थितीको बिस्तृत विवरण: {e}")

        # Extract "पेशी को विवरण"
        try:
            rows = driver.find_elements(By.XPATH, "//tbody/tr[td[1][text()='सुनवाइ मिती']]/following-sibling::tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 4:
                    hearing_detail = {
                        "सुनवाइ मिती": cols[0].text.strip(),
                        "न्यायाधीशहरू": "\n".join([judge.strip() for judge in cols[1].text.strip().split("\n")]),
                        "मुद्दाको स्थिती": cols[2].text.strip(),
                        "आदेश /फैसलाको किसिम": cols[3].text.strip()
                    }
                    case_data[case_number]["पेशी को विवरण"].append(hearing_detail)
        except Exception as e:
            print(f"Error extracting पेशी को विवरण: {e}")

        # Print the corrected JSON format
        print(json.dumps(case_data, ensure_ascii=False, indent=4))

        # Save to JSON file
        with open(f"{case_number}_data.json", "w", encoding='utf-8') as json_file:
            json.dump(case_data, json_file, ensure_ascii=False, indent=4)

        # Close the driver
        driver.quit()
    else:
        print(f"Invalid case number: {case_number}")

if __name__ == "__main__":
    case_number = input("Enter the case number (e.g., 080-CR-0096): ")
    fetch_case_data(case_number)
