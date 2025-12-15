# Auto-winning Machine

此專案乃使用樹梅派自動兌獎發票的機器。
專案由樹梅派、Supabase 組成。處裡分為兩階段。
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
[Winning Receipt Image Output]
```

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

## Cron Check

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
