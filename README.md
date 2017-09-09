# Chinese Worksheet Generator
Allows one to generate Chinese practice worksheets.

![](http://i.imgur.com/idXo0Pj.png)

## Features
* Simplified and traditional Chinese
* Stroke order
* Radicals
* Customizable pinyin and translation
* Customizable title and grid style

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
### Customize pinyin and translation
```
gen.py --dataset=$DATASET_PATH --characters='你好' --info # Generate character_infos.json

# You may edit the 'character_infos.json' to customize pinyin and translation

gen.py --dataset=$DATASET_PATH --title='Vocabulary' --guide='star' --sheet # Generate worksheet
```

## License
This project is released under the GPLv3 license, for more details, take a look at the LICENSE.txt file in the source code.
