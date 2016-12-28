#!/bin/bash

YaraPath="./yaraall"

echo "Update Yara Rules"
if [ -d rules ]; then
    pushd .
    cd rules
    git pull
    popd 
else
    git clone https://github.com/Yara-Rules/rules.git
fi

echo "Update Yara Rat"
if [ -d RATDecoders ]; then
    pushd .
    cd RATDecoders
    git pull
    popd 
else
    git clone https://github.com/kevthehermit/RATDecoders.git
fi

rm -rf $YaraPath
mkdir -p $YaraPath
cp rules/malware/*.yar $YaraPath
cp rules/malware/Operation_Blockbuster/*.yara $YaraPath
cp RATDecoders/yaraRules/*.yar $YaraPath

pushd .
cd $YaraPath
for file in *.yara ;do
    mv "$file" "${file%.yara}.yar"
done
