from translator import Translator
from exceptions import GenException

import json

class Word:
    def __init__(self, character_begin_index, character_end_index, definition):
        self.character_begin_index = character_begin_index;
        self.character_end_index = character_end_index;
        self.definition = definition;

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True);

    def fromJSON(json):
        return Word(json['character_begin_index'], \
                    json['character_end_index'], \
                    json['definition']);

class WordManager:
    WORDS_FILE = 'word_infos.json';
    LEFT_PARENTHESES = '(（';
    RIGHT_PARENTHESES = ')）';
    PARENTHESES = LEFT_PARENTHESES + RIGHT_PARENTHESES;
    MIN_WORD_LEN = 2;
    MAX_WORD_LEN = 10;

    validated = False;

    # characters_and_words: (example) '（你好)我叫(保羅)'
    def __init__(self, characters_and_words, cedict_path):
        self.characters_and_words = characters_and_words;
        self.translator = None;
        self.translator = Translator(cedict_path);

    def __del__(self):
        if self.translator != None:
            self.translator.__del__();

    # throws if invalid parentheses configuration detected or word length
    # is out of bounds
    def assure_valid(self):
        if self.validated:
            return;
        par_cnt = 0;
        in_par = False;
        for c in self.characters_and_words:
            if self.__is_left_parenthesis(c):
                par_cnt = par_cnt + 1;
                word_len = 0;
                if in_par:
                    self.raise_unexpected_parenthesis_exception(par_cnt);
                in_par = True;
            elif self.__is_right_parenthesis(c):
                par_cnt = par_cnt + 1;
                if not in_par:
                    self.raise_unexpected_parenthesis_exception(par_cnt);
                elif word_len < self.MIN_WORD_LEN:
                    raise GenException('Words must be at least ' + \
                                        str(self.MIN_WORD_LEN) + \
                                        ' characters long');
                elif word_len > self.MAX_WORD_LEN:
                    raise GenException('Words cannot be longer than ' + \
                                        str(self.MAX_WORD_LEN) + \
                                        ' characters');
                in_par = False;
            elif in_par:
                word_len = word_len + 1;

        if in_par:
            self.raise_unexpected_parenthesis_exception(par_cnt);
        self.validated = True;

    def raise_unexpected_parenthesis_exception(self, par_cnt):
        raise GenException('Unexpected parenthesis #' + str(par_cnt));

    def get_words(self):
        self.assure_valid();
        words = list();
        par_cnt = 0;
        for i in range(len(self.characters_and_words)):
            c = self.characters_and_words[i]; # TODO: use enumerate
            if self.__is_left_parenthesis(c):
                begin_character_index = i - par_cnt;
                begin_word_index = i+1;
                par_cnt = par_cnt + 1;
            if self.__is_right_parenthesis(c):
                par_cnt = par_cnt + 1;
                end_character_index = i - par_cnt;
                end_word_index = i-1;
                chinese_word = self.characters_and_words[begin_word_index:
                                                        end_word_index+1];
                try:
                    definition = self.translator.translate(chinese_word);
                except GenException:
                    definition = list();
                words.append(Word(begin_character_index, end_character_index, \
                                    definition));
        return words;

    def get_characters(self):
        self.assure_valid();
        characters = self.characters_and_words;
        for par in self.PARENTHESES:
            characters = characters.replace(par, '');
        return characters;

    def __is_left_parenthesis(self, character):
        return character in self.LEFT_PARENTHESES;
    
    def __is_right_parenthesis(self, character):
        return character in self.RIGHT_PARENTHESES;
