"""Automated Backend Test Suite for Kalakriti API."""

import sys
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api/v1"
DEV_PHONE = "+919999999999"
DEV_OTP = "123456"

# Terminal formatting
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def log_test(name: str, passed: bool, details: str = ""):
    status_str = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
    print(f"{status_str} {name}")
    if details and not passed:
        print(f"      {RED}Details: {details}{RESET}")


def run_tests():
    print(f"\n{BLUE}=== Starting Kalakriti Backend Test Suite ==={RESET}\n")

    with httpx.Client(timeout=10.0) as client:
        # 1. Health check
        try:
            res = client.get("http://127.0.0.1:8000/health")
            log_test("Health Check", res.status_code == 200, res.text)
        except Exception as e:
            log_test("Health Check (Is server running?)", False, str(e))
            sys.exit(1)

        # 2. Auth: Send OTP (Dev Bypass)
        res = client.post(f"{BASE_URL}/auth/send-otp", json={"phone_number": DEV_PHONE})
        log_test("Auth - Send OTP", res.status_code == 200, res.text)

        # 3. Auth: Verify OTP
        res = client.post(f"{BASE_URL}/auth/verify-otp", json={"phone_number": DEV_PHONE, "otp": DEV_OTP})
        auth_passed = res.status_code == 200 and "access_token" in res.json()
        log_test("Auth - Verify OTP & Get JWT", auth_passed, res.text)

        if not auth_passed:
            print(f"\n{RED}Cannot proceed with authenticated tests without a valid token.{RESET}")
            sys.exit(1)

        auth_data = res.json()
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. Auth: Get Current Profile
        res = client.get(f"{BASE_URL}/auth/me", headers=headers)
        log_test("Auth - Fetch Current Artisan Profile (/auth/me)", res.status_code == 200, res.text)

        # 5. Pricing: ML Estimation
        pricing_payload = {
            "craft_type": "pottery",
            "material": "clay",
            "length_cm": 20.0,
            "width_cm": 15.0,
            "height_cm": 10.0,
            "weight_g": 600.0,
        }
        res = client.post(f"{BASE_URL}/pricing/estimate", json=pricing_payload, headers=headers)
        pricing_passed = res.status_code == 200 and "suggested_price" in res.json()
        log_test("Pricing - ML Dynamic Estimation", pricing_passed, res.text)
        if pricing_passed:
            p_data = res.json()
            print(f"      Suggested: INR {p_data['suggested_price']} (Range: {p_data['price_min']} - {p_data['price_max']})")

        # 6. Products: Create Product Listing
        product_payload = {
            "title_en": "Handcrafted Terracotta Diya",
            "title_hi": "मिट्टी का दीया",
            "description_en": "Traditional handcrafted clay lamp made with natural terracotta clay.",
            "description_hi": "हाथ से बना हुआ पारम्परिक दीया",
            "craft_type": "pottery",
            "material": "clay",
            "suggested_price": 250.0,
            "final_price": 250.0,
            "length_cm": 10.0,
            "width_cm": 10.0,
            "height_cm": 5.0,
            "weight_grams": 200,
            "image_urls": ["https://example.com/diya.jpg"],
            "gi_tag_name": "Khurja Pottery",
            "is_gi_certified": True,
            "artisan_story": "Crafted using 3rd generation wheel throwing techniques.",
        }
        res = client.post(f"{BASE_URL}/products", json=product_payload, headers=headers)
        product_created = res.status_code == 201
        log_test("Products - Create New Product", product_created, res.text)

        product_id = None
        if product_created:
            product_id = res.json()["id"]

        # 7. Products: List Products
        res = client.get(f"{BASE_URL}/products?page=1&limit=10", headers=headers)
        log_test("Products - List Artisan Products", res.status_code == 200 and res.json()["total"] >= 1, res.text)

        # 8. ONDC: Publish Item
        if product_id:
            res = client.post(f"{BASE_URL}/ondc/publish/{product_id}", headers=headers)
            log_test("ONDC - Publish Item to Beckn Network", res.status_code == 200, res.text)

            # 9. QR Phygital Bridge: Public scan resolution
            res = client.get(f"{BASE_URL}/qr/product/{product_id}")
            log_test("QR Bridge - Public Scan Artisan Story Resolver", res.status_code == 200, res.text)

            # 10. QR Phygital Bridge: Get print link
            res = client.get(f"{BASE_URL}/qr/product/{product_id}/link", headers=headers)
            log_test("QR Bridge - Generate QR Metadata Link", res.status_code == 200, res.text)

        # 11. B2B Inquiries: Public submission
        if product_id:
            b2b_payload = {
                "product_id": product_id,
                "buyer_name": "Priya Sharma",
                "buyer_organization": "Taj Hotels Procurement",
                "buyer_email": "procurement@tajhotels.com",
                "buyer_phone": "+919876543210",
                "craft_type": "Blue Pottery",
                "quantity": 500,
                "target_budget_inr": 250000.0,
                "requirements_description": "Need 500 ceramic dinner plates for new resort opening by Dec 2025.",
            }
            res = client.post(f"{BASE_URL}/b2b/inquiries", json=b2b_payload)
            log_test("B2B - Public Bulk Inquiry Submission", res.status_code == 201, res.text)

            # 12. B2B Inquiries: Artisan fetch incoming inquiries
            res = client.get(f"{BASE_URL}/b2b/inquiries", headers=headers)
            log_test("B2B - Artisan Fetch Inquiries", res.status_code == 200 and res.json()["total"] >= 1, res.text)

    print(f"\n{BLUE}=== Test Suite Complete ==={RESET}\n")


if __name__ == "__main__":
    run_tests()