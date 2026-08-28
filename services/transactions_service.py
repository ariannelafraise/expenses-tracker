import json
from datetime import datetime
from decimal import Decimal
import hashlib

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from database import Session
from models import Transaction, Tag, TransactionDirection, BlacklistKeyword


def delete_transaction(transaction_id: str):
    with Session() as session:
        transaction = session.get(Transaction, transaction_id)

        if transaction is None:
            return False

        session.delete(transaction)
        session.commit()
        return True


def get_transaction(transaction_id: str):
    with Session() as session:
        return session.scalar(
            select(Transaction).where(Transaction.id == transaction_id)
        )


def update_transaction_tags(transaction_id, selected_tag_names):
    with Session() as session:
        transaction = session.scalar(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        if transaction is None:
            return

        tags = session.scalars(
            select(Tag).where(Tag.name.in_(selected_tag_names))
        ).all()
        transaction.tags = list(tags)
        session.commit()


def get_min_max_dates():
    with Session() as session:
        min_date = session.scalar(select(func.min(Transaction.date)))
        max_date = session.scalar(select(func.max(Transaction.date)))
        return min_date, max_date


def get_all_transactions(filters, offset, page_size):
    query = (
        select(Transaction)
        .options(selectinload(Transaction.tags))
        .where(*filters)
        .order_by(
            Transaction.date.desc(),
            Transaction.id.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    with Session() as session:
        return session.scalars(query).unique().all()


def import_from_json_file(uploaded_file):
    imported = 0
    skipped = 0
    errors = 0

    content = uploaded_file.getvalue()
    data = json.loads(content.decode("utf-8-sig"))

    transaction_list = data.get("sectionFactureeCaisse", {}).get("transactionListe", [])

    transactions = []

    with Session() as session:
        blacklist_keywords = session.scalars(select(BlacklistKeyword)).all()

        blacklisted_keywords = [
            keyword.keyword.lower() for keyword in blacklist_keywords
        ]

        for transaction_data in transaction_list:
            identifiant = hashlib.sha256(
                "|".join(
                    [
                        transaction_data.get("numeroSequence", ""),
                        transaction_data.get("dateTransaction", ""),
                        transaction_data.get("montantTransaction", ""),
                        transaction_data.get("descriptionCourte", ""),
                    ]
                ).encode("utf-8")
            ).hexdigest()

            if not identifiant:
                skipped += 1
                continue

            # Skip transactions that already exist
            if session.get(Transaction, identifiant) is not None:
                skipped += 1
                continue

            date_value = transaction_data.get("dateTransaction")
            description = transaction_data.get("descriptionSimplifiee")
            amount_value = transaction_data.get("montantTransactionNormalise")

            if not date_value or not description or not amount_value:
                skipped += 1
                continue

            # Skip blacklisted descriptions
            if any(keyword in description.lower() for keyword in blacklisted_keywords):
                skipped += 1
                continue

            try:
                transaction_date = datetime.fromisoformat(date_value).date()
            except:
                errors += 1
                continue

            try:
                normalized_amount = Decimal(amount_value)
            except:
                errors += 1
                continue

            transaction_direction = (
                TransactionDirection.CREDIT
                if normalized_amount >= 0
                else TransactionDirection.DEBIT
            )

            amount = abs(normalized_amount)

            try:
                reward_amount = (
                    Decimal(transaction_data["montantRecompense"])
                    if transaction_data.get("montantRecompense")
                    else None
                )
                reward_rate = (
                    Decimal(transaction_data["tauxProgrammeRecompense"])
                    if transaction_data.get("tauxProgrammeRecompense")
                    else None
                )
            except:
                errors += 1
                continue

            transactions.append(
                Transaction(
                    id=identifiant,
                    date=transaction_date,
                    type=transaction_data.get("typeTransaction", ""),
                    description=description,
                    card_name=transaction_data.get("descriptionCarteCourte"),
                    account_name=transaction_data.get("descriptionCompteLC"),
                    amount=amount,
                    direction=transaction_direction,
                    cashback_amount=reward_amount,
                    cashback_percentage=reward_rate,
                )
            )

        if transactions:
            if errors > 0:
                session.rollback()
            else:
                session.add_all(transactions)
                session.commit()
                imported += len(transactions)

    return imported, skipped, errors
