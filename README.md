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

## Words

* Use parentheses to group multiple characters together. This will add definition of such words into the sheet.

## Setup

Install dependencies:

```sh
pipenv install
```

> [!NOTE] NOTE:
> You may need to use `pipx` to accomplish this.
> e.g. `sudo apt install pipx` & `pipx install pipenv`,
> then open a new terminal/refresh current one and then run above command.

Then run the setup script to download the datasets and fonts:

```sh
sh setup.sh
```

See also: [Windows 10 64-bit notes](https://github.com/lucivpav/cwg/wiki/Windows-10-64-bit-installation-notes)

## Command line worksheet generation

The `pinenv install` command should have created a virtual environment.
You can verify this by running `pipenv --venv` from the repository's root directory.

Activate the virtual environment by running:

```sh
source .venv/bin/activate
```

> [!NOTE] NOTE:
> You probably need to set the environment variables again.
> You can test this with a simple `echo $MAKEMEAHANZI`
> Or just set them again with similar commands from the setup.sh script:
> `export MAKEMEAHANZI=$(pwd)/makemeahanzi && export CEDICT=$(pwd)/cedict`

### Generate worksheet

To generate a worksheet from a list of characters in the command line, run the following command:

```sh
python backend/src/cli.py --characters='你好' --title='Vocabulary' --guide='star' --stroke-order-color='red'
```

### Customize pinyin, translation and words

You may customize the pinyin, translations, and words on the worksheets
by generating and then editing the .json files,
and then generating the PDF from them.

Generate the `character_infos.json` and `word_infos.json` files by running:

```sh
python backend/src/cli.py --characters='(你好)' --info # Generate character_infos.json
```

You may then edit the 'character_infos.json' and 'word_infos.json'
and generate the PDF by running:

```sh
python backend/src/cli.py --title='Vocabulary' --guide='star' --sheet # Generate worksheet
```

## Running tests

```sh
cd backend
pipenv run pytest test
```

## License

This project is released under the GPLv3 license, for more details, take a look at the LICENSE.txt file in the source code.
