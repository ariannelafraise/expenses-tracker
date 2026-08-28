from sqlalchemy import desc, func, select

from database import Session
from models import Tag, Transaction, TransactionDirection


def calculate_daily_spending(filters):
    with Session() as session:
        daily_spending = session.execute(
            select(
                Transaction.date,
                func.sum(Transaction.amount).label("amount"),
            )
            .where(*filters)
            .where(Transaction.direction == TransactionDirection.DEBIT)
            .group_by(Transaction.date)
            .order_by(Transaction.date)
        ).all()

    if not daily_spending:
        return [], []

    daily_dates = [row.date for row in daily_spending]
    daily_amounts = [float(row.amount) for row in daily_spending]
    return daily_dates, daily_amounts


def calculate_monthly_spending(filters):
    with Session() as session:
        return session.execute(
            select(
                func.strftime("%Y-%m", Transaction.date).label("month"),
                func.sum(Transaction.amount).label("amount"),
            )
            .where(*filters)
            .where(Transaction.direction == TransactionDirection.DEBIT)
            .group_by(func.strftime("%Y-%m", Transaction.date))
            .order_by(func.strftime("%Y-%m", Transaction.date))
        ).all()


def calculate_spending_per_tag(filters):
    with Session() as session:
        return session.execute(
            select(
                Tag.name,
                func.sum(Transaction.amount).label("amount"),
            )
            .join(Tag.transactions)
            .where(*filters)
            .where(Transaction.direction == TransactionDirection.DEBIT)
            .group_by(Tag.id, Tag.name)
            .order_by(desc("amount"))
        ).all()


def calculate_general_stats(filters):
    with Session() as session:
        total_transactions = (
            session.scalar(select(func.count(Transaction.id)).where(*filters)) or 0
        )

        debit_total = (
            session.scalar(
                select(func.coalesce(func.sum(Transaction.amount), 0))
                .where(*filters)
                .where(Transaction.direction == TransactionDirection.DEBIT)
            )
            or 0
        )

        credit_total = (
            session.scalar(
                select(func.coalesce(func.sum(Transaction.amount), 0))
                .where(*filters)
                .where(Transaction.direction == TransactionDirection.CREDIT)
            )
            or 0
        )

        average_transaction = (
            session.scalar(
                select(func.coalesce(func.avg(Transaction.amount), 0))
                .where(*filters)
                .where(Transaction.direction == TransactionDirection.DEBIT)
            )
            or 0
        )

        largest_expense = (
            session.scalar(
                select(func.coalesce(func.max(Transaction.amount), 0))
                .where(*filters)
                .where(Transaction.direction == TransactionDirection.DEBIT)
            )
            or 0
        )

        largest_credit = (
            session.scalar(
                select(func.coalesce(func.max(Transaction.amount), 0))
                .where(*filters)
                .where(Transaction.direction == TransactionDirection.CREDIT)
            )
            or 0
        )

        cashback_total = (
            session.scalar(
                select(func.coalesce(func.sum(Transaction.cashback_amount), 0)).where(
                    *filters
                )
            )
            or 0
        )

        return (
            total_transactions,
            debit_total,
            credit_total,
            average_transaction,
            largest_expense,
            largest_credit,
            cashback_total,
        )
