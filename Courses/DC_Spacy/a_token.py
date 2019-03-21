from spacy.lang.en import English
import spacy  # python -m spacy download en_core_web_sm


class SpacyCourse:
    def __init__(self):
        self.nlp = English()

    def exercise_01(self):
        # Process the text
        doc = self.nlp("I like tree kangaroos and narwhals.")
        # A slice of the Doc for "tree kangaroos"
        tree_kangaroos = doc[2:4]
        print(tree_kangaroos.text)
        # A slice of the Doc for "tree kangaroos and narwhals" (without the ".")
        tree_kangaroos_and_narwhals = doc[2:6]
        print(tree_kangaroos_and_narwhals.text)

    def exercise_02(self):
        # Process the text
        doc = self.nlp("In 1990, more than 60% of people in East Asia were in extreme poverty. Now less than 4% are.")
        # Iterate over the tokens in the doc
        for token in doc:
            # Check if the token resembles a number
            if token.like_num:
                # Get the next token in the document
                next_token = doc[token.i + 1]
                # Check if the next token's text equals '%'
                if next_token.text == '%':
                    print('Percentage found:', token.text)

    def predicting_part_of_speach(self):  # pos_
        self.nlp = spacy.load('en_core_web_sm')  # small English web model
        doc = self.nlp('She ate the pizza')
        for token in doc:
            print(token.text, token.pos_)
        """
        She PRON
        ate VERB
        the DET
        pizza NOUN
        """

    def predicting_syntactical_dependencies(self):  # dep_
        self.nlp = spacy.load('en_core_web_sm')  # small English web model
        doc = self.nlp('Apple is looking at buying U.K. startup for $1 billion')
        for token in doc:
            print(token.text, token.pos_, token.dep_, token.head.text)
        """
        She PRON nsubj ate      # nsubj = nominal subject
        ate VERB ROOT ate       # ROOT = ???
        the DET det pizza       # det = determines (article)
        pizza NOUN dobj ate     # dobj = direct object
        """

    def predicting_named_entities(self):
        self.nlp = spacy.load('en_core_web_sm')  # small English web model
        doc = self.nlp('Apple is looking at buying U.K. startup for $1 billion')
        for ent in doc.ents:
            print(ent.text, ent.label_)
        """
        Apple ORG
        U.K. GPE
        $1 billion MONEY
        """

    def explain(self, term: str):
        # example term = GPE = Countries, cities, states,
        # MONEY = Monetary values, including unit
        print(spacy.explain(term))

course = SpacyCourse()
# course.exercise_01()
# course.exercise_02()
course.predicting_named_entities()
course.explain('MONEY')



