import pandas as pd
from sqlalchemy import create_engine
import numpy as np


def select_all():
    # Create an engine that connects to the census.sqlite file: engine
    engine = create_engine('sqlite:///MySoccer.sqlite')
    #print(engine.table_names())
    connection = engine.connect()
    stmt = """
SELECT GameGroup.GroupId, GameGroup.GroupName, Match.MatchId, Match.MatchDateTime, Match.NumberOfViewers
, Team.TeamId as HomeTeamId, Team2.TeamId as ForeignTeamId, Team.TeamName as HomeTeam, Team2.TeamName as ForeignTeam
, MatchResult.PointsTeam1, MatchResult.PointsTeam2
, Case When MatchResult.PointsTeam1 is NULL Then 0 Else (10 + MatchResult.PointsTeam1 - MatchResult.PointsTeam2) End as GoalDifference
FROM Match
LEFT JOIN GameGroup ON GameGroup.GroupId = Match.GroupId
LEFT JOIN MatchTeam ON Match.MatchId = MatchTeam.MatchId and MatchTeam.IsHomeTeam = 1
LEFT JOIN MatchTeam as MatchTeam2 ON Match.MatchId = MatchTeam2.MatchId and MatchTeam2.IsHomeTeam = 0
LEFT JOIN Team ON Team.TeamId = MatchTeam.TeamId
LEFT JOIN Team as Team2 ON Team2.TeamId = MatchTeam2.TeamId
LEFT JOIN MatchResult on MatchResult.MatchId = Match.MatchId and MatchResult.ResultTypeId = 2
LEFT JOIN Location on Match.LocationId = Location.LocationId
Order by GameGroup.GroupId, Match.MatchId
"""
    results = connection.execute(stmt).fetchall()
    connection.close()
    return results

results = select_all()
df = pd.DataFrame(results)
df.columns = results[0].keys()
print(df.head())
df.info()


def get_nparrays(df: pd.DataFrame):
    group_list = np.sort(pd.unique(df["GroupId"]))
    valid_group_indices = get_latest_valid_group_index(group_list, df)
    np_array = np.zeros((valid_group_indices + 1, df.shape[0]))

    print('shape_np_array {} - valid_group_indices={}'.format(np_array.shape, valid_group_indices))

    for group_list_index in range(0, valid_group_indices + 1):
        for id, row in df.iterrows():
            if row["GroupId"] == group_list[group_list_index]:
                goal_difference = row["GoalDifference"]
                for array_index in range(group_list_index, valid_group_indices + 1):
                    np_array[array_index, id] = goal_difference

    np_predictors = np.copy(np_array)
    print('shape_predictors_after copy {}'.format(np_predictors.shape))
    np_predictors = np.insert(np_predictors, 0, np.zeros(df.shape[0]), axis=0)
    print('shape_predictors_after insert {}'.format(np_predictors.shape))
    np_predictors = np.delete(np_predictors, (-1), axis=0)
    print('shape_predictors_after delete {}'.format(np_predictors.shape))
    np_target = np.copy(np_array)
    return np_predictors, np_target, np_target[-1,:]

def get_latest_valid_group_index(group_list, df: pd.DataFrame):
    for group_list_index, group_id in enumerate(group_list):
        for id, row in df.iterrows():
            if row["GroupId"] == group_id:
                goal_difference = row["GoalDifference"]
                if goal_difference == 0:
                    print('MatchId = {}, list_index ={}'.format(row["MatchId"], group_list_index))
                    return group_list_index - 1  # take the lasted index where there were some games.
    return group_list.size

def make_prediction(np_predictors: np.array, np_target: np.array, np_pred_data: np.array):
    import numpy as np
    from keras.layers import Dense
    from keras.models import Sequential
    # Specify, compile, and fit the model
    print('np_predictors.shape={}, np_target.shape={}, np_pred_data.shape={}'.format(np_predictors.shape, np_target.shape, np_pred_data.shape))
    n_cols = np_predictors.shape[1]
    print('n_cols = {}'.format(n_cols))
    model = Sequential()
    model.add(Dense(32, activation='relu', input_shape=(n_cols,)))
    model.add(Dense(30, activation='relu'))
    model.add(Dense(306))  # output layer
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(np_predictors, np_target)

    # Calculate predictions: predictions
    predictions = model.predict(np_pred_data)
    # Calculate predicted probability of survival: predicted_prob_true
    print(predictions)
    # predicted_prob_true = predictions[:, 1]
    # # print predicted_prob_true
    # print(predicted_prob_true)

[np_predictors, np_target, np_pred_data] = get_nparrays(df)
make_prediction(np_predictors, np_target, np_pred_data)







