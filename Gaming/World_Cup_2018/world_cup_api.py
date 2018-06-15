"""
Description: This module contains the API classes for the FIFA world cup predictor
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-13
"""

import numpy as np


class WorldCupRankingAdjustmentApi:
    def __init__(self, actual_min_penalty = np.inf):
        self.actual_min_penalty = actual_min_penalty
        self.penalty = 0
        self.ranking_difference = 0
        self.ranking_reduction_factor = 0
        self.ranking_enhancement_factor = 0
        self.penalty_wrong_winner = 0
        self.penalty_wrong_remis = 0
        self.penalty_not_remis = 0

    def clone(self):
        api = WorldCupRankingAdjustmentApi(self.actual_min_penalty)
        api.penalty = self.penalty
        api.ranking_difference = self.ranking_difference
        api.ranking_reduction_factor = self.ranking_reduction_factor
        api.ranking_enhancement_factor = self.ranking_enhancement_factor
        api.penalty_wrong_winner = self.penalty_wrong_winner
        api.penalty_wrong_remis = self.penalty_wrong_remis
        api.penalty_not_remis = self.penalty_not_remis
        return api

    def print(self):
        print('Penalty: {:2.0f} for Ranking_difference: {} Reduction_factor: {:1.1f} Enhancement_factor: {:1.1f} '
              'Penalty_wrong_winner: {} Penalty_wrong_remis: {} Penalty_not_remis: {}'.format(
            self.actual_min_penalty, self.ranking_difference, self.ranking_reduction_factor,
            self.ranking_enhancement_factor,
            self.penalty_wrong_winner, self.penalty_wrong_remis, self.penalty_not_remis)
        )