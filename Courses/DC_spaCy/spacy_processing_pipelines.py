"""
Description: This module is the course part for DataCamp spaCy processing pipelines.
Course: Advanced NLP with spaCy
Instructor: Ines Montani
Copyright: DataCamp
Date: 2019-03-25

What happens when you call nlp:
- doc = nlp('This is a sentence.')
- text -> Pipeline[tokenizer - tagger - parser - ner - ...] -> Doc

Built-in pipeline components:
tagger: Part-of-speech tagger -> Token.tag
parser: Dependency parser -> Token.dep, Token.head, Doc.sents, doc.noun_chunks
ner: Named entity recognizer -> Doc.ents, Token.ent_iob, Token.ent_type
textcat: Text classifer -> Doc.cats

Under the hood (e.g. en_core_web_sm):
- Pipeline defined in model's meta.json in order
- Built-in components need binary data to make prediction
- meta.json (ner, parser, tagger, vocab): {"lang":"en", "name": "core_web_sm", "pipeline": ["tagger", "parser", "ner"]]

Pipeline attributes:
- nlp.pipe_names: list of pipeline component names: print(nlp.pipe_names): ["tagger", "parser", "ner"]
- nlp.pipeline: list of (name, component) tuples, e.g. ('parser', <spacy.pipeline.DependencyParser>)

Custom pipeline components
- you can create your own function which is called when the nlp object is called.
- perfect to add your own metadata to documents and tokens (see above the pipeline architecture)
- AND: updating built-in attributes like doc.ents
- anatomy of a component(1): Function that takes a doc, modifies it and returns it
-- def custom_component(doc):
        ...
        return doc
- can be added using the nlp.add_pipe method, which position? use keyword arguments: last (def.), first, before, after.
"""

from spacy.lang.en import English
from spacy.tokens import Doc, Span, Token
from spacy.matcher import Matcher, PhraseMatcher
from DC_spaCy.spacy_basics import SpacyCourseBase


class SpacyCourse4Pipelines(SpacyCourseBase):
    def __init__(self, model=''):
        SpacyCourseBase.__init__(self, model)
        self._matcher_animal = self.__get_animal_matcher__()
        self._matcher_country = self.__get_country_matcher__()

    def print_pipe_names_and_pipeline_components(self):
        # Print the names of the pipeline components
        print(self.nlp.pipe_names)
        # Print the full pipeline of (name, component) tuples
        print(self.nlp.pipeline)

    def simple_custom_component(self, doc: Doc):
        # print the doc's length
        print('Doc length={}'.format(len(doc)))
        return doc

    def handle_simple_custom_component(self):
        self.nlp.add_pipe(self.simple_custom_component, name='CUSTOM', last=True)
        self.nlp.add_pipe(self.animal_component, name='CUSTOM_ANIMAL', after='ner')
        doc = self.nlp('I like dogs, cats, cows but now mice. But I would not buy one - unless having a home.')
        self.__print_tokens_for_doc__(doc)
        self.__print_entities_for_doc__(doc)
        print('pipeline={}'.format(self.nlp.pipe_names))

    # Define the custom component
    def animal_component(self, doc):
        matches = self._matcher_animal(doc)
        # Create a Span for each match and assign the label 'ANIMAL'
        spans = [Span(doc, start, end, label='ANIMAL') for match_id, start, end in matches]
        print(doc.text)
        print(spans)
        # Overwrite the doc.ents with the matched spans
        doc.ents = spans
        return doc

    def handle_extension_attributes_for_token(self):
        # Register the Token extension attribute 'is_country' with the default value False
        Token.set_extension('is_country', default=False, force=True)
        # Process the text and set the is_country attribute to True for the token "Spain"
        doc = self.nlp("I live in Spain.")
        token_spain = doc[3]
        # print('has_extension: {}'.format(token_spain.has_extension('is_country')))
        # print(token_spain.text)
        token_spain._.is_country = True
        # Print the token text and the is_country attribute for all tokens
        print([(token.text, token._.is_country) for token in doc])

    def handle_extension_functions_for_token(self):
        # Register the Token property extension 'reversed' with the getter get_reversed
        Token.set_extension('reversed', getter=self.__get_reversed__, force=True)
        # Process the text and print the reversed attribute for each token
        doc = self.nlp("All generalizations are false, including this one.")
        for token in doc:
            print('reversed:', token._.reversed)

    @staticmethod
    def __get_reversed__(token: Token):
        return token.text[::-1]

    def handle_extension_functions_for_token_02(self):
        # Register the Doc property extension 'has_number' with the getter get_has_number
        Doc.set_extension('has_number', getter=self.__get_has_number__)

        # Process the text and check the custom has_number attribute
        doc = self.nlp("The museum closed for five years in 2012.")
        print('has_number:', doc._.has_number)

    @staticmethod
    def __get_has_number__(doc):
        # Return if any of the tokens in the doc return True for token.like_num
        return any(token.like_num for token in doc)

    @staticmethod
    def __to_html__(span, tag):
        # Wrap the span text in a HTML tag and return it
        return '<{tag}>{text}</{tag}>'.format(tag=tag, text=span.text)

    def handle_extension_method_for_span(self):
        # Register the Span property extension 'to_html' with the method to_html
        Span.set_extension('to_html', method=self.__to_html__)
        # Process the text and call the to_html method on the span with the tag name 'strong'
        doc = self.nlp("Hello world, this is a sentence.")
        span = doc[0:2]
        print(span._.to_html('strong'))

    @staticmethod
    def __get_wikipedia_url__(span):
        # Get a Wikipedia URL if the span has one of the labels
        if span.label_ in ('PERSON', 'ORG', 'GPE', 'LOCATION'):
            entity_text = span.text.replace(' ', '_')
            return "https://en.wikipedia.org/w/index.php?search=" + entity_text

    def handle_extension_getter_for_span(self):
        # Set the Span extension wikipedia_url using get getter get_wikipedia_url
        Span.set_extension('wikipedia_url', getter=self.__get_wikipedia_url__, force=True)
        doc = self.nlp("In over fifty years from his very first recordings right through to his last album, "
                       "David Bowie was at the vanguard of contemporary culture.")
        for ent in doc.ents:  # Print the text and Wikipedia URL of the entity
            print(ent.text, ent._.wikipedia_url)

    def countries_component(self, doc):
        # Create an entity Span with the label 'GPE' for all matches
        doc.ents = [Span(doc, start, end, label='GPE')
                    for match_id, start, end in self._matcher_country(doc)]
        return doc

    def handle_extension_countries(self):
        # Add the component to the pipeline
        self.nlp.add_pipe(self.countries_component)
        capitals = {'Czech Republic': 'Prague', 'Slovakia': 'Bratislava'}
        # Register capital and getter that looks up the span text in country capitals
        Span.set_extension('capital', getter=lambda span: capitals.get(span.text))
        # Process the text and print the entity text, label and capital attributes
        doc = self.nlp("Czech Republic may help Slovakia protect its airspace")
        print([(ent.text, ent.label_, ent._.capital) for ent in doc.ents])

    def __get_animal_matcher__(self):
        matcher = PhraseMatcher(self.nlp.vocab)
        animals = ['dog', 'cat', 'mouse', 'dogs', 'cats', 'mice']
        patterns = list(self.nlp.pipe(animals))
        matcher.add('ANIMAL', None, *patterns)
        return matcher

    def __get_country_matcher__(self):
        matcher = PhraseMatcher(self.nlp.vocab)
        countries = ['Czech Republic', 'Australia', 'Germany', 'Slovakia']
        patterns = list(self.nlp.pipe(countries))
        matcher.add('ANIMAL', None, *patterns)
        return matcher

    def handle_countries_phrase_matching_with_pipeline(self):
        # Import the PhraseMatcher and initialize it
        doc = self.nlp('Czech Republic may help Slovakia protect its airspace.')
        matcher = PhraseMatcher(self.nlp.vocab)
        countries = ['Czech Republic', 'Australia', 'Germany', 'Slovakia']
        # Create pattern Doc objects and add them to the matcher
        # This is the faster version of: [nlp(country) for country in COUNTRIES]
        patterns = list(self.nlp.pipe(countries))
        matcher.add('COUNTRY', None, *patterns)

        # Call the matcher on the test document and print the result
        matches = matcher(doc)
        print([doc[start:end] for match_id, start, end in matches])




