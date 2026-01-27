from playwright.sync_api import sync_playwright
import pytest

# Note: To run this test, you need to have your Flask app running!
# You can run it in a separate terminal with `python app.py`

@pytest.mark.skip(reason="Requires the Flask server to be running manually")
def test_travel_app_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("http://127.0.0.1:5000/")
        assert "Travel Assistant" in page.title()
        
        page.fill("input[name='user_input']", "London")
        page.click("button[type='submit']")
        
        # We look for the "Travel Buddy" text which appears in the response block
        page.wait_for_selector(".response", timeout=10000)
        
        content = page.content()
        assert "Travel Buddy" in content
        
        browser.close()
