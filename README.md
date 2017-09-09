# Chinese Worksheet Generator
Allows one to generate Chinese practice worksheets.

![](https://i.imgur.com/7UDpAIj.png)

## Features
* Simplified and traditional Chinese
* Stroke order
* Radicals
* Customize suggested pinyin and translation
* Customize title and grid style

## Dependencies
* makemeahanzi dataset
* cairosvg
* reportlab
* flask

## Command line worksheet generation
### Show usage
```
gen.py
```
### Generate worksheet
```
gen.py --dataset=$DATASET_PATH --characters='你好' --title='Vocabulary' --guide='star'
```
### Customize suggested pinyin and translation
```
gen.py --dataset=$DATASET_PATH --characters='你好' --info # Generate character_infos.json

# You may edit the 'character_infos.json' to customize pinyin and translation

gen.py --dataset=$DATASET_PATH --title='Vocabulary' --guide='star' # Generate worksheet
```
