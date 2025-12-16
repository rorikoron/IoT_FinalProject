# Auto-winning Machine

此專案乃使用樹梅派自動兌獎發票的機器。
專案由樹梅派、Supabase 組成。處裡分為兩階段。
<img width="2200" height="1800" alt="image" src="https://github.com/user-attachments/assets/78b8db07-3452-4fc2-85d0-ac10a4601326" />

一: 每隔十秒取得相機的影像，傳至 LLM 做 OCR 後存在 Supabase
二: 在本機使用 cron 每天取得正確的中獎號碼，與 Supabase 中的所有儲存的號碼。

## System Architecture

```text
[Camera]
   ↓ (10s)
[Raspberry Pi]
   ↓ Frame Differencing
[LLM OCR (Gemini)]
   ↓ code extraction
[Supabase Database]
   ↑ (daily cron)
[Invoice Checker]
   ↓
[Winning Receipt Email sending]
```

### Step 1. Camera

使用 gpiozero 程式控制外接相機，每隔十秒拍照。
此部分使用 picamera2

### Step 2. Frame Differencing

為了不要浪費 API token，使用 openCV 去觀察兩圖片的差異。如果差異太小就不要執行後面處裡。
此部分重複利用我以前寫的程式。

### Step 3. LLM OCR

這次使用 Gemini 去做 OCR。原因可分為 1.想測試看看相較於傳統 OCR 技術的優劣，探索 LLMOCR 的可能性。 2.這次準確率不是 Critical(兌獎是每一天執行)
這兩項，於是使用 AI~~偷懶~~有效率開發。

### Step 4. 上傳到資料庫

要件為 1.可以輕易上下傳資料(RESTful 為佳)
2.RDBMS 3.有 Python SDK(Library)
所以使用 Supabase(上次黑客松使用感不錯)

### Step 5. 中獎確認

由於政府沒有提供 API 取得當月中獎號碼，使用 beautiful soup 爬蟲取得月份與中獎號碼。
上述程式使用 linux 的 cronjob 每一天執行並從 Supabase 取得所有資料對號碼。

### Step 6. Email 傳送

當有中獎時使用 SMTP 傳送 email 到信箱，提醒使用者記得保留及兌獎。
此部分重複利用我以前寫的程式。
![20251215_233949](https://github.com/user-attachments/assets/03fc5a60-2023-4b57-a214-4d48ca504aaa)
![20251215_233953](https://github.com/user-attachments/assets/77bf3373-13c1-4766-9998-04bafec924b9)

## Getting Started

1. OS setup

```bash
sudo apt update
sudo apt install python3-pip
pip3 install python-dotenv opencv-python numpy requests supabase picamera2
```

2. Execute Python

```bash
python3 ./main.py
```

## Cron Setup

1. OS setup

```bash
pip3 install requests beautifulsoup4 python-dotenv supabase
```

2. Setting Cronjob

```bash
crontab -e
0 3 1 * * /usr/bin/python3 /home/pi/fetch_invoice.py >> /home/pi/invoice.log 2>&1
```

## Reference

-   https://github.com/rorikoron/MotionDetector
    兩年前寫的 python 檔。重複使用 frame-differencing 與 SMTP。

-   https://youtube.com/shorts/ObwLXx1vHIU?si=L_37tWWQwgeqb1Vg
    Youtube 介紹影片
