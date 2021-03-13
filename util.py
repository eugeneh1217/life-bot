from datetime import datetime

import os

PURCHASE_DATE_FORMAT = '%m/%d/%Y'
ITEMID_DATE_FORMAT = '%m/%y'

def log_event(message, module: str=None):
    """
    Log Event

    Args:
        message (any): Message to log.
        module (str, optional): Name of module where message came from. Defaults to None.
    """
    print(f"[{str(module) + ' | ' if module is not None else ''}{datetime.now().strftime('%H:%M:%S')}] {message}")

def itemid(date: datetime, item_name: str):
    """
    Convet datetime object and string to itemid

    Args:
        date (datetime): Datetime accurate to month
        item_name (str): Name of Item

    Returns:
        itemid (str): itemid
    """
    return f"{date.strftime(ITEMID_DATE_FORMAT)}:{item_name}"

def parse_itemid(itemid: str):
    """
    Convert itemid to datetime object and name string.
    Example itemid '01/21:food'

    Args:
        itemid (str): itemid

    Returns:
        tuple: datetime object accurate to month and item name.
    """
    if '/' not in itemid or ':' not in itemid:
        return None
    date_string, item_name = itemid.split(':')
    return datetime.strptime(date_string + '/01', ITEMID_DATE_FORMAT + '/%d'), item_name

def make_purchase(name: str, amount: float, date: datetime):
    """
    Generate purchase dictionary from purchase data.

    Args:
        name (str): Name of purchase.
        amount (float): Amount of purchase.
        date (datetime): Date of purchase.

    Returns:
        dict: Purchase dictionary.
    """
    purchase = {
        'name': name,
        'amount': amount,
        'date': date.strftime(PURCHASE_DATE_FORMAT)
    }
    return purchase
