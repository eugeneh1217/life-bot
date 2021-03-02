import unittest
from budget import Budget, Item, Purchase

mock_item_base = Item('food', 100)
mock_budget_base = Budget('March 2021')

class TestBudget(unittest.TestCase):
    def test_item_append_info(self):
        mock_item = Item(item=mock_item_base)
        mock_item.append(name='breakfast', day=1, amount=2)
        self.assertEqual(Purchase(0, 'breakfast', 1, 2) in mock_item.purchases, True)

    def test_item_append_purchase(self):
        mock_item = Item(item=mock_item_base)
        mock_item.append(purchase=Purchase(0, 'breakfast', 1, 2))
        self.assertEqual(Purchase(0, 'breakfast', 1, 2) in mock_item.purchases, True)

    def test_item_init(self):
        info_item = Item('food', 100)
        item_item = Item(item=info_item)
        self.assertEqual(info_item.name, mock_item_base.name)
        self.assertEqual(info_item.limit, mock_item_base.limit)
        self.assertEqual(item_item.name, mock_item_base.name)
        self.assertEqual(item_item.limit, mock_item_base.limit)

        info_item.limit = 110
        self.assertEqual(info_item.limit, 110)
        self.assertEqual(item_item.limit, 100)

        item_item.append(purchase=Purchase(0, 'lunch', 1, 2))
        self.assertNotEqual(len(info_item.purchases), len(item_item.purchases))

    def test_update_spent(self):
        item = Item(item=mock_item_base)
        item.update_spent()
        self.assertEqual(item.spent, 0)
        item.append(purchase=Purchase(0, 'breakfast', 1, 2))
        item.update_spent()
        self.assertEqual(item.spent, 2)


    def test_budget_init(self):
        budget_budget = Budget(mock_budget_base)
        budget_budget.items.append(mock_item_base)
        self.assertNotEqual(len(budget_budget.items), len(mock_budget_base.items))
        budget_budget.warnings[0.5] = 'red'
        self.assertNotEqual(len(budget_budget.warnings), len(mock_budget_base.warnings))
    
    def test_get_progression(self):
        budget_budget = Budget(mock_budget_base)
        food = Item('food', 100)
        food.append(name='breakfast', day=1, amount=2)
        budget_budget.items.append(food)
        self.assertEqual(budget_budget.get_progression()[0]['food'], .02)


if __name__ == '__main__':
    unittest.main()