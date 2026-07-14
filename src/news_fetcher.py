import requests
from datetime import datetime
import pytz
from typing import List, Dict, Optional
from logger import logger
from config import config


class NewsFetcher:
    """
    Fetches today's USD economic events using ForexFactory's public JSON
    calendar feed. This replaces the old HTML-scraping approach, which
    broke because forexfactory.com serves its calendar via JavaScript
    behind Cloudflare — a plain `requests` GET never sees the actual
    event rows, so every run silently fell back to "no events".

    The feed below is the same data ForexFactory's own calendar widget
    uses, published as static JSON (no auth, no JS rendering needed):
    https://nfs.faireconomy.media/ff_calendar_thisweek.json
    """

    FEED_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        })
        self.ny_tz = pytz.timezone("America/New_York")

    def is_trading_day(self, date: datetime) -> bool:
        """Check if it's a weekday (basic trading day check)."""
        if date.weekday() >= 5:
            return False
        holidays = [
            (1, 1),   # New Year's Day
            (7, 4),   # Independence Day
            (12, 25), # Christmas
            (11, 11), # Veterans Day (approx)
        ]
        if (date.month, date.day) in holidays:
            return False
        return True

    def get_today_date_ny(self) -> datetime:
        """Get current date in New York timezone."""
        return datetime.now(self.ny_tz)

    def _parse_event_time(self, raw_date: str) -> Optional[datetime]:
        """Parse the feed's ISO8601 date string into a NY-aware datetime."""
        if not raw_date:
            return None
        try:
            dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            return dt.astimezone(self.ny_tz)
        except (ValueError, TypeError):
            return None

    def fetch_forex_factory_calendar(self, target_date: Optional[datetime] = None) -> List[Dict]:
        """
        Pull this week's calendar from the JSON feed and filter down to
        today's USD medium/high impact events.
        Returns list of dicts with keys: time, currency, impact, event, actual, forecast, previous
        """
        if target_date is None:
            target_date = self.get_today_date_ny()

        if not self.is_trading_day(target_date):
            logger.info("Not a trading day. Skipping news fetch.")
            return []

        logger.info(f"Fetching economic calendar feed for {target_date.strftime('%Y-%m-%d')}")

        try:
            response = self.session.get(self.FEED_URL, timeout=20)
            response.raise_for_status()
            raw_events = response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch calendar feed: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Failed to parse calendar feed JSON: {str(e)}")
            raise

        logger.info(f"Fetched {len(raw_events)} total events from feed")

        target_date_str = target_date.strftime("%Y-%m-%d")
        events = []

        for item in raw_events:
            try:
                currency = (item.get("country") or "").upper()
                if currency != "USD":
                    continue

                event_dt = self._parse_event_time(item.get("date"))
                if event_dt is None or event_dt.strftime("%Y-%m-%d") != target_date_str:
                    continue

                impact = (item.get("impact") or "").strip().lower()
                if impact not in ("high", "medium"):
                    continue

                events.append({
                    "time": event_dt.strftime("%I:%M %p").lstrip("0") or "N/A",
                    "currency": currency,
                    "impact": impact,
                    "event": item.get("title", "Unknown Event"),
                    "actual": item.get("actual") or None,
                    "forecast": item.get("forecast") or None,
                    "previous": item.get("previous") or None,
                    "date": target_date_str,
                })
            except Exception as e:
                logger.warning(f"Error parsing feed item: {str(e)}")
                continue

        # Sort chronologically
        events.sort(key=lambda e: e["time"])

        logger.info(f"Found {len(events)} USD high/medium impact events for {target_date_str}")
        return events

    def get_usd_events_today(self) -> List[Dict]:
        """Main entry point: fetch today's USD events."""
        try:
            events = self.fetch_forex_factory_calendar()
            return events
        except Exception as e:
            logger.error(f"Error fetching USD events: {str(e)}")
            return []
