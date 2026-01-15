"""
时区工具模块
提供统一的时区感知 datetime 函数
"""
from datetime import datetime
import pytz
from flask import current_app


def get_local_tz():
    """获取配置的本地时区对象"""
    timezone_name = current_app.config.get('TIMEZONE', 'America/Mazatlan')
    return pytz.timezone(timezone_name)


def now():
    """返回当前本地时区的时间（时区感知）"""
    return datetime.now(get_local_tz())


def localize(dt):
    """
    将 naive datetime 转换为本地时区感知的 datetime
    
    Args:
        dt: naive datetime 对象
        
    Returns:
        时区感知的 datetime 对象
    """
    if dt is None:
        return None
    
    if dt.tzinfo is not None:
        # 如果已经有时区信息，转换到本地时区
        return dt.astimezone(get_local_tz())
    
    # 将 naive datetime 本地化
    return get_local_tz().localize(dt)


def to_local(dt):
    """
    将任意时区的 datetime 转换为本地时区
    
    Args:
        dt: datetime 对象（可以是 naive 或 aware）
        
    Returns:
        本地时区的 datetime 对象
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # 如果是 naive datetime，假设它是 UTC 时间
        dt = pytz.UTC.localize(dt)
    
    return dt.astimezone(get_local_tz())


def get_current_date():
    """获取当前本地时区的日期"""
    return now().date()


def get_current_datetime_str(format='%Y%m%d'):
    """
    获取当前本地时区的日期时间字符串
    
    Args:
        format: 日期格式字符串
        
    Returns:
        格式化的日期时间字符串
    """
    return now().strftime(format)
