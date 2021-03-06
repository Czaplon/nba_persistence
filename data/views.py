from datetime import datetime

from pytz import utc
from rest_framework.viewsets import ReadOnlyModelViewSet

from data.models import Team, Position, Season, Game, Player, TraditionalBoxScore, PlayerSalary, DailyFantasySportsSite
from data.serializers import TeamSerializer, PositionSerializer, SeasonSerializer, GameSerializer, PlayerSerializer, BoxScoreSerializer, PlayerSalarySerializer, DailyFantasySportsSiteSerializer


# Create your views here.


class TeamViewSet(ReadOnlyModelViewSet):
    serializer_class = TeamSerializer

    def get_queryset(self):
        queryset = Team.objects.all().order_by('name')
        abbreviation = self.request.query_params.get('abbreviation', None)
        if abbreviation is not None:
            queryset = queryset.filter(abbreviation=abbreviation)

        return queryset


class PositionViewSet(ReadOnlyModelViewSet):
    serializer_class = PositionSerializer

    def get_queryset(self):
        queryset = Position.objects.all().order_by('name')
        abbreviation = self.request.query_params.get('abbreviation', None)
        if abbreviation is not None:
            queryset = queryset.filter(abbreviation=abbreviation)
        return queryset


class SeasonViewSet(ReadOnlyModelViewSet):
    queryset = Season.objects.all().order_by('-start_year')
    serializer_class = SeasonSerializer


class GameViewSet(ReadOnlyModelViewSet):
    serializer_class = GameSerializer

    def get_queryset(self):
        queryset = Game.objects.all().order_by('start_time')
        home_team_abbreviation = self.request.query_params.get('home_team_abbreviation', None)
        away_team_abbreviation = self.request.query_params.get('away_team_abbreviation', None)
        unix_start_time = self.request.query_params.get('unix_start_time', None)
        unix_end_time = self.request.query_params.get('unix_end_time', None)
        season_start_year = self.request.query_params.get('season_start_year', None)
        if home_team_abbreviation is not None:
            queryset = queryset.filter(home_team__abbreviation=home_team_abbreviation)

        if away_team_abbreviation is not None:
            queryset = queryset.filter(away_team__abbreviation=away_team_abbreviation)

        if unix_start_time is not None:
            queryset = queryset.filter(start_time__gte=datetime.fromtimestamp(float(unix_start_time), utc))

        if unix_end_time is not None:
            queryset = queryset.filter(start_time__lte=datetime.fromtimestamp(float(unix_end_time), utc))

        if season_start_year is not None:
            queryset = queryset.filter(season__start_year=season_start_year)

        return queryset


class PlayerViewSet(ReadOnlyModelViewSet):
    serializer_class = PlayerSerializer

    def get_queryset(self):
        queryset = Player.objects.all().order_by('first_name').order_by('last_name')
        first_name = self.request.query_params.get('first_name', None)
        last_name = self.request.query_params.get('last_name', None)
        team_abbreviation = self.request.query_params.get('team_abbreviation', None)
        position_abbreviation = self.request.query_params.get('position_abbreviation', None)
        if first_name is not None:
            queryset = queryset.filter(first_name=first_name)

        if last_name is not None:
            queryset = queryset.filter(last_name=last_name)

        if team_abbreviation is not None:
            queryset = queryset.filter(team__abbreviation=team_abbreviation)

        if position_abbreviation is not None:
            queryset = queryset.filter(position__abbreviation=position_abbreviation)

        return queryset


class BoxScoreViewSet(ReadOnlyModelViewSet):
    serializer_class = BoxScoreSerializer

    def get_queryset(self):
        queryset = TraditionalBoxScore.objects.all().order_by('player__last_name').order_by('player__first_name').order_by('-game__start_time')
        first_name = self.request.query_params.get('first_name', None)
        last_name = self.request.query_params.get('last_name', None)
        team_abbreviation = self.request.query_params.get('team_abbreviation', None)
        unix_start_time = self.request.query_params.get('unix_start_time', None)
        unix_end_time = self.request.query_params.get('unix_end_time', None)

        if first_name is not None:
            queryset = queryset.filter(player__first_name=first_name)

        if last_name is not None:
            queryset = queryset.filter(player__last_name=last_name)

        if team_abbreviation is not None:
            queryset = queryset.filter(team__abbreviation=team_abbreviation)

        if unix_start_time is not None:
            queryset = queryset.filter(game__start_time__gte=datetime.fromtimestamp(float(unix_start_time), utc))

        if unix_end_time is not None:
            queryset = queryset.filter(game__start_time__lte=datetime.fromtimestamp(float(unix_end_time), utc))

        return queryset


class PlayerSalaryViewSet(ReadOnlyModelViewSet):
    serializer_class = PlayerSalarySerializer

    def get_queryset(self):
        queryset = PlayerSalary.objects.all().order_by('site__name').order_by('-salary').order_by('-game__start_time')
        salary_min = self.request.query_params.get('salary_min', None)
        salary_max = self.request.query_params.get('salary_max', None)
        position_abbreviation = self.request.query_params.get('position_abbreviation', None)
        site_name = self.request.query_params.get('site_name', None)
        unix_start_time = self.request.query_params.get('unix_start_time', None)
        unix_end_time = self.request.query_params.get('unix_end_time', None)

        if salary_min is not None:
            queryset = queryset.filter(salary__gte=salary_min)

        if salary_max is not None:
            queryset = queryset.filter(salary__lte=salary_max)

        if position_abbreviation is not None:
            queryset = queryset.filter(player__position__abbreviation=position_abbreviation)

        if site_name is not None:
            queryset = queryset.filter(site__name=site_name)

        if unix_start_time is not None:
            queryset = queryset.filter(game__start_time__gte=datetime.fromtimestamp(float(unix_start_time), utc))

        if unix_end_time is not None:
            queryset = queryset.filter(game__start_time__lte=datetime.fromtimestamp(float(unix_end_time), utc))

        return queryset


class DailyFantasySportsSiteViewSet(ReadOnlyModelViewSet):
    serializer_class = DailyFantasySportsSiteSerializer

    def get_queryset(self):
        queryset = DailyFantasySportsSite.objects.all().order_by('name')
        name = self.request.query_params.get('name', None)

        if name is not None:
            queryset = queryset.filter(name=name)

        return queryset