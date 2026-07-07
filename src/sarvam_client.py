import requests
import json
from typing import List, Dict, Any, Optional
from logger import logger
from config import config

class SarvamClient:
    def __init__(self):
        if not config.SARVAM_API_KEY:
            raise ValueError("SARVAM_API_KEY is required")
        
        self.api_key = config.SARVAM_API_KEY
        self.base_url = config.SARVAM_BASE_URL.rstrip("/")
        self.model = config.SARVAM_MODEL
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "api-subscription-key": self.api_key
        })

    def _call_chat_completions(self, messages: List[Dict[str, str]], max_tokens: int = 4096, temperature: float = 0.3) -> str:
        """Call Sarvam AI chat completions API."""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "reasoning_effort": "medium"  # Enable thinking for better analysis
        }

        try:
            logger.info(f"Calling Sarvam AI ({self.model})...")
            response = self.session.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            
            if "choices" not in data or not data["choices"]:
                raise ValueError("No choices returned from Sarvam API")
            
            content = data["choices"][0]["message"]["content"]
            logger.info("Sarvam AI response received successfully.")
            return content.strip()
            
        except requests.exceptions.Timeout:
            logger.error("Sarvam API request timed out")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Sarvam API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Sarvam: {str(e)}")
            raise

    def analyze_event(self, event: Dict) -> Dict[str, Any]:
        """Analyze a single USD event using Sarvam AI."""
        
        event_text = f"""
Event: {event.get('event', 'N/A')}
Time: {event.get('time', 'N/A')}
Impact: {event.get('impact', 'N/A')}
Currency: {event.get('currency', 'USD')}
Forecast: {event.get('forecast', 'N/A')}
Previous: {event.get('previous', 'N/A')}
Actual: {event.get('actual', 'N/A')}
        """.strip()

        system_prompt = """You are a senior macro economist and trading strategist specializing in USD and Nasdaq markets.

Analyze the following USD economic event and provide a structured, professional analysis.

For each event provide exactly these sections:

1. What the event means
2. Why it matters
3. Expected impact on Nasdaq (positive/negative/neutral + explanation)
4. Expected impact on USD (positive/negative/neutral + explanation)
5. Bullish scenario (for Nasdaq)
6. Bearish scenario (for Nasdaq)
7. Volatility expectation (low/medium/high + why)
8. Trading risk (risk level + specific risk factors)

Respond with clean markdown using headings for each section. Keep analysis concise, data-driven, and actionable. Do not add extra intro or conclusion."""

        user_prompt = f"""Analyze this USD economic event:

{event_text}

Provide the 8 analysis sections exactly as specified."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            analysis = self._call_chat_completions(messages, max_tokens=2500, temperature=0.2)
            return {
                "event": event,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Failed to analyze event {event.get('event')}: {str(e)}")
            return {
                "event": event,
                "analysis": f"**Error analyzing event**: {str(e)}"
            }

    def generate_overall_outlook(self, analyzed_events: List[Dict], date_str: str) -> str:
        """Generate overall Nasdaq outlook, highest-risk window, and key takeaways."""
        
        if not analyzed_events:
            return "No significant USD events today."

        events_summary = "\n".join([
            f"- {e['event'].get('event', 'N/A')} ({e['event'].get('time', 'N/A')}, impact: {e['event'].get('impact', 'N/A')})"
            for e in analyzed_events
        ])

        system_prompt = """You are a senior macro trading strategist.

Based on the list of analyzed USD economic events for today, generate:

1. Overall Nasdaq Outlook (1-2 paragraphs)
2. Highest-Risk Trading Window (specific time range in ET + why it's risky)
3. Key Takeaways (3-5 bullet points)

Respond in clean markdown format. Be professional and concise."""

        user_prompt = f"""Date: {date_str}

Today's USD events:
{events_summary}

Generate the three required sections: Overall Nasdaq Outlook, Highest-Risk Trading Window, and Key Takeaways."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            outlook = self._call_chat_completions(messages, max_tokens=2000, temperature=0.25)
            return outlook
        except Exception as e:
            logger.error(f"Failed to generate overall outlook: {str(e)}")
            return f"**Error generating outlook**: {str(e)}"