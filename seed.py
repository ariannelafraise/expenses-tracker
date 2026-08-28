import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from database import Session
from models import (
    Transaction,
    Tag,
    TransactionDirection,
    BlacklistKeyword,
)

NUMBER_OF_TRANSACTIONS = 500
START_DATE = date(2025, 9, 1)
END_DATE = date(2026, 8, 25)
RANDOM_SEED = 42


# ============================================================
# Tags
# ============================================================

TAG_NAMES = [
    "Food",
    "Groceries",
    "Gas",
    "Transport",
    "Rent",
    "Utilities",
    "Subscriptions",
    "Entertainment",
    "Shopping",
    "Health",
    "Restaurant",
    "Coffee",
    "Travel",
    "Electronics",
    "Clothing",
    "Refund",
]


# ============================================================
# Blacklist Keywords
# ============================================================

BLACKLIST_KEYWORDS = [
    ("BANK FEE", True),
    ("ACCOUNT FEE", True),
    ("INTERAC", False),
    ("TRANSFER", False),
    ("PAYMENT", False),
    ("INTEREST", False),
    ("SERVICE CHARGE", False),
]


# ============================================================
# Merchants
# ============================================================

EXPENSES = [
    # Groceries
    ("IGA", ["Groceries", "Food"], 20, 180),
    ("Metro", ["Groceries", "Food"], 20, 150),
    ("Super C", ["Groceries", "Food"], 15, 120),
    ("Provigo", ["Groceries", "Food"], 20, 180),
    ("Costco", ["Groceries", "Shopping"], 50, 300),
    # Gas
    ("ESSO", ["Gas", "Transport"], 40, 100),
    ("Shell", ["Gas", "Transport"], 40, 100),
    ("Ultramar", ["Gas", "Transport"], 40, 100),
    ("Petro-Canada", ["Gas", "Transport"], 40, 100),
    # Transport
    ("Uber", ["Transport"], 10, 80),
    ("STM", ["Transport"], 3, 30),
    ("Communauto", ["Transport"], 10, 100),
    ("Via Rail", ["Transport", "Travel"], 30, 300),
    # Restaurants
    ("McDonald's", ["Restaurant", "Food"], 10, 40),
    ("Subway", ["Restaurant", "Food"], 10, 35),
    ("Pizza Pizza", ["Restaurant", "Food"], 15, 50),
    ("Restaurant", ["Restaurant", "Food"], 20, 150),
    ("Sushi Restaurant", ["Restaurant", "Food"], 30, 150),
    # Coffee
    ("Starbucks", ["Coffee", "Food"], 4, 20),
    ("Tim Hortons", ["Coffee", "Food"], 3, 20),
    ("Second Cup", ["Coffee", "Food"], 4, 20),
    ("Local Cafe", ["Coffee", "Food"], 4, 25),
    # Shopping
    ("Walmart", ["Shopping"], 20, 200),
    ("Amazon", ["Shopping"], 15, 250),
    ("Dollarama", ["Shopping"], 5, 80),
    # Electronics
    ("Best Buy", ["Electronics", "Shopping"], 30, 500),
    ("Apple", ["Electronics"], 20, 1500),
    ("Canada Computers", ["Electronics"], 30, 1000),
    # Clothing
    ("H&M", ["Clothing", "Shopping"], 20, 150),
    ("Uniqlo", ["Clothing", "Shopping"], 20, 150),
    ("Simons", ["Clothing", "Shopping"], 30, 250),
    # Entertainment
    ("Cinema", ["Entertainment"], 15, 60),
    ("Theatre", ["Entertainment"], 30, 150),
    ("Concert", ["Entertainment"], 40, 250),
    ("Steam", ["Entertainment"], 5, 100),
    # Subscriptions
    ("Netflix", ["Subscriptions", "Entertainment"], 10, 30),
    ("Spotify", ["Subscriptions", "Entertainment"], 10, 20),
    ("YouTube Premium", ["Subscriptions", "Entertainment"], 10, 25),
    ("Amazon Prime", ["Subscriptions", "Shopping"], 10, 20),
    # Health
    ("Pharmacy", ["Health"], 10, 100),
    ("Jean Coutu", ["Health"], 10, 100),
    ("Doctor", ["Health"], 30, 200),
    ("Dentist", ["Health"], 50, 500),
    # Travel
    ("Air Canada", ["Travel"], 100, 800),
    ("Airbnb", ["Travel"], 80, 500),
    ("Hotel", ["Travel"], 80, 400),
]


# ============================================================
# Helpers
# ============================================================


def random_date(start: date, end: date) -> date:
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


def random_amount(minimum: float, maximum: float) -> Decimal:
    amount = random.uniform(minimum, maximum)
    return Decimal(f"{amount:.2f}")


def random_identifiant() -> str:
    return f"seed-{random.getrandbits(128):032x}"


# ============================================================
# Tags
# ============================================================


def create_tags(session):
    tags = {}

    for name in TAG_NAMES:
        tag = session.scalar(select(Tag).where(Tag.name == name))

        if tag is None:
            tag = Tag(name=name)
            session.add(tag)
            session.flush()

        tags[name] = tag

    return tags


# ============================================================
# Blacklist Keywords
# ============================================================


def create_blacklist_keywords(session):
    keywords = {}

    for keyword, strict in BLACKLIST_KEYWORDS:
        blacklist_keyword = session.scalar(
            select(BlacklistKeyword).where(BlacklistKeyword.keyword == keyword)
        )

        if blacklist_keyword is None:
            blacklist_keyword = BlacklistKeyword(
                keyword=keyword,
                strict=strict,
            )
            session.add(blacklist_keyword)
            session.flush()

        keywords[keyword] = blacklist_keyword

    return keywords


# ============================================================
# Transactions
# ============================================================


def create_transactions(session, tags):
    transactions = []

    for _ in range(NUMBER_OF_TRANSACTIONS):
        (
            description,
            transaction_tags,
            minimum,
            maximum,
        ) = random.choice(EXPENSES)

        transaction = Transaction(
            id=random_identifiant(),
            date=random_date(START_DATE, END_DATE),
            type="Purchase",
            description=description,
            card_name="Seed Credit Card",
            account_name="Seed Account",
            amount=random_amount(minimum, maximum),
            direction=TransactionDirection.DEBIT,
            montant_recompense=None,
            taux_recompense=None,
        )

        for tag_name in transaction_tags:
            transaction.tags.append(tags[tag_name])

        transactions.append(transaction)

    # Credits / refunds
    number_of_credits = NUMBER_OF_TRANSACTIONS // 20

    for _ in range(number_of_credits):
        transaction = Transaction(
            id=random_identifiant(),
            date=random_date(START_DATE, END_DATE),
            type="Refund",
            description=random.choice(
                [
                    "Refund",
                    "Purchase Refund",
                    "Credit Card Refund",
                    "Cashback",
                ]
            ),
            card_name="Seed Credit Card",
            account_name="Seed Account",
            amount=random_amount(10, 300),
            direction=TransactionDirection.CREDIT,
            cashback_amount=None,
            cashback_percentage=None,
        )

        transaction.tags.append(tags["Refund"])
        transactions.append(transaction)

    session.add_all(transactions)

    return transactions


# ============================================================
# Main
# ============================================================


def main():
    random.seed(RANDOM_SEED)

    with Session() as session:
        tags = create_tags(session)
        blacklist_keywords = create_blacklist_keywords(session)
        transactions = create_transactions(session, tags)

        session.commit()

        print(f"Created {len(transactions)} transactions.")
        print(f"Created/verified {len(tags)} tags.")
        print(f"Created/verified " f"{len(blacklist_keywords)} blacklist keywords.")


if __name__ == "__main__":
    main()
