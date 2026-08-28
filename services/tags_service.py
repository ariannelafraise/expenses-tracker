from sqlalchemy import select

from database import Session
from models import Tag


def add_tag(name):
    with Session() as session:
        if session.scalar(select(Tag).where(Tag.name == name)):
            return False

        session.add(Tag(name=name))
        session.commit()
        return True


def get_all_tags():
    with Session() as session:
        return session.scalars(select(Tag).order_by(Tag.name)).all()


def delete_tag(tag_id):
    with Session() as session:
        tag = session.get(Tag, tag_id)

        if tag is None:
            return

        session.delete(tag)
        session.commit()


def get_all_tags_names():
    with Session() as session:
        tags = session.scalars(select(Tag).order_by(Tag.name)).all()
        return [tag.name for tag in tags]
