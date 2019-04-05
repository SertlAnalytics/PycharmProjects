"""
Description: This module is the beginners course for DataCamp spaCy rule-based matching.
Course: Advanced NLP with spaCy
Instructor: Ines Montani
Copyright: DataCamp
Date: 2019-03-25

Why not just regular expressions?
a) match on Doc objects
b) match on tokens and token attributes
c) use the model's predictions
Example: 'duck' (verb) vs 'duck' (noun)
Match patterns:
- list of dictionaries, one per token: key are names of the token attributes - mapped to the expected values
Example for Match exact token texts: [{'ORTH': 'iPhone'}, {'ORTH': 'X'}]
Example for Lexical attributes: [{'LOWER': 'iphone'}, {'LOWER': 'x'}]
Example for any token attributes [{'LEMMA': 'buy'}, {'POS': 'NOUN'}]
Example for optional digit: {'IS_DIGIT': True, 'OP': '?'}
- using operators and quantifiers
Example: pattern = [{'LEMMA': 'buy'}, {'POS': 'DET', 'OP': '?'}, {'POS': 'NOUN'}]  # ?=optional, matches 0 or 1 times
-> OP can be '!' = Negation (match 0 times), '?': optional: 0 or 1 times, '+': 1 or more, '*': 0 or more
"""

from spacy.lang.en import English
from spacy.matcher import Matcher
import spacy  # python -m spacy download en_core_web_sm
from DC_spaCy.spacy_basics import SpacyCourseBase


class SpacyCourse4Matcher(SpacyCourseBase):
    def match_pattern(self, text: str, pattern: list):  # pos_
        # Initialize the matcher with the shared vocab
        cat_hash = self.nlp.vocab.strings['cat']
        cat_string = self.nlp.vocab.strings[cat_hash]
        matcher = Matcher(self.nlp.vocab)
        # pattern = [{'ORTH': 'iPhone'}, {'ORTH': 'X'}]
        # pattern = [{'LOWER': 'iphone'}, {'LOWER': 'x'}]
        matcher.add('IPHONE_PATTERN', None, pattern)  # second argument is an optional callback
        # process some text
        doc = self.nlp(text)
        # call the matcher on the doc
        # for token in doc:
        #     print(token.text, token.pos_)
        matches = matcher(doc)
        # Iterate over the matches
        for match_id, start_ind, end_ind in matches:  # get the matched span
            # match_id: hash value of the pattern name
            # start_ind: start index of matched span
            # end_ind: end index of matched span
            matched_span = doc[start_ind:end_ind]
            print('match_id={}, start_ind={}, end_ind={}, matched_span={}'.format(
                match_id, start_ind, end_ind, matched_span))

    def run_match_pattern(self):
        # self.match_pattern('New iPhone X release date leaked', [{'ORTH': 'iPhone'}, {'ORTH': 'X'}])
        # self.match_pattern('2018 FIFA World Cup: France won!',
        #                     [{'IS_DIGIT': True}, {'LOWER': 'fifa'}, {'LOWER': 'world'},
        #                      {'LOWER': 'cup'}, {'IS_PUNCT': True}])
        pattern = [{'LEMMA': 'love', 'POS': 'VERB'}, {'POS': 'NOUN'}]
        # # pattern = [{'LEMMA': 'dog', 'POS': 'NOUN'}]
        self.match_pattern('I loved dogs but now I love cats more!', pattern)
        pattern = [{'LEMMA': 'buy'}, {'POS': 'DET', 'OP': '?'}, {'POS': 'ADJ', 'OP': '?'}, {'POS': 'NOUN'}]
        self.match_pattern('I bought a car but accually I wanted to buy a new bike!', pattern)
        # self.match_pattern('I bought a smartphone. Now I am buying apps!', pattern)
        text = "i downloaded Fortnite on my laptop and can't open the game at all. Help? so when I was downloading Minecraft, I got the Windows version where it is the '.zip' folder and I used the default program to unpack it... do I also need to download Winzip?"
        pattern = [{'LEMMA': 'download'}, {'POS': 'PROPN'}]
        self.match_pattern(text, pattern)

    def debugging_patterns(self):
        """
        Edit pattern1 so that it correctly matches all case-insensitive mentions of
        "Amazon" plus a title-cased proper noun.
        Edit pattern2 so that it correctly matches all case-insensitive mentions of "ad-free",
        plus the following noun.
        :return:
        """
        # Create the match patterns
        pattern1 = [{'LOWER': 'amazon'}, {'IS_TITLE': True, 'POS': 'PROPN'}]
        pattern2 = [{'LOWER': 'ad'}, {'TEXT': '-'}, {'LOWER': 'free'}, {'POS': 'NOUN'}]

        # Initialize the Matcher and add the patterns
        matcher = Matcher(self.nlp.vocab)
        matcher.add('PATTERN1', None, pattern1)
        matcher.add('PATTERN2', None, pattern2)

        doc = self.nlp("Twitch Prime, the perks program for Amazon Prime members offering free loot, "
                       "games and other benefits, is ditching one of its best features: ad-free viewing. "
                       "According to an email sent out to Amazon Prime members today, "
                       "ad-free viewing will no longer be included as a part of Twitch Prime for new members, "
                       "beginning on September 14. "
                       "However, members with existing annual subscriptions will be able "
                       "to continue to enjoy ad-free viewing until their subscription comes up for renewal. "
                       "Those with monthly subscriptions will have access to ad-free viewing until October 15.")

        print(doc.text)
        for token in doc:
            print(token.text, token.pos_, token.dep_, token.head.text)

        # Iterate over the matches
        for match_id, start, end in matcher(doc):
            # Print pattern string name and text of matched span
            print(doc.vocab.strings[match_id], doc[start:end].text)



