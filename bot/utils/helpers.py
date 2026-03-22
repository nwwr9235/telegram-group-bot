"""
دوال مساعدة مشتركة
"""
import re


def extract_username(text: str) -> str:
    """استخراج اليوزر من النص"""
    match = re.search(r'@(\w+)', text)
    return match.group(1) if match else None


def extract_duration(text: str) -> int:
    """استخراج المدة بالثواني"""
    # ساعات
    match = re.search(r'(\d+)\s*(ساعة|h|hour)', text, re.IGNORECASE)
    if match:
        return int(match.group(1)) * 3600
    
    # دقائق
    match = re.search(r'(\d+)\s*(دقيقة|m|min)', text, re.IGNORECASE)
    if match:
        return int(match.group(1)) * 60
    
    # أيام
    match = re.search(r'(\d+)\s*(يوم|d|day)', text, re.IGNORECASE)
    if match:
        return int(match.group(1)) * 86400
    
    return 3600  # افتراضي 1 ساعة


def format_time(seconds: int) -> str:
    """تنسيق الثواني لقراءة بشرية"""
    if seconds >= 86400:
        return f"{seconds // 86400} يوم"
    elif seconds >= 3600:
        return f"{seconds // 3600} ساعة"
    elif seconds >= 60:
        return f"{seconds // 60} دقيقة"
    return f"{seconds} ثانية"


def escape_html(text: str) -> str:
    """تجنب مشاكل HTML"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

