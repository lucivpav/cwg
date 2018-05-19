#!/usr/bin/python3
import os
from exceptions import GenException

# Translator Chinese characters/words -> English
class Translator:
    def __init__(self, cedict_path):
        self.dictionary = None;
        self.dictionary = open(os.path.join(cedict_path, 'data'), 'r', encoding='utf8');

        # Read in the file once and build a list of line offsets
        self.line_offset = []
        offset = 0
        for line in self.dictionary:
            self.line_offset.append(offset)
            offset += len(line.encode('utf-8'))+1

    def __del__(self):
        if self.dictionary != None:
            self.dictionary.close()

    # Returns a list of possible translations
    def translate(self, chinese):
        lo = 0;
        hi = len(self.line_offset)-1;
        while lo <= hi:
            mid = (int)((lo+hi)/2);
            self.dictionary.seek(self.line_offset[mid]);
            line = self.dictionary.readline();
            characters = self.__parse_characters(line);
            if characters < chinese:
                lo = mid+1;
            elif characters > chinese:
                hi = mid-1;
            else:
                return self.__parse_definition(line);
        raise GenException('Word ' + chinese + ' was not found in dictionary');

    def __parse_characters(self, line):
        return line[:line.find(' ')];

    # returns a list of possible translations
    def __parse_definition(self, line):
        substr = line[line.find('/')+1:line.rfind('/')];
        return substr.split('/');
