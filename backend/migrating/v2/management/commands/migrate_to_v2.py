import json
import os
import sys
from datetime import datetime

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from sqlalchemy import create_engine, text

from migrating.v2.utils.migrate_utils import (
    get_all_tables,
    get_column_names,
    get_table_data,
)


class Command(BaseCommand):
    help = "Migrate data from v1 to v2"

    def add_arguments(self, parser):
        parser.add_argument(
            "--table",
            type=str,
            help="Table to migrate",
        )

    def handle(self, *args, **options):
        table = options.get("table")
        if table:
            self.migrate_table(table)
        else:
            self.migrate_all_tables()

    def migrate_all_tables(self):
        tables = get_all_tables()
        for table in tables:
            self.migrate_table(table)

    def migrate_table(self, table):
        self.stdout.write(self.style.SUCCESS(f"Migrating {table}"))
        data = get_table_data(table)
        if not data:
            self.stdout.write(self.style.WARNING(f"No data found for {table}"))
            return
        df = pd.DataFrame(data)
        df.to_csv(f"{settings.BASE_DIR}/migrating/v2/data/{table}.csv", index=False)
        self.stdout.write(
            self.style.SUCCESS(f"Migrated {table} to {table}.csv successfully")
        )

    def update_table(self, table_name, column_name, id, value):
        """
        Update a table with the given value
        """
        engine = create_engine(
            f"postgresql://{settings.DATABASES['default']['USER']}:{settings.DATABASES['default']['PASSWORD']}@{settings.DATABASES['default']['HOST']}:{settings.DATABASES['default']['PORT']}/{settings.DATABASES['default']['NAME']}"
        )
        try:
            # Using parameterized query with SQLAlchemy text() to prevent SQL injection
            query = text(f"UPDATE {table_name} SET {column_name} = :value WHERE id = :id")
            engine.execute(query, value=value, id=id)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated {table_name} with {column_name} = {value} where id = {id}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating {table_name}: {e}"))
