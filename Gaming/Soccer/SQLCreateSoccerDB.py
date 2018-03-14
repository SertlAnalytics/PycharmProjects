import pandas as pd
from sqlalchemy import func
from sqlalchemy import create_engine, MetaData
import requests
# Import Table, Column, String, Integer, Float, Boolean from sqlalchemy
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, Date, ForeignKey

# Create an engine that connects to the census.sqlite file: engine
engine = create_engine('sqlite:///MySoccer.sqlite')

metadata = MetaData()

# Print table names
print(engine.table_names())

# Define a League table
data = Table('League', metadata,
    Column('LeagueId', Integer(), primary_key=True),
    Column('LeagueName', String(100), nullable=False),
)

metadata.create_all(engine)

# Define a Group table
data = Table('GameGroup', metadata,
    Column('GroupId', Integer(), primary_key=True),
    Column('GroupName', String(50)),
    Column('GroupOrderId', Integer())
)

metadata.create_all(engine)

# Define a ResultType table - 1=First half, 2=Final result
data = Table('ResultType', metadata,
    Column('ResultTypeId', Integer(), primary_key=True),
    Column('ResultName', String(100)),
    Column('ResultDescription', String(100)),
    Column('ResultOrderId', Integer())
)

metadata.create_all(engine)

# Define a Location table
data = Table('Location', metadata,
    Column('LocationId', Integer(), primary_key=True),
    Column('LocationCity', String(100)),
    Column('LocationStadium', String(100))
)

metadata.create_all(engine)

# Define a Match table
data = Table('Match', metadata,
    Column('MatchId', Integer(), primary_key=True),
    Column('MatchDateTime', Date()),
    Column('LeagueId', Integer(), ForeignKey('League.LeagueId'), nullable=False),
    Column('GroupId', Integer(), ForeignKey('GameGroup.GroupId'), nullable=False),
    Column('LocationId', Integer(), ForeignKey('Location.LocationId'), nullable=True),
    Column('NumberOfViewers', Integer())
)

metadata.create_all(engine)

# Define a MatchResults table
data = Table('MatchResult', metadata,
    Column('ResultId', Integer(), primary_key=True),
    Column('ResultTypeId', Integer(), ForeignKey('ResultType.ResultTypeId'), nullable=False),
    Column('MatchId', Integer(), ForeignKey('Match.MatchId'), nullable=False),
    Column('PointsTeam1', Integer()),
    Column('PointsTeam2', Integer())
)

metadata.create_all(engine)

# Define a Team table
data = Table('Team', metadata,
    Column('TeamId', Integer(), primary_key=True),
    Column('TeamName', String(100)),
    Column('ShortName', String(100), nullable=False),
)

metadata.create_all(engine)

# Define a MatchTeam table
data = Table('MatchTeam', metadata,
    Column('MatchId', Integer(), ForeignKey('Match.MatchId'), primary_key=True),
    Column('TeamId', Integer(), ForeignKey('Team.TeamId'), primary_key=True),
    Column('IsHomeTeam', Boolean())
)

metadata.create_all(engine)

# Define a Player table
data = Table('Player', metadata,
    Column('PlayerId', Integer(), primary_key=True),
    Column('PlayerName', String(100))
)

metadata.create_all(engine)

# Define a Goal table
data = Table('Goal', metadata,
    Column('GoalId', Integer(), primary_key=True),
    Column('MatchId', Integer(), ForeignKey('Match.MatchId')),
    Column('PlayerId', Integer(), ForeignKey('Player.PlayerId')),
    Column('ScoreTeam1', Integer()),
    Column('ScoreTeam2', Integer()),
    Column('MatchMinute', Integer()),
    Column('IsPenalty', Boolean()),
    Column('IsOwnGoal', Boolean()),
    Column('IsOvertime', Boolean())
)

metadata.create_all(engine)

# Print table details
print(repr(data))



