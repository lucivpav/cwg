#!/usr/bin/env sh

echo "Cleaning up previous setup..."
rm -rf makemeahanzi cedict frontend/tagmanager SourceHanSansTC-Normal.ttf

echo "makemeahanzi..."
curl https://github.com/skishore/makemeahanzi/archive/refs/heads/master.zip -L -o makemeahanzi.zip -sS
unzip makemeahanzi.zip -q
mv makemeahanzi-master makemeahanzi
rm makemeahanzi.zip

echo "cedict..."
mkdir cedict
curl https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz -sS | gunzip > cedict/data

echo "tagmanager..."
mkdir frontend/tagmanager
curl https://raw.githubusercontent.com/max-favilli/tagmanager/v3.0.2/tagmanager.js -o frontend/tagmanager/tagmanager.js -sS
curl https://raw.githubusercontent.com/max-favilli/tagmanager/v3.0.2/tagmanager.css -o frontend/tagmanager/tagmanager.css -sS

echo "SourceHanSansTtf..."
curl https://github.com/be5invis/source-han-sans-ttf/releases/download/v2.001.1/source-han-sans-ttf-2.001.1.7z -L -o SourceHanSansTtf.7z -sS
7z e SourceHanSansTtf.7z SourceHanSansTC-Normal.ttf -bso0 -bsp0
rm SourceHanSansTtf.7z

echo "Done"