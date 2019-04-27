from spacy import displacy
from spacy.lang.en import English

nlp = English()
doc = nlp('Wall Street Journal just published an interesting piece on crypto currencies')
displacy.render(doc, style='dep', jupyter=True, options={'distance': 90})
