from sqlalchemy import select

from database import Session
from models import BlacklistKeyword


def add_blacklist_keyword(keyword, strict):
    keyword = keyword.strip()
    if not keyword:
        return False

    with Session() as session:
        existing_keyword = session.scalar(
            select(BlacklistKeyword).where(BlacklistKeyword.keyword == keyword)
        )
        if existing_keyword:
            return False

        session.add(BlacklistKeyword(keyword=keyword, strict=strict))
        session.commit()

    return True


def get_all_blacklist_keywords():
    with Session() as session:
        return session.scalars(
            select(BlacklistKeyword).order_by(BlacklistKeyword.keyword)
        ).all()


def delete_blacklist_keyword(keyword_id):
    with Session() as session:
        keyword = session.get(BlacklistKeyword, keyword_id)
        if keyword is None:
            return False

        session.delete(keyword)
        session.commit()

    return True
