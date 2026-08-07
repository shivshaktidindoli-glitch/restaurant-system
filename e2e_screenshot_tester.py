import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACT_DIR = r"C:\Users\RAJ YAGNIK\.gemini\antigravity\brain\ee8e896c-a607-41ef-9c38-9f123adcf922"
BASE_URL = "http://127.0.0.1:5000"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def run_tests():
    print("Starting Playwright E2E Verification...")
    
    with sync_playwright() as p:
        browser_exec = CHROME_PATH if os.path.exists(CHROME_PATH) else EDGE_PATH
        browser = p.chromium.launch(executable_path=browser_exec, headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 820})
        page = context.new_page()

        # Step 1: Admin Login
        print("1. Admin Login...")
        page.goto(f"{BASE_URL}/admin/login", wait_until="networkidle")
        page.fill("input[name='mobile']", "7999620244")
        page.fill("input[name='password']", "soulsip@2000")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Step 2: Tables Page - QR Code Modal
        print("2. Tables QR Code Modal...")
        page.goto(f"{BASE_URL}/admin/tables", wait_until="networkidle")
        time.sleep(1)
        qr_btn = page.locator("button:has-text('QR Code'), button:has-text('QR')").first
        if qr_btn.is_visible():
            qr_btn.click()
            time.sleep(1.2)
            qr_modal_path = os.path.join(ARTIFACT_DIR, "table_qr_modal.png")
            page.screenshot(path=qr_modal_path)
            print(f"Saved: {qr_modal_path}")
            close_btn = page.locator("#qrModal button:has-text('×'), #qrModal button.btn-primary:has-text('Close')").first
            if close_btn.is_visible():
                close_btn.click()
                time.sleep(0.5)

        # Step 3: Live Tables Page - QR Code Modal
        print("3. Live Tables QR Code Modal...")
        page.goto(f"{BASE_URL}/admin/live_tables", wait_until="networkidle")
        time.sleep(1)
        live_qr_btn = page.locator("button:has-text('QR Code')").first
        if live_qr_btn.is_visible():
            live_qr_btn.click()
            time.sleep(1.2)
            live_qr_modal_path = os.path.join(ARTIFACT_DIR, "live_tables_qr_modal.png")
            page.screenshot(path=live_qr_modal_path)
            print(f"Saved: {live_qr_modal_path}")
            close_live_qr = page.locator("#liveTableQRModal button:has-text('×')").first
            if close_live_qr.is_visible():
                close_live_qr.click()
                time.sleep(0.5)

        # Step 4: Customer Menu & Place Order (Mobile View)
        print("4. Customer Menu & Order Placement...")
        cust_context = browser.new_context(viewport={'width': 420, 'height': 880})
        cust_page = cust_context.new_page()
        cust_page.goto(f"{BASE_URL}/menu?table=T-1", wait_until="networkidle")
        time.sleep(1.5)
        
        # Add item to cart
        add_btn = cust_page.locator(".btn-add").first
        if add_btn.is_visible():
            add_btn.click()
            time.sleep(0.6)
            plus_btn = cust_page.locator(".stepper.active button:has-text('+')").first
            if plus_btn.is_visible():
                plus_btn.click()
                time.sleep(0.6)
                
            menu_cart_path = os.path.join(ARTIFACT_DIR, "customer_menu_order.png")
            cust_page.screenshot(path=menu_cart_path)
            print(f"Saved: {menu_cart_path}")
            
            # Review & Pay
            cust_page.evaluate("openCheckout()")
            time.sleep(1.0)
            checkout_modal_path = os.path.join(ARTIFACT_DIR, "customer_checkout_modal.png")
            cust_page.screenshot(path=checkout_modal_path)
            print(f"Saved: {checkout_modal_path}")
            
            cust_page.locator("#cust-name").fill("Raj Yagnik")
            cust_page.locator("#cust-mobile").fill("7999620244")
            time.sleep(0.5)
            
            place_order_btn = cust_page.locator("#checkout-modal button:has-text('Place Order')").first
            if place_order_btn.is_visible():
                place_order_btn.click()
                cust_page.wait_for_load_state("networkidle")
                time.sleep(3.0)
                order_success_path = os.path.join(ARTIFACT_DIR, "customer_order_success.png")
                cust_page.screenshot(path=order_success_path)
                print(f"Saved: {order_success_path}")

        # Step 5: Inventory Management & Stock Adjustment
        print("5. Inventory Management & Stock Adjustment...")
        page.goto(f"{BASE_URL}/admin/inventory", wait_until="networkidle")
        time.sleep(1.5)
        inv_page_path = os.path.join(ARTIFACT_DIR, "inventory_page_stock.png")
        page.screenshot(path=inv_page_path)
        print(f"Saved: {inv_page_path}")
        
        # Click Adjust button
        adjust_btn = page.locator("button:has-text('Adjust')").first
        if adjust_btn.is_visible():
            adjust_btn.click()
            time.sleep(1.0)
            inv_adjust_modal_path = os.path.join(ARTIFACT_DIR, "inventory_adjust_modal.png")
            page.screenshot(path=inv_adjust_modal_path)
            print(f"Saved: {inv_adjust_modal_path}")
            
            # Fill form and submit
            page.evaluate("""() => {
                document.querySelector('#entryModal input[name="quantity"]').value = '15';
                document.querySelector('#entryModal input[name="reason"]').value = 'Fresh Restock from Supplier';
                document.querySelector('#entryModal form').submit();
            }""")
            page.wait_for_load_state("networkidle")
            time.sleep(2.0)
            
            inv_after_path = os.path.join(ARTIFACT_DIR, "inventory_after_restock.png")
            page.screenshot(path=inv_after_path)
            print(f"Saved: {inv_after_path}")

        browser.close()
        print("ALL E2E UI TESTS AND SCREENSHOTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
