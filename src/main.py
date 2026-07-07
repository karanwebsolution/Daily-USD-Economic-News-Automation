#!/usr/bin/env python3
"""
Daily USD Economic News Automation
Runs 30 minutes before Nasdaq open (8:30 AM ET)
"""

import sys
import os
from datetime import datetime
import pytz
from typing import List, Dict

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from logger import logger
from news_fetcher import NewsFetcher
from sarvam_client import SarvamClient
from email_generator import EmailGenerator
from email_sender import EmailSender


def is_trading_day_ny() -> bool:
    """Check if today is a trading day in NY timezone."""
    ny_tz = pytz.timezone("America/New_York")
    now = datetime.now(ny_tz)
    # Weekday check
    if now.weekday() >= 5:
        return False
    # Simple holiday check
    holidays = [(1, 1), (7, 4), (11, 11), (12, 25)]
    if (now.month, now.day) in holidays:
        return False
    return True


def run_daily_report():
    """Main entry point for the automation."""
    logger.info("=" * 60)
    logger.info("Starting Daily USD Economic News Report Automation")
    logger.info("=" * 60)

    # Validate configuration
    try:
        config.validate()
        logger.info("Configuration validated successfully.")
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    # Check if trading day
    if not is_trading_day_ny():
        logger.info("Today is not a trading day. Exiting gracefully.")
        return

    # Initialize components
    news_fetcher = NewsFetcher()
    sarvam_client = SarvamClient()
    email_generator = EmailGenerator()
    email_sender = EmailSender()

    date_str = datetime.now(pytz.timezone("America/New_York")).strftime("%Y-%m-%d")
    logger.info(f"Processing date: {date_str}")

    # Step 1: Fetch news
    logger.info("Step 1: Fetching today's USD economic news...")
    try:
        usd_events = news_fetcher.get_usd_events_today()
        if not usd_events:
            logger.warning("No USD events found for today.")
    except Exception as e:
        logger.error(f"News fetch failed: {str(e)}")
        usd_events = []

    if not usd_events:
        # Send a "no events" email
        html_report = email_generator.generate_html_report([], 
            "**No significant USD economic events** are scheduled for today.", date_str)
        subject = f"Daily USD Economic News Report - {date_str} (No Events)"
        email_sender.send_report(html_report, subject)
        logger.info("No-events report sent.")
        return

    # Step 2: Analyze each event with Sarvam AI
    logger.info(f"Step 2: Analyzing {len(usd_events)} events with Sarvam AI...")
    analyzed_events = []
    for i, event in enumerate(usd_events, 1):
        logger.info(f"  Analyzing event {i}/{len(usd_events)}: {event.get('event')}")
        try:
            analyzed = sarvam_client.analyze_event(event)
            analyzed_events.append(analyzed)
        except Exception as e:
            logger.error(f"Analysis failed for {event.get('event')}: {str(e)}")
            analyzed_events.append({
                "event": event,
                "analysis": f"**Analysis unavailable** due to API error: {str(e)}"
            })

    # Step 3: Generate overall outlook
    logger.info("Step 3: Generating overall Nasdaq outlook...")
    try:
        overall_outlook = sarvam_client.generate_overall_outlook(analyzed_events, date_str)
    except Exception as e:
        logger.error(f"Outlook generation failed: {str(e)}")
        overall_outlook = "**Outlook generation failed.** Please review individual events."

    # Step 4: Generate HTML email
    logger.info("Step 4: Generating HTML email report...")
    html_report = email_generator.generate_html_report(analyzed_events, overall_outlook, date_str)

    # Step 5: Send email
    subject = f"Daily USD Economic News Report - {date_str}"
    logger.info("Step 5: Sending email report via Gmail SMTP...")
    
    success = email_sender.send_report(html_report, subject)
    
    if success:
        logger.info("✅ Daily report completed and delivered successfully!")
    else:
        logger.error("❌ Failed to send email report.")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("Automation run completed.")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        run_daily_report()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user.")
    except Exception as e:
        logger.exception(f"Critical error in automation: {str(e)}")
        sys.exit(1)