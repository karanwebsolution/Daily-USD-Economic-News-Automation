from datetime import datetime
from typing import List, Dict, Any
from logger import logger
import html

class EmailGenerator:
    def __init__(self):
        self.ny_tz = "America/New_York"

    def _escape(self, text: str) -> str:
        """Escape HTML for safety."""
        return html.escape(str(text)) if text else ""

    def generate_html_report(self, analyzed_events: List[Dict], overall_outlook: str, date_str: str) -> str:
        """Generate a professional HTML email report."""
        
        today = datetime.now().strftime("%B %d, %Y")
        
        html_parts = [
            """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily USD Economic News Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f8f9fa; }
        .container { max-width: 980px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden; }
        .header { background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px 40px; }
        .header h1 { margin: 0; font-size: 28px; font-weight: 600; }
        .header .subtitle { margin: 8px 0 0; opacity: 0.9; font-size: 16px; }
        .section { padding: 30px 40px; border-bottom: 1px solid #eee; }
        .section:last-child { border-bottom: none; }
        h2 { color: #1e40af; font-size: 22px; margin: 0 0 20px; border-bottom: 3px solid #dbeafe; padding-bottom: 8px; }
        .event-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 24px; margin-bottom: 24px; }
        .event-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
        .event-title { font-size: 20px; font-weight: 600; color: #1e2937; margin: 0; }
        .event-meta { display: flex; gap: 12px; flex-wrap: wrap; }
        .badge { padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }
        .badge-high { background: #fee2e2; color: #b91c1c; }
        .badge-medium { background: #fef3c7; color: #92400e; }
        .analysis-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
        .analysis-item { background: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; }
        .analysis-item h4 { margin: 0 0 8px; font-size: 15px; color: #334155; }
        .analysis-item p { margin: 0; font-size: 14.5px; color: #475569; line-height: 1.55; }
        .outlook-section { background: #f0f9ff; padding: 26px; border-radius: 10px; border-left: 5px solid #3b82f6; }
        .key-takeaways { background: #fefce8; padding: 20px; border-radius: 8px; }
        ul { padding-left: 20px; }
        li { margin-bottom: 6px; }
        .footer { background: #f1f5f9; padding: 20px 40px; font-size: 13px; color: #64748b; text-align: center; }
        .meta { font-size: 13px; color: #64748b; margin-top: 4px; }
        @media (max-width: 700px) {
            .analysis-grid { grid-template-columns: 1fr; }
            .container { margin: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Daily USD Economic News Report</h1>
            <p class="subtitle">""" + today + """ • 30 minutes before Nasdaq open</p>
        </div>
"""
        ]

        # Events section
        html_parts.append('<div class="section"><h2>📅 Today\'s USD Economic Events</h2>')
        
        if not analyzed_events:
            html_parts.append('<p style="color:#64748b">No significant USD events scheduled for today.</p>')
        else:
            for idx, item in enumerate(analyzed_events, 1):
                event = item["event"]
                analysis = item["analysis"]
                
                impact = event.get("impact", "medium").lower()
                badge_class = "badge-high" if impact == "high" else "badge-medium"
                impact_label = impact.upper()
                
                html_parts.append(f"""
                <div class="event-card">
                    <div class="event-header">
                        <h3 class="event-title">{self._escape(event.get('event', 'Unknown Event'))}</h3>
                        <div class="event-meta">
                            <span class="badge {badge_class}">{impact_label}</span>
                            <span style="background:#e0f2fe;color:#0369a1;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:600;">{self._escape(event.get('time', 'N/A'))} ET</span>
                        </div>
                    </div>
                    
                    <div class="meta">
                        <strong>Forecast:</strong> {self._escape(event.get('forecast') or 'N/A')} &nbsp;&nbsp;
                        <strong>Previous:</strong> {self._escape(event.get('previous') or 'N/A')}
                    </div>
                    
                    <div style="margin-top:18px; padding-top:18px; border-top:1px solid #e2e8f0;">
                        {self._convert_markdown_to_html(analysis)}
                    </div>
                </div>
                """)

        html_parts.append('</div>')

        # Overall Outlook
        html_parts.append('<div class="section"><h2>📊 Overall Nasdaq Outlook</h2>')
        html_parts.append(f'<div class="outlook-section">{self._convert_markdown_to_html(overall_outlook)}</div>')
        html_parts.append('</div>')

        # Footer
        html_parts.append(f"""
        <div class="footer">
            <p>Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ET • Powered by Sarvam AI</p>
            <p style="margin-top:6px;">This report is for informational purposes only. Not financial advice.</p>
        </div>
    </div>
</body>
</html>
        """)

        full_html = "".join(html_parts)
        logger.info("HTML email report generated successfully.")
        return full_html

    def _convert_markdown_to_html(self, markdown_text: str) -> str:
        """Convert simple markdown to HTML for email."""
        if not markdown_text:
            return ""
        
        # Basic markdown to HTML conversion
        lines = markdown_text.split("\n")
        html_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                continue
                
            # Headings
            if line.startswith("### "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h4 style='margin:16px 0 8px;color:#1e40af;'>{self._escape(line[4:])}</h4>")
            elif line.startswith("## "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h3 style='margin:20px 0 10px;color:#1e3a8a;'>{self._escape(line[3:])}</h3>")
            elif line.startswith("# "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<h2 style='margin:20px 0 12px;color:#1e3a8a;'>{self._escape(line[2:])}</h2>")
            # Bold
            elif line.startswith("**") and line.endswith("**"):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<p><strong>{self._escape(line[2:-2])}</strong></p>")
            # Bullet points
            elif line.startswith("- ") or line.startswith("* "):
                if not in_list:
                    html_lines.append("<ul style='margin:8px 0;padding-left:22px;'>")
                    in_list = True
                html_lines.append(f"<li>{self._escape(line[2:])}</li>")
            else:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                # Escape and handle bold within paragraph
                escaped = self._escape(line)
                # Simple **bold** support
                escaped = escaped.replace("**", "<strong>").replace("</strong>", "</strong>") # simplistic
                html_lines.append(f"<p style='margin:6px 0 10px;'>{escaped}</p>")
        
        if in_list:
            html_lines.append("</ul>")
            
        return "\n".join(html_lines)