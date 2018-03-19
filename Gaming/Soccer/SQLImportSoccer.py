import pandas as pd
from sqlalchemy import create_engine, MetaData, insert, select
import requests
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, Date
import math
from datetime import datetime

# Create an engine that connects to the census.sqlite file: engine
engine = create_engine('sqlite:///MySoccer.sqlite')
metadata = MetaData()
metadata.drop_all(engine)
# metadata.clear()
print(engine.table_names())

connection = engine.connect()

league = Table('League', metadata, autoload=True, autoload_with=engine)
group = Table('GameGroup', metadata, autoload=True, autoload_with=engine)
resultType = Table('ResultType', metadata, autoload=True, autoload_with=engine)
match = Table('Match', metadata, autoload=True, autoload_with=engine)
match_result = Table('MatchResult', metadata, autoload=True, autoload_with=engine)
team = Table('Team', metadata, autoload=True, autoload_with=engine)
match_team = Table('MatchTeam', metadata, autoload=True, autoload_with=engine)
player = Table('Player', metadata, autoload=True, autoload_with=engine)
goal = Table('Goal', metadata, autoload=True, autoload_with=engine)
location = Table('Location', metadata, autoload=True, autoload_with=engine)

# print(repr(match))

# Assign URL to variable: url - bl/2011 - 2017 available
url = 'https://www.openligadb.de/api/getmatchdata/bl1/2016'

# Package the request, send the request and catch the response: r
r = requests.get(url)

# Decode the JSON data into a dictionary: json_data
json_data = r.json()

# print(json_data)


def get_number_table_records_by_id(table: Table, id: Integer):
    stmt = select([table])
    if table.name == 'GameGroup':
        stmt = stmt.where(table.c.GroupId == id)
    elif table.name == 'Goal':
        stmt = stmt.where(table.c.GoalId == id)
    elif table.name == 'League':
        stmt = stmt.where(table.c.LeagueId == id)
    elif table.name == 'Location':
        stmt = stmt.where(table.c.LocationId == id)
    elif table.name == 'Match':
        stmt = stmt.where(table.c.MatchId == id)
    elif table.name == 'MatchResult':
        stmt = stmt.where(table.c.ResultId == id)
    elif table.name == 'Player':
        stmt = stmt.where(table.c.PlayerId == id)
    elif table.name == 'ResultType':
        stmt = stmt.where(table.c.ResultTypeId == id)
    elif table.name == 'Team':
        stmt = stmt.where(table.c.TeamId == id)
    return len(connection.execute(stmt).fetchall())

def insert_values(table: Table, insert_dic):
    stmt = insert(table)
    results = connection.execute(stmt, insert_dic)
    print('Inserted into table {}: {} record(s)'.format(table.name, results.rowcount))
    return results.rowcount

for dictionaries in json_data:
    insert_dic = {}
    match_id = dictionaries["MatchID"]

    if get_number_table_records_by_id(match, match_id) != 0:  # create match
        continue

    league_id = dictionaries["LeagueId"]

    if get_number_table_records_by_id(league, league_id) == 0:  # create league
        insert_dic = {}
        insert_dic['LeagueId'] = league_id
        insert_dic['LeagueName'] = dictionaries["LeagueName"]
        print('Creating League: {} - {}'.format(league_id, insert_dic['LeagueName']))
        insert_values(league, insert_dic)

    group_dic = dictionaries["Group"]
    group_id = group_dic['GroupID']
    if get_number_table_records_by_id(group, group_id) == 0:  # create group
        insert_dic = {}
        insert_dic['GroupId'] = group_id
        insert_dic['GroupName'] = group_dic['GroupName']
        insert_dic['GroupOrderId'] = group_dic['GroupOrderID']
        print('Creating Group: {} - {} - {}'.format(group_id, insert_dic['GroupName'], insert_dic['GroupOrderId']))
        insert_values(group, insert_dic)

    location_id = None
    location_dic = dictionaries["Location"]
    if location_dic != None:
        location_id = location_dic['LocationID']
        if get_number_table_records_by_id(location, location_id) == 0:  # create league
            insert_dic = {}
            insert_dic['LocationId'] = location_id
            insert_dic['LocationCity'] = location_dic['LocationCity']
            insert_dic['LocationStadium'] = location_dic['LocationStadium']
            print('Creating Location: {} - {} - {}'.format(location_id, insert_dic['LocationCity'],
                                                           insert_dic['LocationStadium']))
            insert_values(location, insert_dic)

    # match_date = datetime.strptime(dictionaries["MatchDateTime"], '%Y-%m-%d') '2017-09-20T19:49:26.917'
    match_date = datetime.strptime(dictionaries["MatchDateTime"][:10], '%Y-%m-%d')
    insert_dic = {}
    insert_dic['MatchId'] = match_id
    insert_dic['MatchDateTime'] = match_date
    insert_dic['LeagueId'] = league_id
    insert_dic['GroupId'] = group_id
    insert_dic['LocationId'] = location_id
    if dictionaries["NumberOfViewers"] == None: insert_dic['NumberOfViewers'] = 0
    else: insert_dic['NumberOfViewers'] = dictionaries["NumberOfViewers"]
    print('Creating match: {}'.format(match_id))
    insert_values(match, insert_dic)

    team_dic_list = [dictionaries["Team1"], dictionaries["Team2"]]
    for index, team1_dic in enumerate(team_dic_list):
        team_id = team1_dic['TeamId']
        if get_number_table_records_by_id(team, team_id) == 0:  # create team
            insert_dic = {}
            insert_dic['TeamId'] = team_id
            insert_dic['TeamName'] = team1_dic['TeamName']
            insert_dic['ShortName'] = team1_dic['ShortName']
            print('Creating Team: {} - {} - {}'.format(team_id, insert_dic['TeamName'], insert_dic['ShortName']))
            insert_values(team, insert_dic)

        insert_dic = {}
        insert_dic['MatchId'] = match_id
        insert_dic['TeamId'] = team_id
        insert_dic['IsHomeTeam'] = (index == 0)
        print('Creating Match-Team: Match={} Team={} - IsHome={}'.format(insert_dic['MatchId'], insert_dic['TeamId'], insert_dic['IsHomeTeam']))
        insert_values(match_team, insert_dic)

    match_results_dic_list = dictionaries["MatchResults"]

    for match_results_dics in match_results_dic_list:
        result_type_id = match_results_dics['ResultTypeID']
        if get_number_table_records_by_id(resultType, result_type_id) == 0:
            insert_dic = {}
            insert_dic['ResultTypeId'] = result_type_id
            insert_dic['ResultName'] = match_results_dics['ResultName']
            insert_dic['ResultDescription'] = match_results_dics['ResultDescription']
            insert_dic['ResultOrderId'] = match_results_dics['ResultOrderID']
            print('Creating ResultType: {} - {}'.format(result_type_id, insert_dic['ResultName']))
            insert_values(resultType, insert_dic)

        result_id = match_results_dics['ResultID']
        if get_number_table_records_by_id(match_result, result_id) == 0:
            insert_dic = {}
            insert_dic['ResultId'] = result_id
            insert_dic['ResultTypeId'] = result_type_id
            insert_dic['MatchId'] = match_id
            insert_dic['PointsTeam1'] = match_results_dics['PointsTeam1']
            insert_dic['PointsTeam2'] = match_results_dics['PointsTeam2']
            print('Creating MatchResults: {}/{} - {}:{}'.format(result_id, result_type_id, insert_dic['PointsTeam1'], insert_dic['PointsTeam2']))
            insert_values(match_result, insert_dic)

    goals_dic_list = dictionaries["Goals"]
    for goals_dics in goals_dic_list:
        player_id = goals_dics['GoalGetterID']
        if get_number_table_records_by_id(player, player_id) == 0:
            insert_dic = {}
            insert_dic['PlayerId'] = player_id
            insert_dic['PlayerName'] = goals_dics['GoalGetterName']
            print('Creating Player: id={} {}'.format(player_id, insert_dic['PlayerId']))
            insert_values(player, insert_dic)

        goal_id = goals_dics['GoalID']
        if get_number_table_records_by_id(goal, goal_id) == 0:
            insert_dic = {}
            insert_dic['GoalId'] = goal_id
            insert_dic['MatchId'] = match_id
            insert_dic['PlayerId'] = player_id
            insert_dic['ScoreTeam1'] = goals_dics['ScoreTeam1']
            insert_dic['ScoreTeam2'] = goals_dics['ScoreTeam2']
            insert_dic['MatchMinute'] = goals_dics['MatchMinute']
            insert_dic['IsPenalty'] = goals_dics['IsPenalty']
            insert_dic['IsOwnGoal'] = goals_dics['IsOwnGoal']
            insert_dic['IsOvertime'] = goals_dics['IsOvertime']
            print('Creating Goals: id={} {}:{}, minute: {}, penalty={}, own_goal={}, overtime={}'
                  .format(goal_id, insert_dic['ScoreTeam1'], insert_dic['ScoreTeam2'], insert_dic['MatchMinute'],
                          insert_dic['IsPenalty'], insert_dic['IsOwnGoal'], insert_dic['IsOvertime']))
            insert_values(goal, insert_dic)

connection.close()
