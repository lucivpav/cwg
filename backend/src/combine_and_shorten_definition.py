from reportlab.pdfbase.pdfmetrics import stringWidth
from exceptions import GenException

# sep: string separating translations in definition
# definition: a string separated by characers in sep
def combine_and_shorten_definition(definition, sep, max_w, font_name, font_size):
    if len(definition) == 0: # TODO!
        raise GenException('Definition is too long and could not be shortened');
    text = sep.join(definition);
    w = stringWidth(text, font_name, font_size);
    if w <= max_w:
        return text;
    return combine_and_shorten_definition(definition[0:-1], sep, max_w, font_name, font_size);
