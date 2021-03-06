from __future__ import unicode_literals

from django.db.models import Model, IntegerField, CharField, DateField, ForeignKey, BigIntegerField, CASCADE


class Position(Model):

    name = CharField(max_length=50, unique=True)

    def __unicode__(self):
        return '{0}'.format(self.name)


class Team(Model):

    name = CharField(max_length=200, unique=True)

    def __unicode__(self):
        return '{0}'.format(self.name)


class Season(Model):

    name = CharField(max_length=50, unique=True)

    def __unicode__(self):
        return '{0}'.format(self.name)


class Game(Model):

    home_team = ForeignKey(Team, on_delete=CASCADE, related_name='home_team')
    away_team = ForeignKey(Team, on_delete=CASCADE, related_name='away_team')
    start_date = DateField()
    season = ForeignKey(Season, on_delete=CASCADE)
    nba_id = CharField(max_length=100, unique=True)

    class Meta:
        unique_together = ('home_team', 'away_team', 'start_date', 'season')

    def __unicode__(self):
        return '{0} - {1} - {2} - {3}'.format(self.home_team.name, self.away_team.name, self.start_date, self.season)


class Player(Model):

    name = CharField(max_length=250)
    position = ForeignKey(Position, on_delete=CASCADE)
    team = ForeignKey(Team, on_delete=CASCADE, null=True)
    season = ForeignKey(Season, on_delete=CASCADE)
    jersey_number = IntegerField(null=True)
    nba_id = BigIntegerField()

    class Meta:
        unique_together = ('name', 'team', 'jersey_number', 'nba_id')

    def __unicode__(self):
        return '{0} - {1} - {2} - {3} - {4} - {5}'.format(self.name, self.position, self.team, self.season, self.jersey_number)


class DailyFantasySportsSite(Model):

    name = CharField(max_length=50, unique=True)

    def __unicode__(self):
        return '{0}'.format(self.name)


class PlayerSalary(Model):

    site = ForeignKey(DailyFantasySportsSite, on_delete=CASCADE)
    game = ForeignKey(Game, on_delete=CASCADE)
    player = ForeignKey(Player, on_delete=CASCADE)
    salary = IntegerField()

    class Meta:
        unique_together = ('site', 'game', 'player', 'salary')

    def __unicode__(self):
        return '{0} - {1} - {2} - {3}'.format(self.site, self.game, self.player, self.salary)


class TraditionalBoxScore(Model):

    player = ForeignKey(Player, on_delete=CASCADE)
    game = ForeignKey(Game, on_delete=CASCADE)
    seconds_played = IntegerField(null=True)
    field_goals = IntegerField(null=True)
    field_goal_attempts = IntegerField(null=True)
    three_point_field_goals = IntegerField(null=True)
    three_point_field_goal_attempts = IntegerField(null=True)
    free_throws = IntegerField(null=True)
    free_throw_attempts = IntegerField(null=True)
    offensive_rebounds = IntegerField(null=True)
    defensive_rebounds = IntegerField(null=True)
    assists = IntegerField(null=True)
    steals = IntegerField(null=True)
    blocks = IntegerField(null=True)
    turnovers = IntegerField(null=True)
    fouls_committed = IntegerField(null=True)
    plus_minus = IntegerField(null=True)

    class Meta:
        unique_together = ('player', 'game')

    def __unicode__(self):
        return '{0} - {1}'.format(self.player, self.game)
