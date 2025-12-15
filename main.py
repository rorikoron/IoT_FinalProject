import time
import cv2
import numpy as np
import base64
import re
import requests
import threading
import os
from dotenv import load_dotenv
from supabase import create_client
from picamera2 import Picamera2

# =====================
# 環境変数
# =====================
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# =====================
# Supabase
# =====================
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =====================
# Camera
# =====================
camera = Picamera2()
camera.configure(camera.create_still_configuration(
    main={"size": (640, 480)}
))
camera.start()

# =====================
# Constants
# =====================
CAPTURE_INTERVAL = 10      # 秒
FETCH_INTERVAL = 30        # 秒
DIFF_THRESHOLD = 500000    # 動体検知閾値

PREV_IMG = "prev.jpg"
CURR_IMG = "current.jpg"

# =====================
# Camera Capture
# =====================
def capture_image(path):
    camera.capture_file(path)

# =====================
# Frame Differencing
# =====================
def has_significant_change(prev_path, curr_path):
    prev = cv2.imread(prev_path, cv2.IMREAD_GRAYSCALE)
    curr = cv2.imread(curr_path, cv2.IMREAD_GRAYSCALE)

    # ノイズ対策
    prev = cv2.GaussianBlur(prev, (5, 5), 0)
    curr = cv2.GaussianBlur(curr, (5, 5), 0)

    diff = cv2.absdiff(prev, curr)
    score = np.sum(diff)

    print(f"[DIFF] score={score}")
    return score > DIFF_THRESHOLD

# =====================
# Gemini OCR
# =====================
def send_to_gemini(image_path):
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()

    payload = {
        "contents": [{
            "parts": [
                {"text": "添付ファイルのレシートをOCRして"},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_base64
                    }
                }
            ]
        }]
    }

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-pro-vision:generateContent?key={GEMINI_API_KEY}"
    )

    res = requests.post(url, json=payload, timeout=30)
    res.raise_for_status()

    return res.json()

# =====================
# Code Extraction
# =====================
def extract_code(text):
    match = re.search(r"[A-Z]{2}-[0-9]{8}", text)
    return match.group(0) if match else None

# =====================
# Supabase Insert
# =====================
def save_to_supabase(code):
    print(f"[SAVE] {code}")
    supabase.table("receipts").insert({
        "code": code
    }).execute()

# =====================
# Supabase Fetch Loop
# =====================
def supabase_polling():
    while True:
        try:
            res = supabase.table("receipts").select("code").execute()
            codes = [r["code"] for r in res.data]
            print("[SUPABASE] stored codes:", codes)
        except Exception as e:
            print("[SUPABASE ERROR]", e)

        time.sleep(FETCH_INTERVAL)

# =====================
# Main Loop
# =====================
def main_loop():
    # 初回撮影
    capture_image(PREV_IMG)
    time.sleep(CAPTURE_INTERVAL)

    while True:
        capture_image(CURR_IMG)

        if has_significant_change(PREV_IMG, CURR_IMG):
            try:
                result = send_to_gemini(CURR_IMG)

                text = result["candidates"][0]["content"]["parts"][0]["text"]
                print("[GEMINI OCR]", text)

                code = extract_code(text)
                if code:
                    save_to_supabase(code)

            except Exception as e:
                print("[GEMINI ERROR]", e)

        # 次回用に保存
        os.replace(CURR_IMG, PREV_IMG)
        time.sleep(CAPTURE_INTERVAL)

if __name__ == "__main__":

    main_loop()
