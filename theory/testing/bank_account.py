
class InsufficientFund(Exception):
    pass


class BankAccount:
    def __init__(self, balance: float):
        if balance < 0:
            raise ValueError("balance cannot be negative")
        self._balance = balance

    @property
    def balance(self):
        return self._balance
    
    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("The amount must be positive")
        
        self._balance += amount

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("The withdrawal amount must be positive")

        if amount >= self.balance:
            raise InsufficientFund("Insufficient amount for withdrawal")
        
        self._balance -= amount