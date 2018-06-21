"""
Description: This module contains all constants used for the FIFA world cup predictor
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""


class FC:
    MATCH_NUMBER = 'match_number'
    DATE = 'date'
    LOCATION = 'location'
    STATUS = 'status'
    HOME_TEAM = 'home_team/country'
    HOME_TEAM_KEY = 'home_team/code'
    GOALS_HOME = 'home_team/goals'
    AWAY_TEAM = 'away_team/country'
    AWAY_TEAM_KEY = 'away_team/code'
    GOALS_AWAY = 'away_team/goals'
    HOME_PENALTIES = 'home_team/penalties'
    AWAY_PENALTIES = 'away_team/penalties'
    HOME_TEAM_RANKING = 'home_team_ranking'
    AWAY_TEAM_RANKING = 'away_team_ranking'
    WINNER = 'winner_system'


class PP:  # policy parameter
    COL_KEY = 'column_key'
    N_ESTIMATORS = 'n_estimators'
    RED_FACTOR = 'reduction_factor'
    ENH_FACTOR = 'enhancement_factor'
    REWARD = 'reward'

    @staticmethod
    def get_pp_as_list():
        return [PP.COL_KEY, PP.N_ESTIMATORS, PP.RED_FACTOR, PP.ENH_FACTOR, PP.REWARD]