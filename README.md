# Daily USD Economic News Automation

**Production-ready Python automation** that runs every trading day via GitHub Actions.

Fetches today's USD economic news, analyzes it using **Sarvam AI**, and delivers a professional HTML email report **exactly 30 minutes before Nasdaq opens** (9:00 AM ET).

---

## Features

- ✅ Fetches **USD-only** economic events from Forex Factory
- ✅ Analyzes **every event** using **Sarvam AI** (no other LLMs)
- ✅ Generates detailed analysis per event:
  - Meaning, importance, Nasdaq impact, USD impact
  - Bullish / Bearish scenarios
  - Volatility expectation & Trading risk
- ✅ Generates **Overall Nasdaq Outlook**, **Highest-Risk Trading Window**, and **Key Takeaways**
- ✅ Sends beautiful, professional **HTML email** via Gmail SMTP
- ✅ Fully automated with **GitHub Actions** (cron + manual trigger)
- ✅ Proper error handling, logging, and secrets management
- ✅ No UI, no dashboard — pure backend automation

---

## Project Structure

```
econ_news_automation/
├── .github/
│   └── workflows/
│       └── daily-report.yml          # GitHub Actions workflow
├── src/
│   ├── config.py                     # Environment + secrets handling
│   ├── logger.py                     # Centralized logging
│   ├── news_fetcher.py               # Forex Factory scraper
│   ├── sarvam_client.py              # Sarvam AI integration
│   ├── email_generator.py            # HTML report generation
│   ├── email_sender.py               # Gmail SMTP delivery
│   └── main.py                       # Orchestration entrypoint
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup Instructions

### 1. Add GitHub Secrets

Go to your repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets:

| Secret Name         | Description                              | Example                     |
|---------------------|------------------------------------------|-----------------------------|
| `SARVAM_API_KEY`    | Your Sarvam AI API key                   | `sk-...`                    |
| `SMTP_EMAIL`        | Your Gmail address                       | `yourname@gmail.com`        |
| `SMTP_PASSWORD`     | Gmail App Password (NOT your normal password) | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL`   | Email address to receive the report      | `you@domain.com`            |
| `SMTP_HOST`         | (Optional) Default: `smtp.gmail.com`     | `smtp.gmail.com`            |
| `SMTP_PORT`         | (Optional) Default: `587`                | `587`                       |

> **Important**: For Gmail, you **must** use an [App Password](https://support.google.com/accounts/answer/185833). Enable 2FA first.

### 2. Fork / Clone the Repository

```bash
git clone <your-repo-url>
cd econ_news_automation
```

### 3. (Optional) Local Testing

```bash
cp .env.example .env
# Edit .env with your keys
pip install -r requirements.txt
cd src
python main.py
```

---

## How It Works

1. **GitHub Actions** triggers at **13:00 UTC** (9:00 AM ET during daylight saving).
2. `main.py` runs:
   - Fetches USD events from Forex Factory
   - Sends each event to **Sarvam AI** for structured analysis
   - Generates overall outlook
   - Creates professional HTML report
   - Sends via Gmail SMTP
3. You receive the email **exactly 30 minutes before market open**.

---

## Cron Schedule

The workflow runs at:
- **13:00 UTC** (Monday–Friday)

This corresponds to:
- **9:00 AM ET** during Daylight Saving Time (EDT)
- **8:00 AM ET** during Standard Time (EST)

> **Note**: You may need to manually update the cron schedule once per year when DST changes.

---

## Customization

- **Change model**: Edit `SARVAM_MODEL` in `src/config.py`
- **Change schedule**: Edit `.github/workflows/daily-report.yml`
- **Add more currencies**: Extend `news_fetcher.py`
- **Change email design**: Modify `email_generator.py`

---

## Error Handling & Logging

- All API failures, network issues, and SMTP errors are caught and logged.
- Failed runs will appear in GitHub Actions with full logs.
- The script exits with code 1 on critical failures.

---

## Security

- **Zero hardcoded credentials**
- All secrets stored in **GitHub Secrets**
- Uses environment variables exclusively

---

## Deliverables

- `main.py` — Full automation
- `requirements.txt` — All dependencies
- GitHub Actions workflow
- `.env.example`
- Professional HTML email template
- Complete modular source code

---

## License

MIT — Free to use and modify.

---

**Ready to use.** Add your secrets and the automation will start sending daily reports automatically.