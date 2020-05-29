# Chinese Worksheet Generator
Allows one to generate Chinese practice worksheets.

[![Build Status](https://travis-ci.org/lucivpav/cwg.svg?branch=master)](https://travis-ci.org/lucivpav/cwg)

![](http://i.imgur.com/HH9eKtC.png)

## Features
* Simplified and traditional Chinese
* Stroke order
* Radicals
* Words
* Customizable pinyin and translation
* Customizable title and grid style

## Dependencies
* [Make Me a Hanzi dataset](https://github.com/skishore/makemeahanzi)
* [CEDICT dataset](https://www.mdbg.net/chinese/dictionary?page=cedict)
* cairosvg
* reportlab
* flask
* [SourceHanSansTC-Normal.ttf](https://github.com/be5invis/source-han-sans-ttf/releases)
* [TagManager](https://maxfavilli.com/jquery-tag-manager)

## Installation notes
* Place TagManager folder into *frontend* folder
* [Windows 10 64-bit notes](https://github.com/lucivpav/cwg/wiki/Windows-10-64-bit-installation-notes)

## Words
* Use parentheses to group multiple characters together. This will add definition of such words into the sheet.

## Command line worksheet generation
### Show usage
```
gen.py
```
### Generate worksheet
```
gen.py --makemeahanzi=$MAKEMEAHANZI_PATH --cedict=$CEDICT_PATH --characters='你好' --title='Vocabulary' --guide='star' --stroke-order-color='red'
```
### Customize pinyin, translation and words
```
gen.py --makemeahanzi=$MAKEMEAHANZI_PATH --cedict=$CEDICT_PATH --characters='(你好)' --info # Generate character_infos.json

# You may edit the 'character_infos.json' and 'word_infos.json' to customize pinyin, translation and words

gen.py --makemeahanzi=$MAKEMEAHANZI_PATH --title='Vocabulary' --guide='star' --sheet # Generate worksheet
```

## Running tests
```
pipenv install
cd backend
pipenv run pytest test
```

## License
This project is released under the GPLv3 license, for more details, take a look at the LICENSE.txt file in the source code.
