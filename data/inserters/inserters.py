import csv
import os
from datetime import datetime, timedelta

from basketball_reference_web_scraper.readers import return_schedule, return_all_player_season_statistics, return_box_scores_for_date
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from pytz import timezone, utc

from data.dfs_sites.sites import sites as dfs_sites
from data.models import Position, Team, Season, Game, Player, BoxScore, DailyFantasySportsSite, PlayerSalary
from utils import draftkings_salary_team_abbreviation_converter, fanduel_salary_team_abbreviation_converter, draftkings_player_name_converter, fanduel_player_name_converter


def insert_positions(positions):
    for position in positions:
        if 'name' in position or 'abbreviation' in position:
            Position.objects.update_or_create(name=position['name'], abbreviation=position['abbreviation'])
        else:
            raise ValueError('position must have both name and abbreviation')


def insert_teams(teams):
    for team in teams:
        if 'name' in team or 'abbreviation' in team:
            Team.objects.update_or_create(name=team['name'], abbreviation=team['abbreviation'])
        else:
            raise ValueError('team must have both name and abbreviation')


def insert_schedules(first_season_start_year, last_season_start_year):
    for season_start_year in range(first_season_start_year, last_season_start_year + 1):
        season, created = Season.objects.get_or_create(start_year=season_start_year)
        season_schedule = return_schedule(season_start_year)
        for event in season_schedule.parsed_event_list:
            home_team = Team.objects.get(name=event.home_team_name)
            away_team = Team.objects.get(name=event.visiting_team_name)
            Game.objects.update_or_create(home_team=home_team, away_team=away_team, start_time=event.start_time, season=season)


def insert_players(season_start_year):
    player_season_statistics = return_all_player_season_statistics(season_start_year=season_start_year)
    for player_season in player_season_statistics:
        team = Team.objects.get(abbreviation=player_season.team)
        if player_season.position == 'G':
            player_position = 'PG'
        elif player_season.position == 'F':
            player_position = 'SF'
        elif '-' in player_season.position:
            player_position = 'PG'
        else:
            player_position = player_season.position
        position = Position.objects.get(abbreviation=player_position)
        Player.objects.update_or_create(first_name=player_season.first_name, last_name=player_season.last_name, team=team, position=position)


def insert_box_score(box_score):
    day_start_est = timezone('US/Eastern').localize(datetime(year=box_score.date.year, month=box_score.date.month, day=box_score.date.day, hour=0, minute=0, second=0, microsecond=0))
    day_end_est = day_start_est + timedelta(hours=24)
    day_start_utc = day_start_est.astimezone(utc)
    day_end_utc = day_end_est.astimezone(utc)
    try:
        team = Team.objects.get(abbreviation=box_score.team)
        opponent = Team.objects.get(abbreviation=box_score.opponent)
        player = Player.objects.filter(first_name=box_score.first_name).filter(last_name=box_score.last_name).get(team=team)
        game = Game.objects.filter((Q(home_team=team) & Q(away_team=opponent)) | (Q(home_team=opponent) & Q(away_team=team))).filter(start_time__gte=day_start_utc).get(start_time__lte=day_end_utc)
        BoxScore.objects.update_or_create(
            player=player,
            game=game,
            seconds_played=box_score.seconds_played,
            field_goals=box_score.field_goals,
            field_goal_attempts=box_score.field_goal_attempts,
            three_point_field_goals=box_score.three_point_field_goals,
            three_point_field_goal_attempts=box_score.three_point_field_goal_attempts,
            free_throws=box_score.free_throws,
            free_throw_attempts=box_score.free_throw_attempts,
            offensive_rebounds=box_score.offensive_rebounds,
            defensive_rebounds=box_score.defensive_rebounds,
            total_rebounds=box_score.total_rebounds,
            assists=box_score.assists,
            steals=box_score.steals,
            blocks=box_score.blocks,
            turnovers=box_score.turnovers,
            fouls_committed=box_score.personal_fouls,
            points=box_score.points,
            draftkings_points=float(box_score.points) + float(box_score.three_point_field_goals) * 0.5 + float(box_score.total_rebounds) * 1.25 + float(box_score.assists) * 1.5 + float(box_score.steals) * 2 + float(box_score.blocks) * 2 - float(box_score.turnovers) * 0.5
        )
    except ObjectDoesNotExist:
        pass


def insert_box_scores(minimum_date, maximum_date):
    games = Game.objects.filter(start_time__gte=minimum_date).filter(start_time__lte=maximum_date).filter(boxscore__isnull=True)
    distinct_start_days = set()
    for game in games:
        distinct_start_days.add(game.start_time.replace(tzinfo=timezone('US/Eastern')).date())
    for start_day in distinct_start_days:
        box_scores = return_box_scores_for_date(start_day)
        for box_score in box_scores:
            insert_box_score(box_score)


def insert_daily_fantasy_sports_sites():
    for site in dfs_sites:
        DailyFantasySportsSite.objects.update_or_create(name=site['name'])


def insert_draftkings_salaries(day):
    draftkings_file_name = os.path.join(os.path.dirname(__file__), "static/salaries/draftkings/{0}.csv".format(day.strftime("%Y-%m-%d")))
    draftkings_log_file_name = os.path.join(os.path.dirname(__file__), "static/salaries/draftkings.log")
    if os.path.isfile(draftkings_file_name):
        log_file = open(draftkings_log_file_name, "a+")
        with open(draftkings_file_name) as file:
            reader = csv.reader(file)
            salaries = list(reader)[1:]
            site = DailyFantasySportsSite.objects.get(name="DraftKings")
            for salary in salaries:
                names_list = salary[1].split(" ")
                first_name = names_list[0]
                last_name = names_list[1]
                converted_names = draftkings_player_name_converter(first_name, last_name)
                first_name = converted_names['first_name']
                last_name = converted_names['last_name']
                game_info_list = salary[3].split(" ")
                team_abbreviation_list = game_info_list[0].split("@")
                away_team_abbreviation = draftkings_salary_team_abbreviation_converter(team_abbreviation_list[0])
                home_team_abbreviation = draftkings_salary_team_abbreviation_converter(team_abbreviation_list[1])
                start_time = game_info_list[1]
                utc_start_time = timezone("US/Eastern").localize(datetime.strptime("{0}-{1}-{2}-{3}".format(day.year, day.month, day.day, start_time), "%Y-%m-%d-%I:%M%p")).astimezone(utc)
                player_team_abbreviation = draftkings_salary_team_abbreviation_converter(salary[5].upper())
                try:
                    player = Player.objects.get(first_name=first_name, last_name=last_name, team__abbreviation=player_team_abbreviation)
                    game = Game.objects.get(home_team__abbreviation=home_team_abbreviation, away_team__abbreviation=away_team_abbreviation, start_time=utc_start_time)
                    salary_value = salary[2]
                    PlayerSalary.objects.update_or_create(site=site, player=player, game=game, salary=salary_value)
                except ObjectDoesNotExist:
                    log_message = "{0} - {1} - {2} - {3}\n".format(first_name, last_name, player_team_abbreviation, utc_start_time)
                    log_file.write(log_message)
        log_file.close()


def insert_fanduel_salaries(day):
    fanduel_file_name = os.path.join(os.path.dirname(__file__), "static/salaries/fanduel/{0}.csv".format(day.strftime("%Y-%m-%d")))
    fanduel_log_file_name = os.path.join(os.path.dirname(__file__), "static/salaries/fanduel.log")
    if os.path.isfile(fanduel_file_name):
        log_file = open(fanduel_log_file_name, "a+")
        with open(fanduel_file_name) as file:
            reader = csv.reader(file)
            salaries = list(reader)[1:]
            site = DailyFantasySportsSite.objects.get(name="FanDuel")
            for salary in salaries:
                first_name = salary[2]
                last_name = salary[3]
                converted_names = fanduel_player_name_converter(first_name, last_name)
                first_name = converted_names['first_name']
                last_name = converted_names['last_name']
                game_info_list = salary[7].split("@")
                away_team_abbreviation = fanduel_salary_team_abbreviation_converter(game_info_list[0])
                home_team_abbreviation = fanduel_salary_team_abbreviation_converter(game_info_list[1])
                player_team_abbreviation = fanduel_salary_team_abbreviation_converter(salary[8].upper())
                day_start_est = timezone('US/Eastern').localize(datetime(year=day.year, month=day.month, day=day.day, hour=0, minute=0, second=0, microsecond=0))
                day_end_est = day_start_est + timedelta(hours=24)
                try:
                    player = Player.objects.get(first_name=first_name, last_name=last_name, team__abbreviation=player_team_abbreviation)
                    game = Game.objects.get(home_team__abbreviation=home_team_abbreviation, away_team__abbreviation=away_team_abbreviation, start_time__gte=day_start_est, start_time__lte=day_end_est)
                    salary_value = salary[6]
                    PlayerSalary.objects.update_or_create(site=site, player=player, game=game, salary=salary_value)
                except ObjectDoesNotExist:
                    log_message = "{0} - {1} - {2} - {3} - {4}\n".format(first_name, last_name, player_team_abbreviation, day_start_est, day_end_est)
                    log_file.write(log_message)
        log_file.close()


def insert_dfs_salaries(start_date, end_date):
    day = start_date
    while day <= end_date:
        insert_draftkings_salaries(day)
        insert_fanduel_salaries(day)
        day = day + timedelta(days=1)