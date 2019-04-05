"""
Description: This module is the central run modul for the spaCy classes
Course: Advanced NLP with spaCy
Instructor: Ines Montani
Copyright: DataCamp
Date: 2019-03-25
"""

from spacy.lang.en import English
from spacy.matcher import Matcher
import spacy  # python -m spacy download en_core_web_sm OR python -m spacy download de_core_news_sm
from DC_spaCy.spacy_basics import SCYL
from DC_spaCy.spacy_matcher_by_pattern import SpacyCourse4Matcher
from DC_spaCy.spacy_vocab_lexemes_stringstore import SpacyCourse4String
from DC_spaCy.spacy_doc_span_token import SpacyCourse4DocSpanToken
from DC_spaCy.spacy_semantic_similarity import SpacyCourse4SemanticSimilarity
from DC_spaCy.spacy_models_and_rules import SpacyCourse4ModelsAndRules
from DC_spaCy.spacy_processing_pipelines import SpacyCourse4Pipelines
from DC_spaCy.spacy_scaling_and_performance import SpacyCourse4Scaling
from DC_spaCy.spacy_training_models import SpacyCourse4TrainingModels

lesson = SCYL.DOC_SPAN_TOKEN

if lesson == SCYL.MATCHER_PATTERN:
    course = SpacyCourse4Matcher('en_core_web_sm')
    # course.run_match_pattern()
    course.debugging_patterns()
elif lesson == SCYL.VOCAB_LEXEMES_STRING_STORE:
    course = SpacyCourse4String('en_core_web_sm')
    course.handle_vocab_strings()
elif lesson == SCYL.DOC_SPAN_TOKEN:
    course = SpacyCourse4DocSpanToken('en_core_web_sm')
    # course.handle_doc()
    course.handle_span(print_ents=True)
elif lesson == SCYL.SEMANTIC_SIMILARITY:
    course = SpacyCourse4SemanticSimilarity('en_core_web_md')
    # course.handle_similarity()
    # course.handle_word_vector()
    course.handle_strange_similarity_example()
elif lesson == SCYL.MODELS_RULES:
    course = SpacyCourse4ModelsAndRules('en_core_web_md')
    # course.handle_word_vector()
    # course.handle_statistical_predictions()
    # course.handle_efficient_phrase_matching()
    course.handle_countries_phrase_matching_with_pipeline()
elif lesson == SCYL.PIPELINE:
    course = SpacyCourse4Pipelines('en_core_web_sm')
    # course.print_pipe_names_and_pipeline_components()
    # course.handle_simple_custom_component()
    # course.handle_extension_attributes_for_token()
    # course.handle_extension_functions_for_token()
    # course.handle_extension_functions_for_token_02()
    # course.handle_extension_method_for_span()
    # course.handle_extension_getter_for_span()
    course.handle_extension_countries()
elif lesson == SCYL.SCALING:
    course = SpacyCourse4Scaling('en_core_web_sm')
    # course.process_large_volume_of_text()
    # course.passing_context_as_tuple()
    course.example_passing_context_with_extension_as_tuple()
    # course.passing_context_with_extensions_as_tuple()
    # course.using_only_the_tokenizer()
    # course.disable_pipeline_components_temporarily()
elif lesson == SCYL.TRAINING:
    course = SpacyCourse4TrainingModels('en_core_web_sm')
    course.train_the_entity_recognizer()

