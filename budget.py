"""
Summary:
    Impliment Budget
"""
from collections import namedtuple
from datetime import datetime

import calendar

Purchase = namedtuple('Purchase', 'pid name day amount')

class Item:
    """
    Summary:
        Class to manage purchases under an item
    """
    #pylint: disable=too-many-arguments
    #pylint: disable=dangerous-default-value
    def __init__(
        self, name: str=str(),
        limit: int=0,
        purchases: list=[],
        flags: list=[],
        item=None
    ):
        """
        Summary:
            Initialize Item

        Args:
            name (str, optional): Name of new Item. Defaults to None.
            limit (int, optional): Limit of new Item. Defaults to None.
            item (Item, optional): New Item object. Defaults to None.
        """
        if item is not None:
            self.name = item.name
            self.limit = item.limit
            self.spent = item.spent
            self.flags = list(item.flags)
            self.purchases = list(item.purchases)
        else:
            self.name = name
            self.limit = limit
            self.purchases = list(purchases)
            self.spent = 0
            self.update_spent()
            self.flags = list(flags)

    def __str__(self):
        purchases = '\n    '.join(map(str, self.purchases))
        return (
            f'name: {self.name}\n'
            f'limit: {self.limit}\n'
            f'spent: {self.spent}\n'
            f'purchases:\n    {purchases}'
        )

    def append(self, name: str=str(), day: int=0, amount: float=0, purchase: Purchase=None):
        """
        Summary:
            Append purchase to self.history
            Ignore informational args if purchase is passed

        Args:
            name (str, optional): Name of new purchase. Defaults to None.
            day (int, optional): Day new purchase was made. Defaults to None.
            amount (float, optional): Cost of new purchase. Defaults to None.
            purchase (Purchase, optional): New purchase object. Defaults to None.
        """
        if purchase is not None:
            self.purchases.append(Purchase(
                purchase.pid,
                purchase.name,
                purchase.day,
                purchase.amount
            ))
        else:
            self.purchases.append(Purchase(
                    (self.purchases[-1].pid + 1) if len(self.purchases) > 0 else 0,
                    name,
                    day,
                    amount
                ))

    def update_spent(self):
        """
        Summary:
            Recalculate Spent
        """
        self.spent =  sum( [ purchase.amount for purchase in self.purchases ] )

class Budget():
    """
    Summary:
        Budget Implimentation
    """
    #pylint: disable=too-many-arguments
    #pylint: disable=dangerous-default-value
    def __init__(
        self, name: str=str(), items: list=[], warnings: dict={},
        budget_id: int=0, owner_id: int=0, budget=None
    ):
        """
        Summary:
            Initialize Budget

        Args:
            name (str, optional): Name of budget. Defaults to None.
            items (list, optional): List of Budget Items. Defaults to None.
            warnings (dict, optional): Dictionary of warnings and their colors. Defaults to None.
            budget_id (int, optional): Budget id. Defaults to None.
            owner_id (int, optional): Ownder id. Defaults to None.
            budget (Budget, optional): Budget object of new Budget. Defaults to None.
        """
        if budget is not None:
            self.name = budget.name
            self.items = list(budget.items)
            self.warnings = dict(budget.warnings)
            self.budget_id = budget.budget_id
            self.owner_id = budget.owner_id
        else:
            self.name = name
            self.items = list(items)
            self.warnings = dict(warnings)
            self.budget_id = budget_id
            self.owner_id = owner_id

    def get_progression(self, *items):
        """
        Summary:
            Get percent progression of items and current month

        Args:
            items (Item, optional): Specific items to get progression of

        Returns:
            Dict: Name of item and its progression
            Float: Progression of current month
        """
        # update spents
        for item in self.items:
            item.update_spent()
        # get progression of items
        if len(items) != 0:
            progressions = { item.name: item.spent / item.limit for item in items }
        else:
            progressions = { item.name: item.spent / item.limit for item in self.items }
        # get progression of current month
        now = datetime.now()
        month_progression = now.month / calendar.monthrange(now.year, now.month)[1]
        return progressions, month_progression

    def check_warnings(self, *items):
        """
        Summary:
            Checks progressions against warnings.

        Returns:
            Dict: Item name and largest warning triggered
        """
        # check that self.warnings is not empty
        if len(self.warnings) == 0:
            return None
        if len(items) != 0:
            item_progression = self.get_progression(items)[0]
        else:
            item_progressions = self.get_progression(self.items)[0]

        # check progressions against warnings
        problems = {}
        for item_name, item_progression in item_progressions:
            for warning in self.warnings.keys():
                if item_progression > warning:
                    problems[item_name] = warning
        return problems
