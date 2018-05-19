import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), \
                                                                '../src')));
import unittest
from word_manager import WordManager, Word
from exceptions import GenException

class TestWordManager(unittest.TestCase):
    CEDICT_PATH = '../cedict';

    def test_assure_valid_should_not_throw_no_parentheses(self):
        manager = WordManager('你好我叫保羅', self.CEDICT_PATH);
        manager.assure_valid();

    def test_assure_valid_should_not_throw(self):
        manager = WordManager('（你好)我叫(保羅)', self.CEDICT_PATH);
        manager.assure_valid();

    def test_assure_valid_should_throw(self):
        manager = WordManager('（你(好)我叫(保羅)', self.CEDICT_PATH);
        with self.assertRaises(GenException):
            manager.assure_valid();

    def test_assure_valid_should_throw2(self):
        manager = WordManager('（你)好)我叫(保羅)', self.CEDICT_PATH);
        with self.assertRaises(GenException):
            manager.assure_valid();

    def test_assure_valid_should_throw3(self):
        manager = WordManager('（你)好)我叫(保羅)', self.CEDICT_PATH);
        with self.assertRaises(GenException):
            manager.assure_valid();

    def test_assure_valid_should_throw_word_too_short(self):
        manager = WordManager('（你)好我叫(保羅)', self.CEDICT_PATH);
        with self.assertRaises(GenException):
            manager.assure_valid();

    def test_assure_valid_should_throw_word_empty(self):
        manager = WordManager('（你)好我叫()', self.CEDICT_PATH);
        with self.assertRaises(GenException):
            manager.assure_valid();

    def test_assure_valid_should_throw_word_too_long(self):
        manager = WordManager('（您那你好我叫保羅號號號)', self.CEDICT_PATH);
        with self.assertRaises(GenException):
            manager.assure_valid();

    def test_get_characters_no_parentheses(self):
        manager = WordManager('你好我叫保羅', self.CEDICT_PATH);
        self.assertEqual('你好我叫保羅', manager.get_characters());

    def test_get_characters_with_parentheses(self):
        manager = WordManager('（你好)我叫(保羅）', self.CEDICT_PATH);
        self.assertEqual('你好我叫保羅', manager.get_characters());

    def test_get_words_two_sunny_words(self):
        manager = WordManager('（你好)我叫(保羅）', self.CEDICT_PATH);
        expected_words = [Word(0,1,['hello']), Word(4,5,['Paul'])];
        words = manager.get_words();
        self.assertEqual(2, len(words));
        for i, word in enumerate(words):
            self.__assert_words_similar(expected_words[i], word);

    def test_get_words_one_word_without_translation(self):
        manager = WordManager('（你好我叫保羅)', self.CEDICT_PATH);
        words = manager.get_words();
        self.assertEqual(1, len(words));
        self.assertEqual(0, len(words[0].definition));

    def __assert_words_similar(self, expected_word, actual_word):
        self.assertEqual(expected_word.character_begin_index, \
                        actual_word.character_begin_index);
        self.assertEqual(expected_word.character_end_index, \
                        actual_word.character_end_index);
        for translation in actual_word.definition:
            if expected_word.definition[0] in translation:
                return;
        raise Exception('definition mistmatch (' + \
                        ', '.join(expected_word.definition) + ' vs ' + \
                        ', '.join(actual_word.definition) + ')');

if __name__ == '__main__':
    unittest.main();
