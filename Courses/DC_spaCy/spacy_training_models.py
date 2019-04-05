"""
Description: This module is the course part for DataCamp spaCy training and updating models
Course: Advanced NLP with spaCy
Instructor: Ines Montani
Copyright: DataCamp
Date: 2019-04-01

Training and updating models:
Why updating the model?

How to train models(1):
1. initialize the model weights randomly with nlp.begin_training
2. predict a few examples with the current weights by calling nlp.update
3. compare prediction with true labels
4. calculate how to change weights to improve predictions
5. update weights slightly
6. go back to 2.

Diagram: Training Data -> [Text, Label, (Label-predicted)] -> Gradient -> Model predict label backwards -> Save updated model:
Training data: Examples and their annotations
Text: The input text the model should predict a label for
Label: can be a text category or an entity span or it's type
Gradient: how to change the weights

The training data:
- examples of what we want the model to predict in context: texts, named entities, tokens and their pos tags.
- to update an existing model: we can start with hundreds or thousands examples
- to create a new model: we need millions of examples (spaCy's English models were trained on 2 millions words)
- usually created manually by human annotators
- can be semi-automated - e.g. using spaCy's Matcher.

The training loop:
1. loop for a number of times
2. Shuffle (by random) the training data for each iteration to avoid getting stuck in a suboptimal solution
3. Divide the data into batches (mini-batching)
4. Update the model for each batch
5. Save the updated model
Goals:
a) Improve the prediction on new data
b) Especially useful to improve existing categories, like PERSON
c) Also possible to add new categories (and test also existing categories which were already predicted correctly)
"""

from spacy.tokens import Doc
import spacy
from DC_spaCy.spacy_basics import SpacyCourseBase
from datetime import datetime
import random


class SpacyCourse4TrainingModels(SpacyCourseBase):
    def __init__(self, model=''):
        SpacyCourseBase.__init__(self, model)

    def train_the_entity_recognizer(self):
        """
        The entity recognizer tags words and phrases in context
        each token can only be part of one entity
        examples need to come with context: ("iPhone X is coming", {'entities': [(0, 8, 'GADGET')]})
        texts with no entities are also important: ("I need a new phone", {'entities': []})
        GOAL: teach the model to generalize, e.g. recognize new entities in similar context -
        even if there were not in the training data
        :return:
        """
        text_01 = 'This is my disable pipeline component test. This is done by my friend Markus.'
        text_02 = 'This is my disable pipeline component test. This is done by my friend Markus.'
        text_list = [text_01, text_02]
        print(datetime.now())
        docs = [self.nlp(text) for text in text_list]  # bad
        print(datetime.now())
        docs = list(self.nlp.pipe(text_list))  # good
        print(datetime.now())
        # Create a list of patterns for the PhraseMatcher
        people = ['David Bowie', 'Angela Merkel', 'Lady Gaga']
        patterns = list(self.nlp.pipe(people))

    def example_loop(self):
        TRAINING_DATA = [('How to preorder the iPhone X', {'entities': [(20, 28, 'GADGET')]})]
        # and many more examples...
        # loop for 10 iterations:
        for i in range(10):
            # shuffle the training data
            random.shuffle(TRAINING_DATA)
            # create batches and iterate over them
            for batch in spacy.util.minibatch(TRAINING_DATA):
                # split the batch in texts and annotations
                texts = [text for text, annotation in batch]
                annotations = [annotation for text, annotation in batch]
                # update the model
                self.nlp.update(texts, annotations)
        self.nlp.to_disk('D:\Spacy_Models')

    def setting_up_a_new_pipeline_from_scratch(self):
        TRAINING_DATA = [('How to preorder the iPhone X', {'entities': [(20, 28, 'GADGET')]})]
        # start with a blank English model (no pipes unless the tokenizer
        self.nlp = spacy.blank('en')
        # create blank entity recognizer and add it to the pipeline
        ner = self.nlp.create_pipe('ner')
        self.nlp.add_pipe(ner)
        # Add a new label
        ner.add_label('GADGET')
        # start the training
        self.nlp.begin_training()
        # train for 10 iterations
        for itn in range(10):
            random.shuffle(TRAINING_DATA)
            losses = {}
            # create batches and iterate over them
            for batch in spacy.util.minibatch(TRAINING_DATA, size=2):  # split the batch in texts and annotations
                texts = [text for text, annotation in batch]
                annotations = [annotation for text, annotation in batch]
                # update the model
                self.nlp.update(texts, annotations, losses=losses)
        self.nlp.to_disk('D:\Spacy_Models_new')

    def exercise_setting_up_the_pipeline(self):
        """
        In this exercise, you'll prepare a spaCy pipeline to train the entity recognizer
        to recognize 'GADGET' entities in a text – for example, "iPhone X".
        """
        TRAINING_DATA = [
            ('How to preorder the iPhone X', {'entities': [(20, 28, 'GADGET')]}),
            ('iPhone X is coming', {'entities': [(0, 8, 'GADGET')]}),
            ('Should I pay $1,000 for the iPhone X?', {'entities': [(28, 36, 'GADGET')]}),
            ('The iPhone 8 reviews are here', {'entities': [(4, 12, 'GADGET')]}),
            ('Your iPhone goes up to 11 today', {'entities': [(5, 11, 'GADGET')]}),
            ('I need a new phone! Any tips?', {'entities': []})]

        # Create a blank 'en' model
        nlp = spacy.blank('en')

        # Create a new entity recognizer and add it to the pipeline
        ner = self.nlp.create_pipe('ner')
        self.nlp.add_pipe(ner)

        # Add the label 'GADGET' to the entity recognizer
        ner.add_label('GADGET')
        # Start the training
        nlp.begin_training()
        # Loop for 10 iterations
        for itn in range(10):
            # Shuffle the training data
            random.shuffle(TRAINING_DATA)
            losses = {}
            # Batch the examples and iterate over them
            for batch in spacy.util.minibatch(TRAINING_DATA, size=2):
                texts = [text for text, entities in batch]
                annotations = [entities for text, entities in batch]
                # Update the model
                nlp.update(texts, annotations, losses=losses)
                print(losses)
        """
            {'ner': 10.399999976158142}
            {'ner': 20.304734706878662}
            {'ner': 31.697577953338623}
            ... (getting better for each minibatch for each loop
            {'ner': 10.399999976158142}
            {'ner': 20.304734706878662}
            {'ner': 31.697577953338623}
    
        Let's see how the model performs on unseen data! To speed things up a little, 
        here's a trained model for the label 'GADGET', using the examples from the previous exercise, 
        plus a few hundred more. The loaded model is already available as the nlp object. 
        A list of test texts is available as TEST_DATA.
        """
        TEST_DATA = ['Apple is slowing down the iPhone 8 and iPhone X - how to stop it',
                     "I finally understand what the iPhone X 'notch' is for",
                     'Everything you need to know about the Samsung Galaxy S9',
                     'Looking to compare iPad models? Here’s how the 2018 lineup stacks up',
                     'The iPhone 8 and iPhone 8 Plus are smartphones designed, developed, and marketed by Apple',
                     'what is the cheapest ipad, especially ipad pro???',
                     'Samsung Galaxy is a series of mobile computing devices designed, '
                     'manufactured and marketed by Samsung Electronics']

        for doc in nlp.pipe(TEST_DATA):
            # Print the document text and entitites
            print(doc.text)
            print(doc.ents, '\n\n')

        """
        Apple is slowing down the iPhone 8 and iPhone X - how to stop it
        (iPhone 8, iPhone X)
        """

    def exercise_creating_training_data(self):
        """
        Let's use the match patterns we've created in the previous exercise to bootstrap a set of training examples.
        The nlp object has already been created for you and the Matcher with the added patterns pattern1
        and pattern2 is available as the variable matcher. A list of sentences is available as the variable TEXTS.

        Match on the doc and create a list of matched spans.
        Format each example as a tuple of the text and a dict, mapping 'entities' to the entity tuples.
        Append the example to TRAINING_DATA and inspect the printed data.

        # Create a Doc object for each text in TEXTS
        for doc in nlp.pipe(TEXTS):
        # Find the matches in the doc
        matches = matcher(doc)

        # Get a list of (start, end, label) tuples of matches in the text
        entities = [(start, end, 'GADGET') for match_id, start, end in matches]
        print(doc.text, entities)

        TRAINING_DATA = []

        # Create a Doc object for each text in TEXTS
        for doc in nlp.pipe(TEXTS):
            # Match on the doc and create a list of matched spans
            spans = [doc[start:end] for match_id, start, end in matcher(doc)]
            # Get (start character, end character, label) tuples of matches
            entities = [(span.start_char, span.end_char, 'GADGET') for span in spans]

            # Format the matches as a (doc.text, entities) tuple
            training_example = (doc.text, {'entities': entities})
            # Append the example to the training data
            TRAINING_DATA.append(training_example)

        print(*TRAINING_DATA, sep='\n')
        :return:
        """
        pass

    def steps_of_a_training_loop(self):
        """

        :return:
        """
