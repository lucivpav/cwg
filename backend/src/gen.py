#!/usr/bin/python3

import sys
import json
import glob
import os
import math
import getopt
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

PROGRAM_NAME = 'gen.py';
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

def usage():
    print('usage: ' + PROGRAM_NAME + '\n' + \
            ' <default>\n' + \
            '   --makemeahanzi=<' + MAKEMEAHANZI_NAME + ' path>\n' + \
            '   --cedict=<' + CEDICT_NAME + ' path>\n' + \
            '   --characters=<chinese characters>\n' + \
            '   [--title=<custom title>]\n' + \
            '   [--guide=star]\n' + \
            ' --info\n' + \
            '   --makemeahanzi=<' + MAKEMEAHANZI_NAME + ' path>\n' + \
            '   --cedict=<' + CEDICT_NAME + ' path>\n' + \
            '   --characters=<chinese characters>\n' + \
            ' --sheet\n' + \
            '   --makemeahanzi=<' + MAKEMEAHANZI_NAME + ' path>\n' + \
            '   [--title=<custom title>]\n' + \
            '   [--guide=star]');

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

def get_character_json(file, character):
    while 1:
        line = file.readline();
        if line == '':
            break;
        item = json.loads(line);
        if item['character'] == character:
            return item;
    return -1;

def get_dictionary_json(dataset_path, character):
    with open(dataset_path + '/dictionary.txt', 'r', encoding='utf8') as dictionary:
        return get_character_json(dictionary, character);

def get_graphics_json(dataset_path, character):
    with open(dataset_path + '/graphics.txt', 'r', encoding='utf8') as graphics:
        return get_character_json(graphics, character);

def retrieve_info(dataset_path, character):
    d = get_dictionary_json(dataset_path, character);
    g = get_graphics_json(dataset_path, character);

    if d == -1 or g == -1:
        return -1;

    try:
        radical = d['radical'];
        pinyin = d['pinyin'];

        r = get_dictionary_json(dataset_path, radical);

        if r == -1:
            return -1;

        radical_pinyin = r['pinyin'];
        definition = d['definition'];

        stroke_order = g['strokes'];
        return character_info(character, radical, pinyin, radical_pinyin, \
                definition, stroke_order);
    except KeyError:
        raise GenException('Invalid dataset data for character ' + character);
    
def create_character_svg(working_dir, character_info):
    create_stroke_svg(working_dir, character_info.character, character_info.stroke_order, \
                        len(character_info.stroke_order));

def create_radical_svg(dataset_path, working_dir, character_info):
    radical = character_info.radical;

    g = get_graphics_json(dataset_path, radical)
    if g == -1:
        raise GenException('Could not find data for radical ' + radical);
    stroke_order = g['strokes'];
    create_stroke_svg(working_dir, radical, stroke_order, \
                        len(stroke_order));

def create_stroke_svg(working_dir, filename, stroke_order, stroke_number):
    output = '<svg viewBox="0 0 128 128">' \
            '<g transform="scale(0.125, -0.125) translate(0, -900)">'
    for j in range(stroke_number, len(stroke_order)):
        output += '\n<path fill=\"gray\" d=\"' + stroke_order[j] + '\"></path>';
    for j in range(0, stroke_number):
        output += '\n<path d=\"' + stroke_order[j] + '\"></path>';
    output += '</g>\n</svg>';
    with open(os.path.join(working_dir, filename + '.svg'), 'w') as svg:
        svg.write(output);

def create_stroke_order_svgs(working_dir, character_info):
    character = character_info.character;
    stroke_order = character_info.stroke_order;
    for i in range(0, len(stroke_order)+1):
        create_stroke_svg(working_dir, character + str(i), stroke_order, i);

def convert_svg_to_png(svg_path, png_path):
    quality = 100;
    with open(svg_path, 'r') as f:
        svg_data = '\n'.join(f.readlines());
    svg2png(bytestring=svg_data, write_to=png_path, \
            output_width=quality, output_height=quality);

def convert_svgs_to_pngs(working_dir):
    for file in list_files(working_dir, '.*\.svg'):
        file = os.path.join(working_dir, file[:-4]);
        convert_svg_to_png(file + '.svg', file + '.png');

def delete_files(directory, pattern):
    for file in list_files(directory, pattern):
        os.remove(os.path.join(directory, file));

def list_files(directory, pattern):
    result = [];
    for f in os.listdir(directory):
        if re.match(pattern, f):
            result.append(f);
    return result;

def shorten_stroke_order(stroke_order, max_strokes):
    if len(stroke_order) <= max_strokes:
        return stroke_order;
    step = math.ceil(len(stroke_order) / max_strokes);
    new_stroke_order = [];
    for i in range(0, len(stroke_order), step):
        new_stroke_order.append(stroke_order[i]);
    if new_stroke_order[-1] != stroke_order[-1]:
        new_stroke_order.append(stroke_order[-1]);
    return new_stroke_order;

def draw_header(canvas, title, font_size, y):
    canvas.setFont(FONT_NAME, font_size);
    canvas.drawString(GRID_OFFSET, y, title);
    canvas.drawString(NAME_OFFSET, y, 'Name:');
    canvas.drawString(NAME_OFFSET + SCORE_OFFSET, y, 'Score:');

def draw_guide(canvas, x, y, guide):
    canvas.setDash(1, 2);
    canvas.setStrokeColor(CMYKColor(0, 0, 0, 0.2));

    if guide == Guide.STAR:
        x1 = x;
        y1 = y;
        x2 = x1 + SQUARE_SIZE;
        y2 = y - SQUARE_SIZE;
        canvas.line(x1, y1, x2, y2);
        canvas.line(x2, y1, x1, y2);
    elif guide == Guide.CROSS:
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

def prefill_character(working_dir, canvas, x, y, filename):
    size = SQUARE_SIZE - 2*SQUARE_PADDING
    canvas.drawImage(os.path.join(working_dir, filename), \
            x, \
            y - size, \
            size, \
            size, mask='auto');

def draw_character_row(working_dir, canvas, character_info, y, guide): #TODO: refactor
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
        draw_guide(canvas, GRID_OFFSET + i*SQUARE_SIZE, radical_pinyin_y, guide);

    prefill_character(working_dir, canvas, GRID_OFFSET + SQUARE_PADDING, \
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
    stroke_order = sorted(list_files(working_dir, character + '.*\.png'))[2:];
    stroke_order = [x[1:-4] for x in stroke_order];
    stroke_order = sorted([int(x) for x in stroke_order]); # sort numerically
    stroke_order = shorten_stroke_order(stroke_order, MAX_STROKES);
    for stroke in stroke_order:
        stroke = os.path.join(working_dir, character + str(stroke) + '.png');
        canvas.drawImage(stroke, \
                stroke_x, stroke_y, STROKE_SIZE, STROKE_SIZE, mask='auto');
        stroke_x += STROKE_SIZE + 2*STROKE_PADDING;

def draw_footer(canvas, font_size, y):
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

def draw_page_number(canvas, page_number, font_size):
    canvas.setFont(FONT_NAME, font_size);
    canvas.drawString(PAGE_SIZE[0]-PAGE_NUMBER_X_OFFSET, PAGE_NUMBER_Y_OFFSET, \
            str(int(page_number)));

def draw_words(canvas, character_infos, words, page_number, spanning_map):
    page_index = page_number - 1;
    min_index = CHARACTERS_PER_PAGE * page_index;
    max_index = min_index + CHARACTERS_PER_PAGE - 1;

    # draw bottom words
    for word in words:
        to = word.character_end_index;
        if word.character_begin_index < min_index and \
            to >= min_index and to <= max_index:
            draw_bottom_word(canvas, to % CHARACTERS_PER_PAGE, \
                            spanning_map[word].bottom_translation);

    # draw full words
    for word in words:
        begin = word.character_begin_index;
        end = word.character_end_index;
        if begin >= min_index and begin <= max_index and \
            end >= min_index and end <= max_index:
            draw_full_word(canvas, begin % CHARACTERS_PER_PAGE, \
                            end % CHARACTERS_PER_PAGE, word);

    # draw top words
    for word in words:
        begin = word.character_begin_index;
        if word.character_end_index > max_index and \
            begin >= min_index and begin <= max_index:
            draw_top_word(canvas, begin % CHARACTERS_PER_PAGE, \
                            spanning_map[word].top_translation);

def draw_top_word(canvas, begin_index, top_translation):
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

def draw_bottom_word(canvas, end_index, bottom_translation):
    yfrom = FIRST_CHARACTER_ROW_Y - (end_index+1)*CHARACTER_ROW_HEIGHT;
    yfrom_word = yfrom + WORD_OFFSET;
    ymid = PAGE_SIZE[1] - int((PAGE_SIZE[1]-yfrom_word)/2);
    draw_vertical_text(canvas, FONT_NAME, WORD_FONT_SIZE, \
                        SUMMATION_FROM_X, ymid, bottom_translation);
    draw_bottom_summation_curve(canvas, SUMMATION_FROM_X+SUMMATION_OFFSET, \
                                yfrom, GRID_OFFSET, \
                                PAGE_SIZE[1]-SUMMATION_OFFSET);

def draw_full_word(canvas, begin_index, end_index, word):
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
def generate_infos(makemeahanzi_path, cedict_path, working_dir, characters):
    if ( len(characters) == 0 ):
        raise GenException('No characters provided');
    manager = WordManager(characters, cedict_path);
    characters = manager.get_characters();
    words = manager.get_words();
    if len(characters) > MAX_INPUT_CHARACTERS:
        raise GenException('Maximum number of characters exceeded (' + \
                str(len(characters)) + \
                '/' + str(MAX_INPUT_CHARACTERS) + ')');

    generate_character_infos(working_dir, characters, makemeahanzi_path);
    generate_word_infos(working_dir, words);

def generate_character_infos(working_dir, characters, makemeahanzi_path):
    with open(os.path.join(working_dir, CHARACTERS_FILE), 'w') as cf:
        for i in range(len(characters)):
            character = characters[i];
            info = retrieve_info(makemeahanzi_path, character);
            if info == -1:
                raise GenException('Could not find data for character ' + \
                        character);
            j = info.toJSON();
            cf.write(j + '\n');

def generate_word_infos(working_dir, words):
    with open(os.path.join(working_dir, WORDS_FILE), 'w') as wf:
        for word in words:
            j = word.toJSON();
            wf.write(j + '\n');

def load_data_from_json_file(working_dir, filename, parse_function):
    data = [];
    with open(os.path.join(working_dir, filename), 'r') as f:
        while 1:
            line = f.readline();
            if line == '':
                break;
            j = json.loads(line);
            data.append(parse_function(j));
    return data;

def filter_out_words_with_empty_definition(words):
    filtered = [];
    for word in words:
        if len(word.definition) != 0:
            filtered.append(word);
    return filtered;

# returns map from word to spanning translation
# not all words have a spanning translation
def get_spanning_translations(characters, words):
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

def generate_sheet(makemeahanzi_path, working_dir, title, guide):
    if len(title) > MAX_TITLE_LENGTH:
        raise GenException('Title length exceeded (' + str(len(title)) + \
                '/' + str(MAX_TITLE_LENGTH) + ')');

    character_infos = [];
    words = [];

    character_infos = load_data_from_json_file(working_dir, CHARACTERS_FILE, \
                                                object_to_character_info);
    words = load_data_from_json_file(working_dir, WORDS_FILE, Word.fromJSON);
    words = filter_out_words_with_empty_definition(words);

    c = canvas.Canvas(os.path.join(working_dir, SHEET_FILE), PAGE_SIZE);
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_NAME + '.ttf'));

    words_with_spanning_translation = get_spanning_translations( \
                                        character_infos, words);

    draw_header(c, title, HEADER_FONT_SIZE, \
            PAGE_SIZE[1]-HEADER_PADDING);
    for i in range(len(character_infos)):
        i_mod = i % CHARACTERS_PER_PAGE;
        page_number = int(i / CHARACTERS_PER_PAGE + 1);
        if i != 0 and i_mod == 0:
            draw_footer(c, FOOTER_FONT_SIZE, y-CHARACTER_ROW_HEIGHT - \
                    GRID_OFFSET/2);
            draw_page_number(c, i / CHARACTERS_PER_PAGE, PAGE_NUMBER_FONT_SIZE);
            draw_words(c, character_infos, words, page_number-1, \
                        words_with_spanning_translation);
            c.showPage();
            draw_header(c, title, HEADER_FONT_SIZE, \
                    PAGE_SIZE[1]-HEADER_PADDING);
        info = character_infos[i];
        create_character_svg(working_dir, info);
        create_radical_svg(makemeahanzi_path, working_dir, info);
        create_stroke_order_svgs(working_dir, info);
        convert_svgs_to_pngs(working_dir);
        y = FIRST_CHARACTER_ROW_Y-i_mod*CHARACTER_ROW_HEIGHT;
        draw_character_row(working_dir, c, info, y, guide);
        delete_files(working_dir, '.*\.svg');
        delete_files(working_dir, '.*\.png');
    
    y = PAGE_SIZE[1]-HEADER_PADDING-GRID_OFFSET/2 - \
        (CHARACTERS_PER_PAGE-1)*CHARACTER_ROW_HEIGHT;
    # TODO: extract
    draw_footer(c, FOOTER_FONT_SIZE, y-CHARACTER_ROW_HEIGHT - \
                    GRID_OFFSET/2);
    draw_page_number(c, page_number, PAGE_NUMBER_FONT_SIZE);
    draw_words(c, character_infos, words, page_number, \
            words_with_spanning_translation);
    c.setTitle(title);
    c.showPage();
    c.save();

def get_guide(guide_str):
    if guide_str == '' or guide_str == Guide.NONE.name.lower():
        return Guide.NONE;
    elif guide_str == Guide.STAR.name.lower():
        return Guide.STAR;
    elif guide_str == Guide.CROSS.name.lower():
        return Guide.CROSS;
    else:
        raise GenException('Invalid guide ' + guide_str);

def main(argv):
    makemeahanzi = '';
    cedict = ''
    characters = '';
    title = '';
    guide = '';
    info_mode = False;
    sheet_mode = False;
    opts, args = getopt.getopt(argv, '', \
            ['makemeahanzi=', 'cedict=', 'characters=', \
            'title=', 'guide=', 'info', 'sheet']);
    for opt, arg in opts:
        if opt == '--makemeahanzi':
            makemeahanzi = arg;
        elif opt == '--cedict':
            cedict = arg;
        elif opt == '--characters':
            characters = arg;
        elif opt == '--title':
            title = arg;
        elif opt == '--guide':
            guide = arg;
        elif opt == '--info':
            info_mode = True;
        elif opt == '--sheet':
            sheet_mode = True;
        else:
            usage();
            exit(1);

    if info_mode == sheet_mode:
        info_mode = True;
        sheet_mode = True;

    if makemeahanzi == '' \
            or (info_mode and cedict == '') \
            or (info_mode and characters == '') \
            or (sheet_mode and not info_mode and characters != '') \
            or (info_mode and not sheet_mode and title != ''):
        usage();
        exit(1);

    working_dir = os.getcwd();
    try:
        guide_val = get_guide(guide);
        if info_mode == sheet_mode:
            generate_infos(makemeahanzi, cedict, working_dir, characters);
            generate_sheet(makemeahanzi, working_dir, title, guide_val);
            delete_files(working_dir, CHARACTERS_FILE.replace('.', '\.'));
            delete_files(working_dir, WORDS_FILE.replace('.', '\.'));
        elif info_mode:
            generate_infos(makemeahanzi, cedict, working_dir, characters);
        else:
            generate_sheet(makemeahanzi, working_dir, title, guide_val);
    except GenException as e:
        print(str(e));

if __name__ == '__main__':
    main(sys.argv[1:]);
