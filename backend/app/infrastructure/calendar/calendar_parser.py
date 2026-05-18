"""
Calendar Parser - Extracts structured posts from DUDA's text response.
DDD: Infrastructure layer - Text parsing logic.
Max 200L strict. Type-safe.
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Spanish day names mapping
DAY_NAMES = {
    "lunes": 0,
    "martes": 1,
    "miércoles": 2,
    "miercoles": 2,  # without accent
    "jueves": 3,
    "viernes": 4,
    "sábado": 5,
    "sabado": 5,
    "domingo": 6
}


class CalendarParser:
    """
    Parses DUDA's calendar text responses into structured post data.

    Expected format:
    - **Martes 3** - **Post 1:** Title — **8:00 AM**
    - **Jueves 5** - **Post 2:** Another Title — **12:30 PM**
    """

    @staticmethod
    def _parse_time(time_str: str) -> str:
        """
        Convert time string to 24h format.

        Args:
            time_str: Time like "8:00 AM", "12:30 PM", "7:30 PM"

        Returns:
            Time in HH:MM:SS format

        Examples:
            "8:00 AM" -> "08:00:00"
            "12:30 PM" -> "12:30:00"
            "7:30 PM" -> "19:30:00"
        """
        time_str = time_str.strip().upper()

        # Extract time and period (AM/PM)
        match = re.search(r"(\d{1,2}):(\d{2})\s*(AM|PM)", time_str)
        if not match:
            logger.warning(f"Could not parse time: {time_str}")
            return "08:00:00"  # default

        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3)

        # Convert to 24h format
        if period == "PM" and hour != 12:
            hour += 12
        elif period == "AM" and hour == 12:
            hour = 0

        return f"{hour:02d}:{minute:02d}:00"

    @staticmethod
    def _extract_month_year(text: str) -> tuple:
        """Extract month and year from header. Returns (month, year) or (None, 2026)."""
        months = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
                  "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
        month_names = "|".join(months.keys())
        # Try "month year" or "de month"
        for pattern in [rf"({month_names})\s+(\d{{4}})", rf"de\s+({month_names})"]:
            match = re.search(pattern, text.lower())
            if match:
                return (months[match.group(1)], int(match.group(2)) if len(match.groups()) > 1 else 2026)
        return (None, 2026)

    @staticmethod
    def _parse_date(day_name: str, day_number: int, month: int = None, year: int = 2026) -> str:
        """Convert day name and number to YYYY-MM-DD. Uses specified month/year or finds next occurrence."""
        if month:
            try:
                return datetime(year, month, day_number).strftime("%Y-%m-%d")
            except ValueError:
                month = (month % 12) + 1
                year = year + 1 if month == 1 else year
                return datetime(year, month, day_number).strftime("%Y-%m-%d")

        # Find next occurrence if no month specified
        for offset in range(13):
            try:
                next_month = ((datetime.now().month + offset - 1) % 12) + 1
                target = datetime(year, next_month, day_number)
                if offset == 0 and target < datetime.now():
                    continue
                return target.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return datetime(year, 1, 1).strftime("%Y-%m-%d")

    @staticmethod
    def parse(text: str, client_id: str) -> List[Dict[str, Any]]:
        """Parse DUDA's calendar response. Handles multi-line format (day and post on separate lines)."""
        posts = []
        month, year = CalendarParser._extract_month_year(text)

        # Parse line by line - day and post are on separate lines:
        # - **Martes 3**
        # - **Post 1:** Title — **8:00 AM**
        lines = text.split('\n')
        logger.info(f"Calendar parser started: {len(lines)} lines received, month={month}, year={year}")

        current_day_name = None
        current_day_number = None

        # Patterns for separate lines (robust to variations)
        # Day: - **Martes 3** or - **martes 3** (case insensitive, flexible spacing)
        day_pattern = r"-+\s*\*\*\s*([A-Za-zá-úÁ-Úñ]+)\s+(\d{1,2})\s*\*\*"
        # Post: - **Post 1:** Title — **8:00 AM** (flexible dash: -, –, —)
        post_pattern = r"-+\s*\*\*\s*Post\s+\d+:?\*\*\s*(.+?)\s*[—–\-]+\s*\*\*([^*]+)\*\*"

        for line in lines:
            line = line.strip()

            # Check if this line is a day line
            day_match = re.search(day_pattern, line)
            if day_match:
                current_day_name = day_match.group(1).lower().strip()
                current_day_number = int(day_match.group(2))
                logger.info(f"Día detectado: {current_day_name.title()} {current_day_number}")
                continue

            # Check if this line is a post line
            post_match = re.search(post_pattern, line, re.IGNORECASE)
            if post_match and current_day_name and current_day_number:
                title = post_match.group(1).strip()
                time_str = post_match.group(2).strip()
                logger.info(f"Post detectado: '{title[:40]}...' para {current_day_name.title()} {current_day_number} a las {time_str}")

                # Validate day name
                if current_day_name not in DAY_NAMES:
                    logger.warning(f"Unknown day name: {current_day_name}")
                    continue

                # Parse date and time
                scheduled_date = CalendarParser._parse_date(current_day_name, current_day_number, month, year)
                scheduled_time = CalendarParser._parse_time(time_str)

                # Detect content type from title
                content_type = "carousel"
                if "reel" in title.lower() or "video" in title.lower():
                    content_type = "reel"
                elif "imagen" in title.lower() or "photo" in title.lower():
                    content_type = "post"

                post = {
                    "client_id": client_id,
                    "content_type": content_type,
                    "text_content": title,
                    "scheduled_date": scheduled_date,
                    "scheduled_time": scheduled_time,
                    "timezone": "America/Puerto_Rico",
                    "status": "scheduled",
                    "is_active": True,
                    "agent_assigned": "DUDA",
                    "hashtags": []
                }

                posts.append(post)
                logger.info(
                    f"Parsed post: {title[:30]}... on {scheduled_date} at {scheduled_time}"
                )

        return posts
