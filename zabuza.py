import helium
import creds as creds
from helium import Text, Button, S
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome

def is_logged_in():
    """
    Check if the user is logged in by verifying the presence of the username and the "SAIR" button.
    Returns True if logged in, False otherwise.
    """
    try:
        return Text("258866909677").exists() and Button("SAIR").exists()
    except Exception:
        return False

def navigate_to_aviator():
    """
    Navigate to the 'Aviator' page if the user is logged in.
    """
    if is_logged_in():
        try:
            helium.click("Aviator")
            print("Navigated to Aviator successfully.")
            return True
        except Exception as e:
            print(f"Failed to navigate to Aviator: {e}")
            return False
    else:
        print("User is not logged in. Cannot navigate to Aviator.")
        return False

def capture_dropdown_content(duration=60):
    """
    Capture content from the dropdown within the 'game_loader' iframe for a specified duration (in seconds).
    Looks for text ending with 'x' and appends it to 'outcomes.txt'.
    """
    start_time = time.time()
    seen_outcomes = set()  # To avoid duplicates in this session

    # Get the Selenium WebDriver instance from Helium
    driver = helium.get_driver()

    # Find and switch to the 'game_loader' iframe
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "game_loader")))
        iframe_element = driver.find_element(By.ID, "game_loader")
        print(f"Found iframe element: {iframe_element}")
        driver.switch_to.frame(iframe_element)
        print("Switched to 'game_loader' iframe.")
    except Exception as e:
        print(f"Failed to switch to 'game_loader' iframe: {e}")
        return

    # Click the dropdown-toggle button within the iframe
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "dropdown-toggle.button")))
        dropdown_button = driver.find_element(By.CLASS_NAME, "dropdown-toggle.button")
        print(f"Found dropdown button: {dropdown_button}")
        dropdown_button.click()
        print("Dropdown opened successfully.")
    except Exception as e:
        print(f"Failed to open dropdown: {e}")
        driver.switch_to.default_content()
        return

    while time.time() - start_time < duration:
        try:
            # Wait for and re-locate text elements on each iteration
            WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//*[contains(text(), 'x') and not(contains(text(), 'Histórico'))]")))
            all_text = helium.find_all(Text())
            current_outcomes = [t.value.strip() for t in all_text if t.value.strip().endswith('x')]

            # Identify new outcomes
            new_outcomes = [outcome for outcome in current_outcomes if outcome not in seen_outcomes]

            # If there are new outcomes, append them to the file
            if new_outcomes:
                with open("outcomes.txt", "a", encoding="utf-8") as f:
                    for outcome in new_outcomes:
                        f.write(f"{outcome} - {time.ctime()}\n")
                print(f"Captured new outcomes: {new_outcomes}")

            # Update seen_outcomes
            seen_outcomes.update(new_outcomes)

            # Wait 1 second before the next check
            time.sleep(1)

        except Exception as e:
            print(f"Error capturing outcomes: {e}")
            time.sleep(1)  # Wait before retrying and continue to next iteration

    # Switch back to default content when done
    driver.switch_to.default_content()

def main(headless=False):
    # Start the browser and navigate to the website
    helium.start_chrome('https://elephantbet.co.mz', headless=headless)

    try:
        # Wait for the popup and decline notifications
        helium.wait_until(
            lambda: Text("Gostaria de receber notificações de promoções e ofertas?").exists()
            and Button("Não").exists(),
            timeout_secs=15
        )
        helium.click(Button("Não"))

        # Log in using credentials
        helium.write(creds.username, into="Telefone")
        helium.write(creds.password, into="Senha")
        helium.click("Conecte-se")

        # Wait for login to complete
        helium.wait_until(is_logged_in, timeout_secs=10)

        # Navigate to Aviator and capture dropdown content
        if navigate_to_aviator():
            print("Starting outcome capture for 60 seconds...")
            capture_dropdown_content(duration=60)

        # Wait for user input before closing (if not headless)
        if not headless:
            input("Press Enter to close the browser...")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        helium.kill_browser()

def kill_browser():
    """
    Kill the Chrome browser process.
    """
    try:
        os.system("pkill -f chrome")
    except Exception as e:
        print(f"Error killing Chrome process: {e}")

if __name__ == "__main__":
    main(headless=False)  # Set to True to run in background
