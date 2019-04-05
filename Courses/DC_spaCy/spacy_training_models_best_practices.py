"""
Description: This module is the course part for DataCamp spaCy training and updating models
Course: Advanced NLP with spaCy
Instructor: Ines Montani
Copyright: DataCamp
Date: 2019-04-01

Training and updating models:
Why updating the model?

Diagram: Training Data -> [Text, Label, (Label-predicted)] -> Gradient -> Model predict label backwards -> Save updated model:
Training data: Examples and their annotations

"""

from spacy.tokens import Doc
import spacy
from DC_spaCy.spacy_basics import SpacyCourseBase
from datetime import datetime
import random


class SpacyCourse4TrainingModelsBestPractices(SpacyCourseBase):
    def __init__(self, model=''):
        SpacyCourseBase.__init__(self, model)

    def models_can_forget_things(self):
        """
        a) Existing model can overfit on new data
            i) e.g. if you only update it with "WEBSITE", it can 'unlearn' what a person is
        b) also known as 'catastrophic forgetting' problem

        Solution:
        - For example, if you're training WEBSITE, also include examples of PERSON
        - run existing spaCy model over data and extract all other relevant entities
        """
        # BAD
        TRAINING_DATA = [
            ('Reddit is a website', {'entities': [(0, 6, 'WEBSITE')]})
        ]

        # GOOD
        TRAINING_DATA = [
            ('Reddit is a website', {'entities': [(0, 6, 'WEBSITE')]}),
            ('Obama is a person', {'entities': [(0, 5, 'PERSON')]})
        ]

    def models_cannot_learn_everything(self):
        """
        a) spaCy's models make predictions based on local context,
            - e.g. for entities: the surrounding words are most important
        b) model can struggle to learn if decision is difficult to make based on context
        c) label scheme needs to be consistent and not too specific
            - for example: CLOTHING is better than ADULT_CLOTHING and CHILDRENS_CLOTHING

        Solution:
        - it's always good to plan the category scheme very well in advance
        - pick categories that are reflected in local context
        - more generic is better than too specific
        - use rules to go from generic labels to specific categories

        """
        # BAD
        LABELS = ['ADULT_CLOTHING', 'CHILDRENS_CLOTHING', 'BANDS_I_LIKE']

        # GOOD
        LABELS = ['CLOTHING', 'BANDS']

    def excercise_good_data_versus_bad_data(self):
        TRAINING_DATA = [
            ("i went to amsterdem last year and the canals were beautiful", {'entities': [(10, 19, 'GPE')]}),
            ("You should visit Paris once in your life, but the Eiffel Tower is kinda boring",
             {'entities': [(17, 22, 'GPE')]}),
            ("There's also a Paris in Arkansas, lol", {'entities': [(15, 20, 'GPE'), (24, 32, 'GPE')]}),
            ("Berlin is perfect for summer holiday: lots of parks, great nightlife, cheap beer!",
             {'entities': [(0, 6, 'GPE')]})
        ]

        print(*TRAINING_DATA, sep='\n')

        TRAINING_DATA = [
            ("Reddit partners with Patreon to help creators build communities",
             {'entities': [(0, 6, 'WEBSITE'), (21, 28, 'WEBSITE')]}),

            ("PewDiePie smashes YouTube record",
             {'entities': [(0, 9, 'PERSON'), (18, 25, 'WEBSITE')]}),

            ("Reddit founder Alexis Ohanian gave away two Metallica tickets to fans",
             {'entities': [(0, 6, 'WEBSITE'), (15, 29, 'PERSON')]})
        ]
        # And so on...