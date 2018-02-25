import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), \
                                                                '../src')));
import unittest
import tempfile

from gen import generate_infos, WORDS_FILE, CHARACTERS_FILE
from exceptions import GenException

class TestGen(unittest.TestCase):
    def setUp(self):
        self.makemeahanzi_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../makemeahanzi'));
        self.cedict_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../cedict'));

    def test_generate_infos_no_words(self):
        with tempfile.TemporaryDirectory() as wd:
            characters = '你好';
            generate_infos(self.makemeahanzi_path, self.cedict_path, \
                            wd, characters);
            self.__assert_correct_info_files(wd, 2, 0);

    def test_generate_infos_one_word(self):
        with tempfile.TemporaryDirectory() as wd:
            characters = '(你好)';
            generate_infos(self.makemeahanzi_path, self.cedict_path, \
                            wd, characters);
            self.__assert_correct_info_files(wd, 2, 1);

    def test_generate_infos_two_words(self):
        with tempfile.TemporaryDirectory() as wd:
            characters = '(你好)(高興）';
            generate_infos(self.makemeahanzi_path, self.cedict_path, \
                            wd, characters);
            self.__assert_correct_info_files(wd, 4, 2);

    def test_generate_infos_unknown_character(self):
        with tempfile.TemporaryDirectory() as wd:
            characters = '你好ř';
            with self.assertRaises(GenException):
                generate_infos(self.makemeahanzi_path, self.cedict_path, \
                                wd, characters);

    # expected: word with empty definition list
    def test_generate_infos_unknown_word(self):
        with tempfile.TemporaryDirectory() as wd:
            characters = '(你好號號)';
            generate_infos(self.makemeahanzi_path, self.cedict_path, \
                            wd, characters);
            self.__assert_correct_info_files(wd, 4, 1);

    def test_generate_infos_invalid_makemeahanzi_path(self):
        with tempfile.TemporaryDirectory() as wd:
            characters = '你好';
            with self.assertRaises(Exception):
                generate_infos('i_dont_exist', self.cedict_path, \
                            wd, characters);

    def test_generate_infos_invalid_cedict_path(self):
        with tempfile.TemporaryDirectory() as wd:
            characters = '你好';
            with self.assertRaises(Exception):
                generate_infos(self.makemeahanzi_path, 'i_dont_exist', \
                            wd, characters);

    def test_generate_infos_no_characters(self):
        with tempfile.TemporaryDirectory() as wd:
            characters = '';
            with self.assertRaises(GenException):
                generate_infos(self.makemeahanzi_path, self.cedict_path, \
                                wd, characters);

    def test_generate_infos_too_many_characters(self):
        with tempfile.TemporaryDirectory() as wd:
            characters = '你好號號號號號號號號號號號號號號號號號' + \
                            '號號號號號號號號號號號號號號號號號號號' + \
                            '號號號號號號號號號號號號號號號號號號號';
            with self.assertRaises(GenException):
                generate_infos(self.makemeahanzi_path, self.cedict_path, \
                            wd, characters);

    def __assert_correct_info_files(self, working_directory, \
                                    expected_number_of_characters, \
                                    expected_number_of_words):
        wd = working_directory;
        self.__assert_correct_infos_file(os.path.join(wd, CHARACTERS_FILE), \
                                            expected_number_of_characters);
        self.__assert_correct_infos_file(os.path.join(wd, WORDS_FILE), \
                                            expected_number_of_words);

    def __assert_correct_infos_file(self, file_path, expected_number_of_infos):
        cnt = 0;
        with open(file_path, 'r') as f:
            while 1:
                line = f.readline();
                if line == '':
                    break;
                cnt += 1;
        self.assertEqual(expected_number_of_infos, cnt);

if __name__ == '__main__':
    unittest.main();
