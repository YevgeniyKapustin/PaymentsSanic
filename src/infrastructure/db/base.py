import re

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

from src.infrastructure.db.db_types import TYPE_ANNOTATION_MAP

NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


def _camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map = TYPE_ANNOTATION_MAP

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return _camel_to_snake(cls.__name__)
