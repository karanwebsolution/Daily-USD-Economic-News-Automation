import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Optional
from logger import logger
from config import config

class NewsFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        self.ny_tz = pytz.timezone("America/New_York")

    def is_trading_day(self, date: datetime) -> bool:
        """Check if it's a weekday (basic trading day check)."""
        # Monday=0 ... Friday=4
        if date.weekday() >= 5:
            return False
        # Basic US holiday skip (can be expanded)
        holidays = [
            (1, 1),   # New Year's Day
            (7, 4),   # Independence Day
            (12, 25), # Christmas
            (11, 11), # Veterans Day (approx)
        ]
        month_day = (date.month, date.day)
        if month_day in holidays:
            return False
        return True

    def get_today_date_ny(self) -> datetime:
        """Get current date in New York timezone."""
        return datetime.now(self.ny_tz)

    def fetch_forex_factory_calendar(self, target_date: Optional[datetime] = None) -> List[Dict]:
        """
        Scrape Forex Factory calendar for today's USD events.
        Returns list of dicts with keys: time, currency, impact, event, actual, forecast, previous
        """
        if target_date is None:
            target_date = self.get_today_date_ny()

        if not self.is_trading_day(target_date):
            logger.info("Not a trading day. Skipping news fetch.")
            return []

        # ForexFactory uses date format YYYY-MM-DD in URL
        date_str = target_date.strftime("%Y-%m-%d")
        url = f"https://www.forexfactory.com/calendar?day={date_str}"

        logger.info(f"Fetching economic calendar from ForexFactory for {date_str}")

        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch calendar: {str(e)}")
            raise

        soup = BeautifulSoup(response.content, "html.parser")
        events = []

        # ForexFactory table structure: rows with class 'calendar_row'
        rows = soup.find_all("tr", class_="calendar_row")

        for row in rows:
            try:
                # Currency
                currency_cell = row.find("td", class_="currency")
                if not currency_cell:
                    continue
                currency = currency_cell.get_text(strip=True).upper()

                if currency != "USD":
                    continue

                # Time
                time_cell = row.find("td", class_="time")
                time_str = time_cell.get_text(strip=True) if time_cell else "N/A"

                # Impact
                impact_cell = row.find("td", class_="impact")
                impact = "low"
                if impact_cell:
                    impact_span = impact_cell.find("span")
                    if impact_span:
                        impact_class = impact_span.get("class", [])
                        if any("red" in c.lower() for c in impact_class):
                            impact = "high"
                        elif any("orange" in c.lower() for c in impact_class):
                            impact = "medium"

                # Event name
                event_cell = row.find("td", class_="event")
                event_name = event_cell.get_text(strip=True) if event_cell else "Unknown Event"

                # Actual / Forecast / Previous
                actual_cell = row.find("td", class_="actual")
                forecast_cell = row.find("td", class_="forecast")
                previous_cell = row.find("td", class_="previous")

                actual = actual_cell.get_text(strip=True) if actual_cell else ""
                forecast = forecast_cell.get_text(strip=True) if forecast_cell else ""
                previous = previous_cell.get_text(strip=True) if previous_cell else ""

                # Skip low impact unless high/medium
                if impact == "low":
                    continue

                events.append({
                    "time": time_str,
                    "currency": currency,
                    "impact": impact,
                    "event": event_name,
                    "actual": actual or None,
                    "forecast": forecast or None,
                    "previous": previous or None,
                    "date": date_str,
                })

            except Exception as e:
                logger.warning(f"Error parsing row: {str(e)}")
                continue

        logger.info(f"Fetched {len(events)} USD events for {date_str}")
        return events

    def get_usd_events_today(self) -> List[Dict]:
        """Main entry point: fetch today's USD events."""
        try:
            events = self.fetch_forex_factory_calendar()
            return events
        except Exception as e:
            logger.error(f"Error fetching USD events: {str(e)}")
            return []