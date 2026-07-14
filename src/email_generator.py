from datetime import datetime
from typing import List, Dict, Any
from logger import logger
import html

# Design tokens
COLOR_NAVY = "#0f1b3d"
COLOR_NAVY_LIGHT = "#1e3a8a"
COLOR_ACCENT = "#2563eb"
COLOR_BG = "#eef1f6"
COLOR_CARD = "#ffffff"
COLOR_BORDER = "#e2e6ee"
COLOR_TEXT = "#1a2233"
COLOR_MUTED = "#5b6474"
COLOR_HIGH_BG = "#fdecec"
COLOR_HIGH_TEXT = "#b3261e"
COLOR_MED_BG = "#fff4e0"
COLOR_MED_TEXT = "#9a5b00"


class EmailGenerator:
    def __init__(self):
        self.ny_tz = "America/New_York"

    def _escape(self, text: str) -> str:
        """Escape HTML for safety."""
        return html.escape(str(text)) if text else ""

    def generate_html_report(self, analyzed_events: List[Dict], overall_outlook: str, date_str: str) -> str:
        """Generate a professional, email-client-safe HTML report.

        Built with tables and inline styles (the standard for email HTML,
        since many clients strip <style> blocks or apply their own dark-mode
        recoloring on top of CSS). color-scheme meta tags plus explicit
        bgcolor/style pairing on every cell keep the report looking the
        same in Gmail's dark mode instead of getting auto-inverted.
        """

        today = datetime.now().strftime("%B %d, %Y")

        parts = [f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="x-apple-disable-message-reformatting">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<title>Daily USD Economic News Report</title>
<style>
  :root {{ color-scheme: light; supported-color-schemes: light; }}
  body {{ margin:0; padding:0; background-color:{COLOR_BG} !important; }}
  table {{ border-collapse:collapse; }}
  a {{ color:{COLOR_ACCENT}; }}
  @media (prefers-color-scheme: dark) {{
    body, .bg-page {{ background-color:{COLOR_BG} !important; }}
    .card, .bg-card {{ background-color:{COLOR_CARD} !important; }}
    .text-main {{ color:{COLOR_TEXT} !important; }}
    .text-muted {{ color:{COLOR_MUTED} !important; }}
  }}
  @media (max-width: 640px) {{
    .container {{ width:100% !important; }}
    .stack {{ display:block !important; width:100% !important; }}
    .px {{ padding-left:20px !important; padding-right:20px !important; }}
  }}
</style>
</head>
<body class="bg-page" style="margin:0;padding:0;background-color:{COLOR_BG};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="bg-page" style="background-color:{COLOR_BG};padding:24px 0;">
<tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" class="container" style="width:600px;max-width:600px;background-color:{COLOR_CARD};border-radius:14px;overflow:hidden;box-shadow:0 2px 14px rgba(15,27,61,0.08);">

<!-- Header -->
<tr><td style="background-color:{COLOR_NAVY};background-image:linear-gradient(135deg,{COLOR_NAVY},{COLOR_NAVY_LIGHT});padding:32px 36px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td>
<div style="font-size:12px;font-weight:700;letter-spacing:1.5px;color:#93c5fd;text-transform:uppercase;margin-bottom:8px;">Daily Market Briefing</div>
<div style="font-size:24px;font-weight:700;color:#ffffff;line-height:1.3;">USD Economic News Report</div>
<div style="font-size:14px;color:#c7d2fe;margin-top:8px;">{today} &nbsp;•&nbsp; 30 minutes before Nasdaq open</div>
</td></tr></table>
</td></tr>

<!-- Events section -->
<tr><td class="px" style="padding:32px 36px 8px 36px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td>
<div class="text-main" style="font-size:18px;font-weight:700;color:{COLOR_TEXT};border-bottom:2px solid {COLOR_BORDER};padding-bottom:10px;margin-bottom:20px;">📅 Today's USD Economic Events</div>
</td></tr></table>
"""]

        if not analyzed_events:
            parts.append(f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f6f8fb;border:1px solid {COLOR_BORDER};border-radius:10px;margin-bottom:8px;">
<tr><td style="padding:20px;text-align:center;">
<div class="text-muted" style="font-size:14px;color:{COLOR_MUTED};">No significant USD economic events are scheduled for today.</div>
</td></tr></table>
""")
        else:
            for item in analyzed_events:
                event = item["event"]
                analysis = item["analysis"]
                impact = (event.get("impact") or "medium").lower()
                if impact == "high":
                    badge_bg, badge_text = COLOR_HIGH_BG, COLOR_HIGH_TEXT
                else:
                    badge_bg, badge_text = COLOR_MED_BG, COLOR_MED_TEXT

                parts.append(f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="card" style="background-color:{COLOR_CARD};border:1px solid {COLOR_BORDER};border-radius:12px;margin-bottom:18px;">
<tr><td style="padding:22px 24px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
    <td class="text-main" style="font-size:17px;font-weight:700;color:{COLOR_TEXT};">{self._escape(event.get('event', 'Unknown Event'))}</td>
    <td align="right" style="white-space:nowrap;">
      <span style="display:inline-block;background-color:{badge_bg};color:{badge_text};font-size:12px;font-weight:700;padding:4px 10px;border-radius:12px;margin-right:6px;">{impact.upper()}</span>
      <span style="display:inline-block;background-color:#e0edff;color:#1d4ed8;font-size:12px;font-weight:700;padding:4px 10px;border-radius:12px;">{self._escape(event.get('time', 'N/A'))} ET</span>
    </td>
  </tr></table>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:14px;">
  <tr><td class="text-muted" style="font-size:13px;color:{COLOR_MUTED};">
    <strong style="color:{COLOR_TEXT};">Forecast:</strong> {self._escape(event.get('forecast') or 'N/A')}
    &nbsp;&nbsp;|&nbsp;&nbsp;
    <strong style="color:{COLOR_TEXT};">Previous:</strong> {self._escape(event.get('previous') or 'N/A')}
  </td></tr>
  </table>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px;border-top:1px solid {COLOR_BORDER};">
  <tr><td style="padding-top:16px;">
    {self._convert_markdown_to_html(analysis)}
  </td></tr>
  </table>
</td></tr>
</table>
""")

        parts.append("</td></tr>")

        # Overall outlook
        parts.append(f"""
<tr><td class="px" style="padding:8px 36px 32px 36px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td>
<div class="text-main" style="font-size:18px;font-weight:700;color:{COLOR_TEXT};border-bottom:2px solid {COLOR_BORDER};padding-bottom:10px;margin-bottom:16px;">📊 Overall Nasdaq Outlook</div>
</td></tr></table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f0f6ff;border-left:4px solid {COLOR_ACCENT};border-radius:8px;">
<tr><td style="padding:22px 24px;">
{self._convert_markdown_to_html(overall_outlook)}
</td></tr>
</table>
</td></tr>
""")

        # Footer
        parts.append(f"""
<tr><td style="background-color:#f6f8fb;border-top:1px solid {COLOR_BORDER};padding:20px 36px;text-align:center;">
<div class="text-muted" style="font-size:12px;color:{COLOR_MUTED};">Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ET &nbsp;•&nbsp; Powered by Sarvam AI</div>
<div class="text-muted" style="font-size:12px;color:{COLOR_MUTED};margin-top:6px;">This report is for informational purposes only. Not financial advice.</div>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>
""")

        full_html = "".join(parts)
        logger.info("HTML email report generated successfully.")
        return full_html

    def _convert_markdown_to_html(self, markdown_text: str) -> str:
        """Convert simple markdown to inline-styled HTML for email clients."""
        if not markdown_text:
            return ""

        lines = markdown_text.split("\n")
        html_lines = []
        in_list = False

        def close_list():
            nonlocal in_list
            if in_list:
                html_lines.append("</ul>")
                in_list = False

        for line in lines:
            line = line.strip()
            if not line:
                close_list()
                continue

            if line.startswith("### "):
                close_list()
                html_lines.append(f"<h4 style='margin:16px 0 8px;font-size:14px;color:{COLOR_NAVY_LIGHT};'>{self._escape(line[4:])}</h4>")
            elif line.startswith("## "):
                close_list()
                html_lines.append(f"<h3 style='margin:18px 0 8px;font-size:15px;color:{COLOR_NAVY};'>{self._escape(line[3:])}</h3>")
            elif line.startswith("# "):
                close_list()
                html_lines.append(f"<h2 style='margin:18px 0 10px;font-size:16px;color:{COLOR_NAVY};'>{self._escape(line[2:])}</h2>")
            elif line.startswith("**") and line.endswith("**") and len(line) > 4:
                close_list()
                html_lines.append(f"<p style='margin:6px 0;font-size:14px;'><strong style='color:{COLOR_TEXT};'>{self._escape(line[2:-2])}</strong></p>")
            elif line.startswith("- ") or line.startswith("* "):
                if not in_list:
                    html_lines.append(f"<ul style='margin:8px 0;padding-left:20px;font-size:14px;color:{COLOR_TEXT};'>")
                    in_list = True
                html_lines.append(f"<li style='margin-bottom:6px;line-height:1.5;'>{self._render_inline_bold(line[2:])}</li>")
            else:
                close_list()
                html_lines.append(f"<p style='margin:6px 0 10px;font-size:14px;line-height:1.6;color:{COLOR_TEXT};'>{self._render_inline_bold(line)}</p>")

        close_list()
        return "\n".join(html_lines)

    def _render_inline_bold(self, text: str) -> str:
        """Escape text but properly render **bold** segments inline."""
        escaped = self._escape(text)
        parts = escaped.split("**")
        out = []
        for i, part in enumerate(parts):
            out.append(f"<strong style='color:{COLOR_TEXT};'>{part}</strong>" if i % 2 == 1 else part)
        return "".join(out)
