from datetime import datetime

from django.core.management.base import BaseCommand
from pytz import timezone

from data.inserters import insert_daily_fantasy_sports_sites, insert_dfs_salaries


class Command(BaseCommand):
    def handle(self, *args, **options):
        insert_daily_fantasy_sports_sites()
        insert_dfs_salaries(
            start_date=timezone('US/Eastern').localize(datetime(year=2016, month=01, day=03)),
            end_date=timezone('US/Eastern').localize(datetime.now())
        )