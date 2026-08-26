import unittest

from bank_account import BankAccount

class TestBankAccount(unittest.TestCase):

    def setUp(self) -> None:
        self.bank_account = BankAccount(100)

    def test_deposit(self):
        self.bank_account.deposit(100)
        self.assertEqual(self.bank_account.balance, 200)
    
    def test_withdraw(self):
        self.bank_account.withdraw(50)
        self.assertEqual(self.bank_account.balance, 50)

    @unittest.skip("Work in progress")
    def test_case_2(self):
        pass

    def tearDown(self) -> None:
        self.bank_account = None


@unittest.skip('Work in progress')
class TestDemo(unittest.TestCase):
    def test_case_1(self):
        self.assertEqual(1+1, 2)

    def test_case_2(self):
        self.assertIsNotNone([])

if __name__ == "__main__":
    unittest.main()
