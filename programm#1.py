import re
from abc import ABC, abstractmethod
import logging
from datetime import datetime

# Abstract base class for discounts 
# This class defines an interface for discount strategies.
# Follows the Open/Closed Principle (OCP) because new discount types can be added without modifying existing code & Follows the (SRP) because So that each function is responsible for only one thing.
class Discount(ABC):
    @abstractmethod
    def calculate_discount(self, amount: float) -> float:
        pass

# Concrete class for percentage discount
# Implements the strategy for percentage-based discounts.
class PercentageDiscount(Discount):
    def __init__(self, percentage: float):
        self.percentage = percentage

    def calculate_discount(self, amount: float) -> float:
        return amount * (self.percentage / 100)

# Concrete class for fixed amount discount
# Implements the strategy for fixed amount discounts.
class FixedAmountDiscount(Discount):
    def __init__(self, discount_amount: float):
        self.discount_amount = discount_amount

    def calculate_discount(self, amount: float) -> float:
        return self.discount_amount
    
# Abstract base class for payment methods
# Defines an interface for different payment methods.
# The Strategy Pattern is used here as different payment methods implement the strategy defined by this class.
# Follows the Open/Closed Principle (OCP) because new Payment types can be added without modifying existing code & Follows the (SRP) because So that each function is responsible for only one thing & Dependency Inversion Principle.
class PaymentMethod(ABC):
    @abstractmethod
    def validate(self, payment_details: dict) -> bool:
        pass

    @abstractmethod
    def process_payment(self, amount: float, payment_details: dict = None) -> bool:
        pass

    @abstractmethod
    def check_balance(self, payment_details: dict, amount: float) -> bool:
        pass

    @abstractmethod
    def get_discount(self) -> Discount:
        return None

# Concrete class for credit card payment
# Implements the strategy for credit card payments.
class CreditCardPayment(PaymentMethod):
    def __init__(self):
        self.approved_cards = {
            "1234567891234567": 500.0,  # Mock balance
        }

    def validate(self, payment_details: dict) -> bool:
        card_number = payment_details.get("card_number")
        expiry_date = payment_details.get("expiry_date")
        cvv = payment_details.get("cvv")

        if not card_number or not re.match(r"^\d{16}$", card_number):
            print("Invalid Credit Card number")
            return False
        if not expiry_date or not re.match(r"^\d{2}/\d{2}$", expiry_date):
            print("Invalid expiry date")
            return False
        if not cvv or not re.match(r"^\d{3}$", cvv):
            print("Invalid CVV")
            return False

        if card_number not in self.approved_cards:
            print("Card number not approved")
            return False

        print("Credit Card details are valid.")
        return True

    def check_balance(self, payment_details: dict, amount: float) -> bool:
        card_number = payment_details.get("card_number")
        if card_number in self.approved_cards:
            return self.approved_cards[card_number] >= amount
        return False

    def process_payment(self, amount: float, payment_details: dict = None) -> bool:
        card_number = payment_details.get("card_number")

        if not self.check_balance(payment_details, amount):
            print(f"Not enough money for {card_number}")
            return False

        self.approved_cards[card_number] -= amount
        print(f"Processing Credit Card payment of ${amount:.2f}")
        return True

    def get_discount(self) -> Discount:
        return FixedAmountDiscount(30)  # Fixed discount of $30

# Concrete class for PayPal payment
# Implements the strategy for PayPal payments.
class PayPalPayment(PaymentMethod):
    def __init__(self):
        self.approved_emails = {
            "Rand@gmail.com": 500.0,
            "Sama@gmail.com": 1000.0,
        }

    def validate(self, payment_details: dict) -> bool:
        email = payment_details.get("email")

        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("Invalid PayPal email")
            return False

        if email not in self.approved_emails:
            print("Email not approved for PayPal")
            return False

        print("PayPal details are valid.")
        return True

    def check_balance(self, payment_details: dict, amount: float) -> bool:
        email = payment_details.get("email")
        return self.approved_emails.get(email, 0) >= amount

    def process_payment(self, amount: float, payment_details: dict) -> bool:
        email = payment_details.get("email")

        if not self.check_balance(payment_details, amount):
            print(f"Not enough money for {email}")
            return False

        self.approved_emails[email] -= amount
        print(f"Processing PayPal payment of ${amount:.2f}...")
        print(f"PayPal payment of ${amount:.2f} was successful.")
        return True

    def get_discount(self) -> Discount:
        return PercentageDiscount(10)  # 10% discount for PayPal

# Concrete class for cryptocurrency payment
# Implements the strategy for cryptocurrency payments.
class CryptocurrencyPayment(PaymentMethod):
    def __init__(self):
        self.mock_wallets = {
            "1BoatSLRHtKNngkdXEeobR76b53LETtpyT": 1000.0,
        }

    def validate(self, payment_details: dict) -> bool:
        wallet_address = payment_details.get("wallet_address")

        if not wallet_address or len(wallet_address) != 34:
            print("Invalid Cryptocurrency wallet address")
            return False

        if wallet_address not in self.mock_wallets:
            print("Wallet address not found")
            return False

        print("Cryptocurrency wallet details are valid.")
        return True

    def check_balance(self, payment_details: dict, amount: float) -> bool:
        wallet_address = payment_details.get("wallet_address")
        return self.mock_wallets.get(wallet_address, 0) >= amount

    def process_payment(self, amount: float, payment_details: dict) -> bool:
        wallet_address = payment_details.get("wallet_address")

        if not self.check_balance(payment_details, amount):
            print(f"Not enough money for {wallet_address}")
            return False

        self.mock_wallets[wallet_address] -= amount
        print(f"Processing Cryptocurrency payment of ${amount:.2f}...")
        print(f"Cryptocurrency payment of ${amount:.2f} was successful.")
        return True

    def get_discount(self) -> Discount:
        return PercentageDiscount(20)  # 20% discount for Cryptocurrency

# Order class with optional discount strategy
# The Order class encapsulates the order details and applies the payment and discount strategies.
# Follows the Single Responsibility Principle (SRP) as it manages only the order's state and its related operations & Liskov Substitution Principle.
class Order:
    def __init__(self):
        self.items = []
        self.quantities = []
        self.prices = []
        self.status = "open"
        self.payment_method = None
        self.discount_strategy = None

    def add_item(self, name: str, quantity: int, price: float):
        self.items.append(name)
        self.quantities.append(quantity)
        self.prices.append(price)

    def total_price(self):
        total = 0
        for quantity, price in zip(self.quantities, self.prices):
            total += quantity * price
        return total

    def set_payment_method(self, payment_method: PaymentMethod):
        self.payment_method = payment_method

    def set_discount_strategy(self, discount_strategy: Discount):
        self.discount_strategy = discount_strategy

    def apply_discounts(self):
        if self.discount_strategy:
            return self.discount_strategy.calculate_discount(self.total_price())
        return 0

    def pay(self, payment_details: dict):
        if not self.payment_method:
           return True
        if self.payment_method.validate(payment_details):
            discount = self.apply_discounts()
            final_amount = self.total_price() - discount
            if final_amount < 0:
                final_amount = 0

            if self.payment_method.process_payment(final_amount, payment_details):
                self.status = "paid"
                return True
        return False

# Abstract base class for logging transactions
# Defines the interface for logging mechanisms.
# Follows the Open/Closed Principle (OCP) because new TransactionLogger types can be added without modifying existing code & Follows the (SRP) because So that each function is responsible for only one thing.
class TransactionLogger(ABC):
    @abstractmethod
    def log_transaction(self, payment_method: str, amount: float, success: bool):
        pass

# Concrete class for logging transactions to a file
# Implements the file-based logging mechanism.
class FileLogger(TransactionLogger):
    def __init__(self, filename: str):
        self.filename = filename
        logging.basicConfig(filename=self.filename, level=logging.INFO, format='%(message)s')

    def log_transaction(self, payment_method: str, amount: float, success: bool):
        status = 'Success' if success else 'Failure'
        log_message = f"{datetime.now()}: {payment_method} payment of ${amount:.2f} - {status}"
        logging.info(log_message)

# Main function
# Demonstrates the use of Strategy Pattern and Dependency Injection by allowing different payment methods and discount strategies to be chosen at runtime.
def main():
    print("Welcome to the Payment System")

    # Create an Order
    order = Order()

    # Add items to the order
    while True:
        item_name = input("Enter the item name (or 'done' to finish): ")
        if item_name.lower() == 'done':
            break
        quantity = int(input(f"Enter the quantity for {item_name}: "))
        price = float(input(f"Enter the price for {item_name}: "))
        order.add_item(item_name, quantity, price)

    # Choose a payment method
    print("Choose a payment method:")
    print("1. Credit Card")
    print("2. PayPal")
    print("3. Cryptocurrency")
    print("4. Cash")
    method_choice = input("Enter the number of your choice: ")

    if method_choice == '1':
        payment_method = CreditCardPayment()
    elif method_choice == '2':
        payment_method = PayPalPayment()
    elif method_choice == '3':
        payment_method = CryptocurrencyPayment()
    elif method_choice == '4':
        payment_method = None
    else:
        print("Invalid choice.")
        return

    # Set the payment method
    if payment_method:
        order.set_payment_method(payment_method)
        discount_strategy = payment_method.get_discount()
        if discount_strategy:
            order.set_discount_strategy(discount_strategy)

    # Process the payment
    payment_details = {}
    if payment_method:
        if isinstance(payment_method, CreditCardPayment):
            payment_details = {
                "card_number": input("Enter your Credit Card number (16 digits): "),
                "expiry_date": input("Enter the expiry date (MM/YY): "),
                "cvv": input("Enter the CVV (3 digits): ")
            }
        elif isinstance(payment_method, PayPalPayment):
            payment_details = {
                "email": input("Enter your PayPal email: ")
            }
        elif isinstance(payment_method, CryptocurrencyPayment):
            payment_details = {
                "wallet_address": input("Enter your Cryptocurrency wallet address: ")
            }

        success = order.pay(payment_details)
        logger = FileLogger('transactions.log')
        payment_method_name = payment_method.__class__.__name__.replace('Payment', '')
        logger.log_transaction(payment_method_name, order.total_price(), success)
        if success:
            print("Payment successful!")
        else:
            print("Payment failed.")
    else:
        payment_details = {
                "name": input("Enter your name: "),
                "address": input("Enter your address: ")
            }      
        print("Cash payment does not include any discount.")
        success = order.pay(payment_details)
        logger = TransactionLogger('transactions.log')
        logger.log_transaction("cash", order.total_price(), success) 
        print("Payment successful!")     
         
if __name__ == "__main__":
    main()
