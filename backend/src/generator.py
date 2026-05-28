#!/usr/bin/python3

import json
import os
import math

import re
from enum import Enum
from cairosvg import svg2png
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import CMYKColor
from spanning_translation import SpanningTranslation
from exceptions import GenException
from combine_and_shorten_definition import combine_and_shorten_definition
from word_manager import Word, WordManager
from draw import draw_full_summation_curve, \
                    draw_vertical_text, \
                    draw_bottom_summation_curve, \
                    draw_opened_top_summation_curve, \
                    draw_top_summation_curve

PROGRAM_FULLNAME = 'Chinese Worksheet Generator';
PROGRAM_WEBSITE = 'chineseworksheetgenerator.org';
MAKEMEAHANZI_NAME = 'Make Me a Hanzi';
CEDICT_NAME = 'CEDICT';
CHARACTERS_FILE = 'character_infos.json';
WORDS_FILE = 'word_infos.json';
SHEET_FILE = 'sheet.pdf';

PAGE_SIZE = A4;
CHARACTERS_PER_PAGE = 5;
GRID_OFFSET = 30;
RADICAL_HEIGHT = 30;
RADICAL_PINYIN_HEIGHT = 10;
CHARACTERS_PER_ROW = 10;
CHARACTER_ROW_WIDTH = PAGE_SIZE[0]-2*GRID_OFFSET;
SQUARE_SIZE = CHARACTER_ROW_WIDTH/CHARACTERS_PER_ROW;
CHARACTER_ROW_HEIGHT = SQUARE_SIZE*2+RADICAL_HEIGHT+RADICAL_PINYIN_HEIGHT;
SQUARE_PADDING = SQUARE_SIZE/15;
RADICAL_PADDING = RADICAL_HEIGHT/10;
FONT_NAME = 'SourceHanSansTC-Normal'
FONT_SIZE = 13;
HEADER_FONT_SIZE = 20;
FOOTER_FONT_SIZE = 10;
PAGE_NUMBER_FONT_SIZE = 10;
TEXT_PADDING = SQUARE_SIZE/4;
DEFINITION_PADDING = TEXT_PADDING*2;
STROKE_SIZE = SQUARE_SIZE*0.5; # size of stroke order character
STROKE_PADDING = SQUARE_PADDING*0.3;
STROKES_W = CHARACTER_ROW_WIDTH - SQUARE_SIZE - TEXT_PADDING;
MAX_STROKES = math.floor(STROKES_W / (STROKE_SIZE+STROKE_PADDING));
HEADER_PADDING = 40;
NAME_OFFSET = 300;
SCORE_OFFSET = 150;
PAGE_NUMBER_X_OFFSET = 40;
PAGE_NUMBER_Y_OFFSET = 20;
MAX_INPUT_CHARACTERS = 50;
MAX_TITLE_LENGTH = 20;
GUIDE_LINE_WIDTH = 5;
FIRST_CHARACTER_ROW_Y = PAGE_SIZE[1]-HEADER_PADDING-GRID_OFFSET/2;
WORD_FONT_SIZE = 11;
WORD_OFFSET = CHARACTER_ROW_HEIGHT/15;
SUMMATION_OFFSET = 3;
SUMMATION_FROM_X = GRID_OFFSET*0.4; # word summation
DEFINITION_SEPARATOR = ', ';

# TODO: rename to character
class character_info:
    def __init__(self, character, radical, pinyin, radical_pinyin, \
            definition, stroke_order):
        self.character = character;
        self.radical = radical;
        self.pinyin = pinyin;
        self.radical_pinyin = radical_pinyin;
        self.definition = definition;
        self.stroke_order = stroke_order;

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True);

def object_to_character_info(obj):
    return character_info(obj['character'], obj['radical'], obj['pinyin'], \
            obj['radical_pinyin'], obj['definition'], obj['stroke_order']);

class Guide(Enum):
    NONE = 1
    STAR = 2
    CROSS = 3
    CROSS_STAR = 4
    CHARACTER = 5

class InMemoryDataset:
    def __init__(self, dataset_path):
        with open(dataset_path, 'r', encoding='utf8') as dataset:
            self.lines = dataset.readlines();

    def get_character_json(self, character):
        for line in self.lines:
            if line == '':
                break;
            item = json.loads(line);
            if item['character'] == character:
                return item;
        return -1;

class Generator:
    def __init__(self, makemeahanzi_path):
        self._initialize_datasets(makemeahanzi_path);

    def _initialize_datasets(self, dataset_path):
        self.dictionary_dataset = InMemoryDataset(dataset_path + '/dictionary.txt')
        self.graphics_dataset = InMemoryDataset(dataset_path + '/graphics.txt')

    def _retrieve_info(self, dataset_path, character):
        d = self.dictionary_dataset.get_character_json(character);
        g = self.graphics_dataset.get_character_json(character);

        if d == -1 or g == -1:
            return -1;

        try:
            radical = d['radical'];
            pinyin = d['pinyin'];

            r = self.dictionary_dataset.get_character_json(radical);

            if r == -1:
                return -1;

            radical_pinyin = r['pinyin'];
            definition = d['definition'];

            stroke_order = g['strokes'];
            return character_info(character, radical, pinyin, radical_pinyin, \
                    definition, stroke_order);
        except KeyError:
            raise GenException('Invalid dataset data for character ' + character);
        
    def _create_character_svg(self, working_dir, character_info):
        self._create_stroke_svg(working_dir, character_info.character, character_info.stroke_order, \
                            len(character_info.stroke_order));

    def _create_radical_svg(self, dataset_path, working_dir, character_info):
        radical = character_info.radical;

        g = self.graphics_dataset.get_character_json(radical)
        if g == -1:
            raise GenException('Could not find data for radical ' + radical);
        stroke_order = g['strokes'];
        self._create_stroke_svg(working_dir, radical, stroke_order, \
                            len(stroke_order));

    def _create_stroke_svg(self, working_dir, filename, stroke_order, stroke_number, stroke_color="black"):
        output = '<svg viewBox="0 0 128 128">' \
                '<g transform="scale(0.125, -0.125) translate(0, -900)">'
        for j in range(stroke_number, len(stroke_order)):
            output += '\n<path fill=\"gray\" d=\"' + stroke_order[j] + '\"></path>';
        for j in range(0, stroke_number):
            output += '\n<path fill=\"' + stroke_color + '\" d=\"' + stroke_order[j] + '\"></path>';
        output += '</g>\n</svg>';
        with open(os.path.join(working_dir, filename + '.svg'), 'w') as svg:
            svg.write(output);

    def _create_stroke_order_svgs(self, working_dir, character_info, stroke_order_color):
        character = character_info.character;
        stroke_order = character_info.stroke_order;
        for i in range(0, len(stroke_order)+1):
            self._create_stroke_svg(working_dir, character + str(i), stroke_order, i, stroke_order_color);

    def _convert_svg_to_png(self, svg_path, png_path):
        quality = 100;
        with open(svg_path, 'r') as f:
            svg_data = '\n'.join(f.readlines());
        svg2png(bytestring=svg_data, write_to=png_path, \
                output_width=quality, output_height=quality);

    def _convert_svgs_to_pngs(self, working_dir):
        for file in self._list_files(working_dir, '.*\.svg'):
            file = os.path.join(working_dir, file[:-4]);
            self._convert_svg_to_png(file + '.svg', file + '.png');

    def delete_files(self, directory, pattern):
        for file in self._list_files(directory, pattern):
            os.remove(os.path.join(directory, file));

    def _list_files(self, directory, pattern):
        result = [];
        for f in os.listdir(directory):
            if re.match(pattern, f):
                result.append(f);
        return result;

    def _shorten_stroke_order(self, stroke_order, max_strokes):
        if len(stroke_order) <= max_strokes:
            return stroke_order;
        step = math.ceil(len(stroke_order) / max_strokes);
        new_stroke_order = [];
        for i in range(0, len(stroke_order), step):
            new_stroke_order.append(stroke_order[i]);
        if new_stroke_order[-1] != stroke_order[-1]:
            new_stroke_order.append(stroke_order[-1]);
        return new_stroke_order;

    def _draw_header(self, canvas, title, font_size, y):
        canvas.setFont(FONT_NAME, font_size);
        canvas.drawString(GRID_OFFSET, y, title);
        canvas.drawString(NAME_OFFSET, y, 'Name:');
        canvas.drawString(NAME_OFFSET + SCORE_OFFSET, y, 'Score:');

    def _draw_guide(self, canvas, x, y, guide, working_dir, character_info):
        if guide == Guide.CHARACTER:
            self._prefill_character(working_dir, canvas, x + SQUARE_PADDING, \
                                y - SQUARE_PADDING, \
                                character_info.character + '0.png');
            return;

        canvas.setDash(1, 2);
        canvas.setStrokeColor(CMYKColor(0, 0, 0, 0.2));

        if guide == Guide.STAR or guide == Guide.CROSS_STAR:
            x1 = x;
            y1 = y;
            x2 = x1 + SQUARE_SIZE;
            y2 = y - SQUARE_SIZE;
            canvas.line(x1, y1, x2, y2);
            canvas.line(x2, y1, x1, y2);
        if guide == Guide.CROSS or guide == Guide.CROSS_STAR:
            x1 = x;
            y1 = y - SQUARE_SIZE/2;
            x2 = x1 + SQUARE_SIZE;
            y2 = y1;
            canvas.line(x1, y1, x2, y2);
            x1 = x + SQUARE_SIZE/2;
            y1 = y;
            x2 = x1;
            y2 = y1 - SQUARE_SIZE;
            canvas.line(x1, y1, x2, y2);
            
        canvas.setDash();
        canvas.setStrokeColor(CMYKColor(0, 0, 0, 1));

    def _prefill_character(self, working_dir, canvas, x, y, filename):
        size = SQUARE_SIZE - 2*SQUARE_PADDING
        canvas.drawImage(os.path.join(working_dir, filename), \
                x, \
                y - size, \
                size, \
                size, mask='auto');

    def _draw_character_row(self, working_dir, canvas, character_info, y, guide): #TODO: refactor
        character_y = y - SQUARE_SIZE;
        radical_y = character_y - RADICAL_HEIGHT;
        radical_pinyin_y = radical_y - RADICAL_PINYIN_HEIGHT

        # draw layout
        canvas.rect(GRID_OFFSET, radical_pinyin_y, \
                SQUARE_SIZE, SQUARE_SIZE + RADICAL_HEIGHT + RADICAL_PINYIN_HEIGHT);
        canvas.rect(GRID_OFFSET+SQUARE_SIZE, radical_pinyin_y, \
                CHARACTER_ROW_WIDTH-SQUARE_SIZE, SQUARE_SIZE + RADICAL_HEIGHT \
                + RADICAL_PINYIN_HEIGHT);
        for i in range(0, int(CHARACTER_ROW_WIDTH/SQUARE_SIZE)):
            canvas.rect(GRID_OFFSET + i*SQUARE_SIZE, \
                    radical_pinyin_y - SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE);
            self._draw_guide(canvas, GRID_OFFSET + i*SQUARE_SIZE, radical_pinyin_y, guide, working_dir, character_info);

        if guide != Guide.CHARACTER:
            self._prefill_character(working_dir, canvas, GRID_OFFSET + SQUARE_PADDING, \
                                radical_pinyin_y - SQUARE_PADDING, \
                                character_info.character + '0.png');

        # draw character
        character = os.path.join(working_dir, character_info.character + '.png');
        canvas.drawImage(character, \
                GRID_OFFSET + SQUARE_PADDING, \
                character_y + SQUARE_PADDING, \
                SQUARE_SIZE - 2*SQUARE_PADDING, \
                SQUARE_SIZE - 2*SQUARE_PADDING, mask='auto');

        # draw radical
        should_draw_radical = len(character_info.radical_pinyin) > 0;
        if should_draw_radical:
            radical_size = RADICAL_HEIGHT-2*RADICAL_PADDING;
            radical_x = GRID_OFFSET + (SQUARE_SIZE - radical_size)/2
            radical_y += RADICAL_PADDING;
            radical = os.path.join(working_dir, character_info.radical + '.png');
            canvas.drawImage(radical, \
                    radical_x, radical_y, radical_size, radical_size, mask='auto');

        # draw radical pinyin
        canvas.setFont(FONT_NAME, FONT_SIZE);
        if should_draw_radical:
            radical_pinyin = character_info.radical_pinyin[0];
            radical_pinyin_w = stringWidth(radical_pinyin, FONT_NAME, FONT_SIZE);
            radical_pinyin_x = GRID_OFFSET + (SQUARE_SIZE - radical_pinyin_w) / 2;
            radical_pinyin_y += SQUARE_PADDING;
            canvas.drawString(radical_pinyin_x, radical_pinyin_y, radical_pinyin);

        # draw pinyin
        pinyin = character_info.pinyin[0];
        pinyin_w = stringWidth(pinyin, FONT_NAME, FONT_SIZE);
        pinyin_h = FONT_SIZE*0.8; # TODO
        pinyin_x = GRID_OFFSET + SQUARE_SIZE + TEXT_PADDING;
        pinyin_y = y - TEXT_PADDING - pinyin_h;
        canvas.drawString(pinyin_x, pinyin_y, pinyin);

        # draw definition
        definition_x = pinyin_x + pinyin_w + DEFINITION_PADDING;
        definition_y = pinyin_y;
        max_w = CHARACTER_ROW_WIDTH - SQUARE_SIZE - TEXT_PADDING \
                - pinyin_w - DEFINITION_PADDING - TEXT_PADDING;
        definition = character_info.definition.replace(';',',').split(',');
        definition = combine_and_shorten_definition(definition, \
                        DEFINITION_SEPARATOR, \
                        max_w, FONT_NAME, FONT_SIZE).text;
        canvas.drawString(definition_x, definition_y, definition);

        # draw stroke order
        character = character_info.character;
        stroke_y = y - TEXT_PADDING - pinyin_h - TEXT_PADDING - STROKE_SIZE;
        stroke_x = pinyin_x;
        stroke_order = sorted(self._list_files(working_dir, character + '.*\.png'))[2:];
        stroke_order = [x[1:-4] for x in stroke_order];
        stroke_order = sorted([int(x) for x in stroke_order]); # sort numerically
        stroke_order = self._shorten_stroke_order(stroke_order, MAX_STROKES);
        for stroke in stroke_order:
            stroke = os.path.join(working_dir, character + str(stroke) + '.png');
            canvas.drawImage(stroke, \
                    stroke_x, stroke_y, STROKE_SIZE, STROKE_SIZE, mask='auto');
            stroke_x += STROKE_SIZE + 2*STROKE_PADDING;

    def _draw_footer(self, canvas, font_size, y):
        text1 = 'Created with ' + PROGRAM_FULLNAME;
        text2 = PROGRAM_WEBSITE;
        text2_w = stringWidth(text2, FONT_NAME, FOOTER_FONT_SIZE);
        text2_x = PAGE_SIZE[0]-GRID_OFFSET-text2_w;
        canvas.setFont(FONT_NAME, font_size);
        canvas.drawString(GRID_OFFSET, y, text1);
        canvas.drawString(text2_x, y, text2);
        y -= 0.2*FONT_SIZE;
        canvas.linkURL('www.' + text2, (text2_x, y, \
                        text2_x + text2_w, y + 0.8*FONT_SIZE));

    def _draw_page_number(self, canvas, page_number, font_size):
        canvas.setFont(FONT_NAME, font_size);
        canvas.drawString(PAGE_SIZE[0]-PAGE_NUMBER_X_OFFSET, PAGE_NUMBER_Y_OFFSET, \
                str(int(page_number)));

    def _draw_words(self, canvas, character_infos, words, page_number, spanning_map):
        page_index = page_number - 1;
        min_index = CHARACTERS_PER_PAGE * page_index;
        max_index = min_index + CHARACTERS_PER_PAGE - 1;

        # draw bottom words
        for word in words:
            to = word.character_end_index;
            if word.character_begin_index < min_index and \
                to >= min_index and to <= max_index:
                self._draw_bottom_word(canvas, to % CHARACTERS_PER_PAGE, \
                                spanning_map[word].bottom_translation);

        # draw full words
        for word in words:
            begin = word.character_begin_index;
            end = word.character_end_index;
            if begin >= min_index and begin <= max_index and \
                end >= min_index and end <= max_index:
                self._draw_full_word(canvas, begin % CHARACTERS_PER_PAGE, \
                                end % CHARACTERS_PER_PAGE, word);

        # draw top words
        for word in words:
            begin = word.character_begin_index;
            if word.character_end_index > max_index and \
                begin >= min_index and begin <= max_index:
                self._draw_top_word(canvas, begin % CHARACTERS_PER_PAGE, \
                                spanning_map[word].top_translation);

    def _draw_top_word(self, canvas, begin_index, top_translation):
        yto = FIRST_CHARACTER_ROW_Y - begin_index*CHARACTER_ROW_HEIGHT;
        yto_word = yto - WORD_OFFSET;
        ymid = int(yto_word/2);
        if top_translation == '':
            draw_opened_top_summation_curve(canvas, \
                                            SUMMATION_FROM_X+SUMMATION_OFFSET, \
                                            SUMMATION_OFFSET, GRID_OFFSET, \
                                            yto);
            return;
        draw_vertical_text(canvas, FONT_NAME, WORD_FONT_SIZE, SUMMATION_FROM_X, \
                            ymid, top_translation);
        draw_top_summation_curve(canvas,
                                    SUMMATION_FROM_X+SUMMATION_OFFSET, \
                                    SUMMATION_OFFSET, GRID_OFFSET, \
                                    yto);

    def _draw_bottom_word(self, canvas, end_index, bottom_translation):
        yfrom = FIRST_CHARACTER_ROW_Y - (end_index+1)*CHARACTER_ROW_HEIGHT;
        yfrom_word = yfrom + WORD_OFFSET;
        ymid = PAGE_SIZE[1] - int((PAGE_SIZE[1]-yfrom_word)/2);
        draw_vertical_text(canvas, FONT_NAME, WORD_FONT_SIZE, \
                            SUMMATION_FROM_X, ymid, bottom_translation);
        draw_bottom_summation_curve(canvas, SUMMATION_FROM_X+SUMMATION_OFFSET, \
                                    yfrom, GRID_OFFSET, \
                                    PAGE_SIZE[1]-SUMMATION_OFFSET);

    def _draw_full_word(self, canvas, begin_index, end_index, word):
        h = CHARACTER_ROW_HEIGHT*(end_index-begin_index+1);
        h_word = h-2*WORD_OFFSET;
        yto = FIRST_CHARACTER_ROW_Y-begin_index*CHARACTER_ROW_HEIGHT;
        ymid = yto-WORD_OFFSET-h_word/2;
        text = combine_and_shorten_definition(word.definition, \
                                                DEFINITION_SEPARATOR, h, \
                                                FONT_NAME, WORD_FONT_SIZE).text;
        draw_vertical_text(canvas, FONT_NAME, WORD_FONT_SIZE, \
                                    SUMMATION_FROM_X, ymid, text);
        draw_full_summation_curve(canvas, SUMMATION_FROM_X+SUMMATION_OFFSET, \
                                    yto-h, GRID_OFFSET, yto);
    
    # TODO: this should return list of words not found
    # and main should display them as warnings
    def generate_infos(self, makemeahanzi_path, cedict_path, working_dir, characters):
        if ( len(characters) == 0 ):
            raise GenException('No characters provided');
        manager = WordManager(characters, cedict_path);
        characters = manager.get_characters();
        words = manager.get_words();
        if len(characters) > MAX_INPUT_CHARACTERS:
            raise GenException('Maximum number of characters exceeded (' + \
                    str(len(characters)) + \
                    '/' + str(MAX_INPUT_CHARACTERS) + ')');

        self._generate_character_infos(working_dir, characters, makemeahanzi_path);
        self._generate_word_infos(working_dir, words);

    def _generate_character_infos(self, working_dir, characters, makemeahanzi_path):
        with open(os.path.join(working_dir, CHARACTERS_FILE), 'w') as cf:
            for i in range(len(characters)):
                character = characters[i];
                info = self._retrieve_info(makemeahanzi_path, character);
                if info == -1:
                    raise GenException('Could not find data for character ' + \
                            character);
                j = info.toJSON();
                cf.write(j + '\n');

    def _generate_word_infos(self, working_dir, words):
        with open(os.path.join(working_dir, WORDS_FILE), 'w') as wf:
            for word in words:
                j = word.toJSON();
                wf.write(j + '\n');

    def _load_data_from_json_file(self, working_dir, filename, parse_function):
        data = [];
        with open(os.path.join(working_dir, filename), 'r') as f:
            while 1:
                line = f.readline();
                if line == '':
                    break;
                j = json.loads(line);
                data.append(parse_function(j));
        return data;

    def _filter_out_words_with_empty_definition(self, words):
        filtered = [];
        for word in words:
            if len(word.definition) != 0:
                filtered.append(word);
        return filtered;

    # returns map from word to spanning translation
    # not all words have a spanning translation
    def _get_spanning_translations(self, characters, words):
        # TODO: combine_... may throw!
        spanning_translations = dict();

        words_with_spanning_translations = [];
        for word in words:
            from_page_idx = int(word.character_begin_index / CHARACTERS_PER_PAGE);
            to_page_idx = int(word.character_end_index / CHARACTERS_PER_PAGE);
            if from_page_idx == to_page_idx-1:
                words_with_spanning_translations.append(word);
        
        for word in words_with_spanning_translations:
            # bottom translation
            to_idx = word.character_end_index % CHARACTERS_PER_PAGE;
            yfrom = FIRST_CHARACTER_ROW_Y - (to_idx+1)*CHARACTER_ROW_HEIGHT + \
                    WORD_OFFSET;
            max_w = PAGE_SIZE[1]-yfrom;
            result = combine_and_shorten_definition(word.definition, \
                                                    DEFINITION_SEPARATOR, \
                                                    max_w, \
                                                    FONT_NAME, WORD_FONT_SIZE);
            bottom_translation = result.text;

            # top translation
            orig_num_words = len(word.definition);
            num_words = result.num_words;
            if  orig_num_words == num_words:
                tr = SpanningTranslation('', bottom_translation);
                spanning_translations[word] = tr;
                continue;
            definition = word.definition[num_words:orig_num_words]; # rest
            from_idx = word.character_begin_index % CHARACTERS_PER_PAGE;
            max_w = FIRST_CHARACTER_ROW_Y-from_idx*CHARACTER_ROW_HEIGHT - \
                    WORD_OFFSET;
            result = combine_and_shorten_definition(definition, \
                                                    DEFINITION_SEPARATOR, \
                                                    max_w, \
                                                    FONT_NAME, WORD_FONT_SIZE);
            top_translation = result.text;
            tr = SpanningTranslation(top_translation, bottom_translation);
            spanning_translations[word] = tr;
        return spanning_translations;

    def generate_sheet(self, makemeahanzi_path, working_dir, title, guide, stroke_order_color):
        if len(title) > MAX_TITLE_LENGTH:
            raise GenException('Title length exceeded (' + str(len(title)) + \
                    '/' + str(MAX_TITLE_LENGTH) + ')');

        character_infos = [];
        words = [];

        character_infos = self._load_data_from_json_file(working_dir, CHARACTERS_FILE, \
                                                    object_to_character_info);
        words = self._load_data_from_json_file(working_dir, WORDS_FILE, Word.fromJSON);
        words = self._filter_out_words_with_empty_definition(words);

        c = canvas.Canvas(os.path.join(working_dir, SHEET_FILE), PAGE_SIZE);
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_NAME + '.ttf'));

        words_with_spanning_translation = self._get_spanning_translations( \
                                            character_infos, words);

        self._draw_header(c, title, HEADER_FONT_SIZE, \
                PAGE_SIZE[1]-HEADER_PADDING);
        for i in range(len(character_infos)):
            i_mod = i % CHARACTERS_PER_PAGE;
            page_number = int(i / CHARACTERS_PER_PAGE + 1);
            if i != 0 and i_mod == 0:
                self._draw_footer(c, FOOTER_FONT_SIZE, y-CHARACTER_ROW_HEIGHT - \
                        GRID_OFFSET/2);
                self._draw_page_number(c, i / CHARACTERS_PER_PAGE, PAGE_NUMBER_FONT_SIZE);
                self._draw_words(c, character_infos, words, page_number-1, \
                            words_with_spanning_translation);
                c.showPage();
                self._draw_header(c, title, HEADER_FONT_SIZE, \
                        PAGE_SIZE[1]-HEADER_PADDING);
            info = character_infos[i];
            self._create_character_svg(working_dir, info);
            self._create_radical_svg(makemeahanzi_path, working_dir, info);
            self._create_stroke_order_svgs(working_dir, info, stroke_order_color);
            self._convert_svgs_to_pngs(working_dir);
            y = FIRST_CHARACTER_ROW_Y-i_mod*CHARACTER_ROW_HEIGHT;
            self._draw_character_row(working_dir, c, info, y, guide);
            self.delete_files(working_dir, '.*\.svg');
            self.delete_files(working_dir, '.*\.png');
        
        y = PAGE_SIZE[1]-HEADER_PADDING-GRID_OFFSET/2 - \
            (CHARACTERS_PER_PAGE-1)*CHARACTER_ROW_HEIGHT;
        # TODO: extract
        self._draw_footer(c, FOOTER_FONT_SIZE, y-CHARACTER_ROW_HEIGHT - \
                        GRID_OFFSET/2);
        self._draw_page_number(c, page_number, PAGE_NUMBER_FONT_SIZE);
        self._draw_words(c, character_infos, words, page_number, \
                words_with_spanning_translation);
        c.setTitle(title);
        c.showPage();
        c.save();

    def get_guide(self, guide_str):
        if guide_str == '' or guide_str == Guide.NONE.name.lower():
            return Guide.NONE;
        elif guide_str == Guide.STAR.name.lower():
            return Guide.STAR;
        elif guide_str == Guide.CROSS.name.lower():
            return Guide.CROSS;
        elif guide_str == Guide.CROSS_STAR.name.lower():
            return Guide.CROSS_STAR;
        elif guide_str == Guide.CHARACTER.name.lower():
            return Guide.CHARACTER;
        else:
            raise GenException('Invalid guide ' + guide_str);