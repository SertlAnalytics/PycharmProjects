"""
Description: This module contains different confirmation handlings.
They enable to loop with a counter without declaring a counter variable.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-21
"""


class UserInput:
    @staticmethod
    def get_confirmation(question_str: str) -> bool:
        question = question_str + " (y/n)?"
        answer = ''
        while not UserInput.__is_answer_yes_or_no__(answer):
            answer = input(question)
        if UserInput.__is_answer_yes__(answer):
            return True
        else:
            return False

    @staticmethod
    def get_input(quote: str) -> str:
        request = quote.strip() + " (x=cancel): "
        answer = ''
        while answer.strip() == '':
            answer = input(request)
        return answer

    @staticmethod
    def __is_answer_yes__(answer: str) -> bool:
        return answer.lower().strip() in ['y', 'yes']

    @staticmethod
    def __is_answer_no__(answer: str) -> bool:
        return answer.lower().strip() in ['n', 'no']

    @staticmethod
    def __is_answer_yes_or_no__(answer: str) -> bool:
        return UserInput.__is_answer_yes__(answer) or UserInput.__is_answer_no__(answer)