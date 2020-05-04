#!/usr/bin/python3
from flask import Flask, request, send_file
from flask_restful import Resource, Api
from flask_jsonpify import jsonpify
from flask_cors import CORS, cross_origin
import json
import os
import tempfile
import shutil
import getopt
import sys
import datetime
from exceptions import GenException
from threading import Lock
from gen import generate_infos, generate_sheet, \
                CHARACTERS_FILE, WORDS_FILE, SHEET_FILE, get_guide, \
                MAKEMEAHANZI_NAME, CEDICT_NAME

MAKEMEAHANZI_PATH = '';
CEDICT_PATH = '';
PROGRAM_NAME = 'server.py';
LOG_FILE = 'errors.log';
COUNT_FILE = 'count.txt'
INTERNAL_ERROR_MSG = 'Failed to generate sheet. Please enter different configuration or try again later.';

count_lock = Lock();
error_lock = Lock();

class GenerateInfos(Resource):
    def post(self):
        characters = request.args.get('characters')
        data = request.get_json()
        characters = data['characters']
        if characters == None or len(characters) == 0:
            return jsonpify({'error': 'No characters provided'});
        characters = characters.replace(' ', '');
        path = tempfile.mkdtemp();
        error_msg = 'generate_infos ' + characters + '\n';
        try:
            generate_infos(MAKEMEAHANZI_PATH, CEDICT_PATH, path, characters);
        except GenException as e:
            log_error(path, error_msg + str(e));
            return jsonpify({'error': str(e)});
        except Exception as e:
            log_error(path, error_msg + str(e));
            return jsonpify({'error': INTERNAL_ERROR_MSG});

        characters = get_characters(path);
        words = get_words(path, characters);

        result = { 'id': path, 'characters': characters, 'words': words };
        return jsonpify(result);

class GenerateSheet(Resource):
    def post(self):
        temp_path = request.args.get('id');
        guide = request.args.get('guide');
        title = request.args.get('title');
        data = request.get_json()
        if temp_path == None or len(temp_path) == 0 or \
            guide == None or len(guide) == 0 or \
            title == None:
            return jsonpify({'error': 'Invalid parameters'});
        try:
            guide = get_guide(guide);
        except GenException as e:
            return jsonpify({'error': str(e)});

        update_characters_file(temp_path, data);
        update_words_file(temp_path, data);

        error_msg = 'generate_sheet ' + title + ' ' + str(guide) + '\n';
        try:
            generate_sheet(MAKEMEAHANZI_PATH, temp_path, title, guide);
        except GenException as e:
            log_error(temp_path, error_msg + str(e));
            return jsonpify({'error': str(e)});
        except Exception as e:
            log_error(temp_path, error_msg + str(e));
            return jsonpify({'error': INTERNAL_ERROR_MSG});

        # increment count
        count_lock.acquire();
        try:
            with open(COUNT_FILE, 'r') as f:
                count = int(f.read().strip());
            with open(COUNT_FILE, 'w') as f:
                f.write(str(count+1));
        except:
            pass;
        finally:
            count_lock.release();

        return jsonpify({});

class RetrieveSheet(Resource):
    def get(self):
        temp_path = request.args.get('id');
        pdf = send_file(os.path.join(temp_path, SHEET_FILE), \
                        mimetype='application/pdf', \
                        cache_timeout=-1);
        return pdf;

class RetrieveCount(Resource):
    def get(self):
        count_lock.acquire();
        try:
            with open(COUNT_FILE, 'r') as f:
                count = f.read().strip();
                return jsonpify({'count': count});
        except:
            return jsonpify({'count': 'N/A'});
        finally:
            count_lock.release();

def update_characters_file(working_directory, request_body):
    file_path = os.path.join(working_directory, CHARACTERS_FILE);
    new_file_name = 'new_' + CHARACTERS_FILE;
    new_file_path = os.path.join(working_directory, new_file_name);
    with open(file_path, 'r') as f_orig:
        with open(new_file_path, 'w') as f_new:
            i = 0;
            while 1:
                line = f_orig.readline();
                if line == '':
                    break;
                info = json.loads(line);
                pinyin = request_body['characters'][info["character"]]['pinyin']
                definition = request_body['characters'][info["character"]]['definition']
                info['pinyin'] = [pinyin];
                info['definition'] = definition;
                f_new.write(json.dumps(info) + '\n');
                i += 1;
    shutil.copy(new_file_path, file_path);

def update_words_file(working_directory, request_body):
    try:
        words_definitions = request_body['words']
    except:
        # no words in this file
        return
    file_path = os.path.join(working_directory, WORDS_FILE);
    new_file_name = 'new_' + WORDS_FILE;
    new_file_path = os.path.join(working_directory, new_file_name);
    with open(file_path, 'r') as f_orig:
        with open(new_file_path, 'w') as f_new:
            i = 0;
            while 1:
                line = f_orig.readline();
                if line == '':
                    break;
                word = json.loads(line);
                word['definition'] = words_definitions[i];
                f_new.write(json.dumps(word) + '\n');
                i += 1;
    shutil.copy(new_file_path, file_path);

def get_characters(working_directory):
    characters = [];
    with open(os.path.join(working_directory, CHARACTERS_FILE)) as f:
        while 1:
            line = f.readline();
            if line == '':
                break;
            info = json.loads(line);
            character = info['character'];
            definition = info['definition'];
            pinyin = info['pinyin'][0];
            i = {'character': character, \
                    'definition': definition, \
                    'pinyin': pinyin}
            characters.append(i);
    return characters;

def get_words(working_directory, characters):
    words = [];
    with open(os.path.join(working_directory, WORDS_FILE)) as f:
        while 1:
            line = f.readline();
            if line == '':
                break;
            word = json.loads(line);

            chars = [];
            for i in range(word['character_begin_index'], \
                            word['character_end_index']+1):
                chars.append(characters[i]['character']);

            w = {'characters': ''.join(chars), \
                    'definition': word['definition']}
            words.append(w);
    return words;

def log_error(working_directory, message):
    error_lock.acquire();
    try:
        with open(LOG_FILE, 'a', encoding='utf8') as f:
            f.write(str(datetime.datetime.now()));
            f.write(os.linesep);
            f.write(working_directory);
            f.write(os.linesep);
            f.write(message);
            f.write(os.linesep + os.linesep);
    finally:
        error_lock.release();

def usage():
    print('usage: ' + PROGRAM_NAME + '\n' + \
            '   --makemeahanzi=<' + MAKEMEAHANZI_NAME + ' path>\n' + \
            '   --cedict=<' + CEDICT_NAME + ' path>');

def main(argv):
    global MAKEMEAHANZI_PATH, CEDICT_PATH;
    opts, args = getopt.getopt(argv, '', ['makemeahanzi=', 'cedict=']);
    for opt, arg in opts:
        if opt == '--makemeahanzi':
            MAKEMEAHANZI_PATH = arg;
        elif opt == '--cedict':
            CEDICT_PATH = arg;
    if MAKEMEAHANZI_PATH == '' or CEDICT_PATH == '':
        usage();
        exit(1);

    app = Flask(__name__);
    cors = CORS(app);
    app.config['CORS_HEADERS'] = 'Content-Type';
    api = Api(app);
    api.add_resource(GenerateInfos, '/generate_infos', methods=['POST']);
    api.add_resource(GenerateSheet, '/generate_sheet', methods=['POST']);
    api.add_resource(RetrieveSheet, '/retrieve_sheet');
    api.add_resource(RetrieveCount, '/retrieve_count');
    app.run(port='5002', threaded=True);
if __name__ == '__main__':
    main(sys.argv[1:]);
