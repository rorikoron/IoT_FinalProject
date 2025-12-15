import os
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client
from send_mail import send_email

# =====================
# ENV
# =====================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

INVOICE_URL = "https://invos.com.tw/invoice-list"

# =====================
# Fetch winning numbers
# =====================
def fetch_winning_numbers():
    res = requests.get(INVOICE_URL, timeout=20)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text()

    # 8桁数字をすべて抽出
    numbers = re.findall(r"\b\d{8}\b", text)

    # 重複排除
    unique_numbers = list(set(numbers))

    print(f"[INFO] Winning numbers: {unique_numbers}")
    return unique_numbers

# =====================
# Fetch receipts
# =====================
def fetch_receipts():
    res = supabase.table("receipts").select("*").execute()
    return res.data

# =====================
# Matching
# =====================
def match_receipts(winning_numbers, receipts):
    matched = []

    for r in receipts:
        # AA-12345678 → 12345678
        receipt_num = r["code"].split("-")[-1]

        if receipt_num in winning_numbers:
            matched.append({
                "code": r["code"],
                "image_path": r["image_path"]
            })

    return matched

# =====================
# Output matched images
# =====================
def output_results(matches):
    if not matches:
        print("❌ No winning receipts")
        return

    print("🎉 WINNING RECEIPTS FOUND 🎉")
    send_email(f"{m['code']} is a winning receipt!");


# =====================
# Main
# =====================
def main():
    print("=== Invoice Check Start ===")

    winning_numbers = fetch_winning_numbers()
    receipts = fetch_receipts()
    matches = match_receipts(winning_numbers, receipts)

    output_results(matches)

    print("=== Done ===")

if __name__ == "__main__":
    main()
