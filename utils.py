from datetime import datetime
from collections import namedtuple

Month = namedtuple('Month', 'month year')

def current_month():
    now = datetime.now()
    return Month(now.strftime('%m'), now.strftime('%Y'))