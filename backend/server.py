#!/usr/bin/python3
from flask import Flask, request, send_file
from flask_restful import Resource, Api
from flask_jsonpify import jsonpify
from flask_cors import CORS, cross_origin
import json
import os
import tempfile
import shutil
from threading import Lock
from gen import generate_infos, generate_sheet, GenException, \
                INFOS_FILE, SHEET_FILE, get_guide

DATASET_NAME = 'makemeahanzi';
LOG_FILE = 'errors.log';
COUNT_FILE = 'count.txt'
INTERNAL_ERROR_MSG = 'Failed to generate sheet. Please enter different configuration or try again later.';

count_lock = Lock();

class GenerateInfos(Resource):
    def get(self):
        characters = request.args.get('characters');
        if characters == None or len(characters) == 0:
            return jsonpify({'error': 'No characters provided'});
        with tempfile.TemporaryDirectory() as path:
            dataset_path = get_dataset_path();
            try:
                generate_infos(dataset_path, path, characters);
            except GenException as e:
                log_error('generate_infos ' + characters);
                return jsonpify({'error': str(e)});
            except:
                log_error('generate_infos ' + characters);
                return jsonpify({'error': INTERNAL_ERROR_MSG});

            with open(os.path.join(path, INFOS_FILE)) as f:
                infos = [];
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
                    infos.append(i);

                new_dir = tempfile.mkdtemp();
                shutil.copy(os.path.join(path, INFOS_FILE), new_dir);
                result = { "id": new_dir, "infos": infos };
                return jsonpify(result);

class GenerateSheet(Resource):
    def get(self):
        temp_path = request.args.get('id');
        guide = request.args.get('guide');
        title = request.args.get('title');
        if temp_path == None or len(temp_path) == 0 or \
            guide == None or len(guide) == 0 or \
            title == None:
            return jsonpify({'error': 'Invalid parameters'});
        try:
            guide = get_guide(guide);
        except GenException as e:
            return jsonpify({'error': str(e)});

        pinyins = [];
        definitions = [];
        i = 0;
        while ('pinyin' + str(i)) in request.args:
            pinyins.append(request.args.get('pinyin' + str(i)));
            definitions.append(request.args.get('definition' + str(i)));
            i += 1;

        file_path = os.path.join(temp_path, INFOS_FILE);
        update_infos_file(file_path, pinyins, definitions);
        dataset_path = get_dataset_path();
        error_msg = 'generate_sheet ' + title + ' ' + str(guide);
        try:
            generate_sheet(dataset_path, temp_path, title, guide);
        except GenException as e:
            log_error(error_msg);
            shutil.rmtree(temp_path);
            return jsonpify({'error': str(e)});
        except:
            log_error(error_msg);
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
                        mimetype='application/pdf');
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

def get_dataset_path():
    dataset_path = os.path.dirname(SCRIPT_PATH); # go up
    dataset_path = os.path.join(dataset_path, DATASET_NAME);
    return dataset_path;

def update_infos_file(file_path, pinyins, definitions):
    new_file_name = 'new.json';
    new_file_path = os.path.join(os.path.dirname(file_path), new_file_name);
    with open(file_path, 'r') as f_orig:
        with open(new_file_path, 'w') as f_new:
            i = 0;
            while 1:
                line = f_orig.readline();
                if line == '':
                    break;
                info = json.loads(line);
                info['pinyin'] = [pinyins[i]];
                info['definition'] = definitions[i];
                f_new.write(json.dumps(info) + '\n');
                i += 1;
    shutil.copy(new_file_path, file_path);

def log_error(parameters):
    with open(LOG_FILE, 'w') as f:
        f.write(parameters + os.linesep);

if __name__ == '__main__':
    SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__));
    app = Flask(__name__);
    cors = CORS(app);
    app.config['CORS_HEADERS'] = 'Content-Type';
    api = Api(app);
    api.add_resource(GenerateInfos, '/generate_infos');
    api.add_resource(GenerateSheet, '/generate_sheet');
    api.add_resource(RetrieveSheet, '/retrieve_sheet');
    api.add_resource(RetrieveCount, '/retrieve_count');
    app.run(port='5002', threaded=True);
