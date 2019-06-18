"""
Description: This module contains the drop down classes for the tab trades in Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03
"""

from sertl_analytics.mydash.my_dash_components import ButtonHandler


class PFBTN:  # Portfolio Buttons
    RESET_PORTFOLIO_SELECTION = 'Reset_Portfolio_Selection'


class PortfolioButtonHandler(ButtonHandler):
    @property
    def my_portfolio_reset_button(self) -> str:
        return self.get_element_id(PFBTN.RESET_PORTFOLIO_SELECTION)

    @property
    def my_portfolio_reset_button_div(self) -> str:
        return self.get_embracing_div_id(PFBTN.RESET_PORTFOLIO_SELECTION)

    def __get_text__(self, button_type: str):
        value_dict = {
            PFBTN.RESET_PORTFOLIO_SELECTION: 'Reset Selection',
        }
        return value_dict.get(button_type, None)

    def __get_element_id__(self, button_type: str):
        value_dict = {
            PFBTN.RESET_PORTFOLIO_SELECTION: 'my_portfolio_reset_button',
        }
        return value_dict.get(button_type, None)

    def __get_width__(self, button_type: str):
        value_dict = {
            PFBTN.RESET_PORTFOLIO_SELECTION: '250',
        }
        return value_dict.get(button_type, 200)

    def __get_button_value_dict__(self) -> dict:
        return {
            PFBTN.RESET_PORTFOLIO_SELECTION: '',
        }

