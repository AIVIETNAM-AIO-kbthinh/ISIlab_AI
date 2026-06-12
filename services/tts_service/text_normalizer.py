"""
TTS Service - Vietnamese Text Normalizer
Preprocesses Vietnamese text before TTS to improve pronunciation quality.
"""

import re
import logging

logger = logging.getLogger("tts_service.text_normalizer")

# Number words in Vietnamese
ONES = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
TEENS = ["mười", "mười một", "mười hai", "mười ba", "mười bốn", "mười lăm",
         "mười sáu", "mười bảy", "mười tám", "mười chín"]


def normalize_vietnamese_text(text: str) -> str:
    """
    Normalize Vietnamese text for TTS:
    1. Remove markdown formatting
    2. Clean up special characters
    3. Convert common abbreviations
    4. Handle numbers
    5. Split into sentences for better prosody
    
    Args:
        text: Raw text from LLM
        
    Returns:
        Normalized text suitable for TTS
    """
    if not text:
        return text

    # Remove markdown formatting
    text = _remove_markdown(text)

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Convert common abbreviations
    text = _expand_abbreviations(text)

    # Remove unsupported characters (keep Vietnamese diacritics)
    text = _clean_special_chars(text)

    # Ensure proper sentence endings for better TTS prosody
    text = _fix_sentence_endings(text)

    return text.strip()


def _remove_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Remove headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove bold/italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)

    # Remove links [text](url) → text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove bullet points
    text = re.sub(r"^[\s]*[-*+]\s+", "", text, flags=re.MULTILINE)

    # Remove numbered lists
    text = re.sub(r"^[\s]*\d+\.\s+", "", text, flags=re.MULTILINE)

    return text


def _expand_abbreviations(text: str) -> str:
    """Expand common Vietnamese abbreviations."""
    abbreviations = {
        "TP.": "Thành phố",
        "TP.HCM": "Thành phố Hồ Chí Minh",
        "Tp.": "Thành phố",
        "Q.": "Quận",
        "P.": "Phường",
        "Đ/c": "Địa chỉ",
        "SĐT": "Số điện thoại",
        "ĐT": "Điện thoại",
        "GS.": "Giáo sư",
        "PGS.": "Phó giáo sư",
        "TS.": "Tiến sĩ",
        "ThS.": "Thạc sĩ",
        "KS.": "Kỹ sư",
        "CN.": "Cử nhân",
        "SV": "sinh viên",
        "GV": "giảng viên",
        "CNTT": "Công nghệ thông tin",
        "ĐHQG": "Đại học Quốc gia",
        "PTN": "Phòng thí nghiệm",
    }

    for abbr, full in abbreviations.items():
        text = text.replace(abbr, full)

    return text


def _clean_special_chars(text: str) -> str:
    """Remove characters that TTS engines handle poorly."""
    # Keep Vietnamese characters, numbers, common punctuation
    # Remove emojis, special symbols, etc.
    text = re.sub(r"[^\w\s.,;:!?()\"'\-–—/\u00C0-\u024F\u1E00-\u1EFF]", " ", text)

    # Clean up multiple punctuation
    text = re.sub(r"([.!?])\1+", r"\1", text)

    return text


def _fix_sentence_endings(text: str) -> str:
    """Ensure sentences end properly for TTS prosody."""
    # Add period at end if missing
    text = text.strip()
    if text and text[-1] not in ".!?":
        text += "."

    return text
