"""
测试时区配置
"""
from app import create_app
from app.utils import timezone
from datetime import datetime
import pytz

app = create_app('development')

with app.app_context():
    # 测试时区函数
    local_now = timezone.now()
    print(f"当前马萨特兰时间: {local_now}")
    print(f"时区: {local_now.tzinfo}")
    print(f"时间字符串: {local_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # 验证时区是否正确
    mazatlan_tz = pytz.timezone('America/Mazatlan')
    assert local_now.tzinfo == mazatlan_tz, "时区不匹配!"
    print("✓ 时区配置正确")
    
    # 测试其他工具函数
    current_date = timezone.get_current_date()
    print(f"\n当前日期: {current_date}")
    
    date_str = timezone.get_current_datetime_str('%Y%m%d')
    print(f"日期字符串: {date_str}")
    
    print("\n✓ 所有时区工具函数测试通过!")
