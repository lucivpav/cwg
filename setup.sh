#!/usr/bin/env bash

rm -rf cedict makemeahanzi frontend/tagmanager

git clone https://github.com/skishore/makemeahanzi.git makemeahanzi
mkdir cedict
curl https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz | gunzip > cedict/data
mkdir frontend/tagmanager
curl https://raw.githubusercontent.com/max-favilli/tagmanager/v3.0.2/tagmanager.js > frontend/tagmanager/tagmanager.js
curl https://raw.githubusercontent.com/max-favilli/tagmanager/v3.0.2/tagmanager.css > frontend/tagmanager/tagmanager.css