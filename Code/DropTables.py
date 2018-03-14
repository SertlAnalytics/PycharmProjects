import pandas as pd
from sqlalchemy import create_engine, MetaData, insert, select
import requests
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, Date, ForeignKey
import math
from datetime import datetime
from sqlalchemy.orm import sessionmaker

# Create an engine that connects to the census.sqlite file: engine
engine = create_engine('sqlite:///MySoccer.sqlite')
Session = sessionmaker(bind=engine)
session = Session()
session.commit()
metadata = MetaData()
print(engine.table_names())

# match_team_table = Table('MatchTeam', metadata, autoload=True, autoload_with=engine)
#
# match_team_table.drop(engine)

match_table = Table('Match', metadata, autoload=True, autoload_with=engine)
team_table = Table('Team', metadata, autoload=True, autoload_with=engine)

print(engine.table_names())

# Define a MatchTeam table
data = Table('MatchTeam', metadata,
    Column('MatchId', Integer(), ForeignKey('Match.MatchId'), primary_key=True),
    Column('TeamId', Integer(), ForeignKey('Team.TeamId'), primary_key=True),
    Column('IsHomeTeam', Boolean())
)

metadata.create_all(engine)


# league_table = Table('League', metadata, autoload=True, autoload_with=engine)
# group_table = Table('Group', metadata, autoload=True, autoload_with=engine)
# resultType_table = Table('ResultType', metadata, autoload=True, autoload_with=engine)
# match_table = Table('Match', metadata, autoload=True, autoload_with=engine)
# match_result_table = Table('MatchResult', metadata, autoload=True, autoload_with=engine)
# team_table = Table('Team', metadata, autoload=True, autoload_with=engine)
# match_team_table = Table('MatchTeam', metadata, autoload=True, autoload_with=engine)
# player_table = Table('Player', metadata, autoload=True, autoload_with=engine)
# goal_table = Table('Goal', metadata, autoload=True, autoload_with=engine)
# location_table = Table('Location', metadata, autoload=True, autoload_with=engine)

# league_table.drop(engine)
# group_table.drop(engine)
# resultType_table.drop(engine)
# match_result_table.drop(engine)
# team_table.drop(engine)
# match_team_table.drop(engine)
# player_table.drop(engine)
# goal_table.drop(engine)
# location_table.drop(engine)

# Print table names
print(engine.table_names())

