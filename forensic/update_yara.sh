#!/bin/bash

YaraPath="./yaraall"

echo "Update Yara Rules"
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

echo "Update Thanatos Yara"
if [ -d Yaramoi ]; then
    pushd .
    cd Yaramoi
    git pull
    popd
else
  git clone https://github.com/Th4nat0s/Yaramoi.git
fi

rm -rf $YaraPath
mkdir -p $YaraPath
cp rules/malware/*.yar $YaraPath
cp rules/malware/Operation_Blockbuster/*.yara $YaraPath
cp RATDecoders/yaraRules/*.yar $YaraPath
cp Yaramoi/*.yar $YaraPath

pushd .
cd $YaraPath
for file in *.yara ;do
    mv "$file" "${file%.yara}.yar"
done
popd

# Remove nasty include
rm $YaraPath/yaraRules.yar

# Create Metafile
pushd .
for file in `ls -1 $YaraPath` ;do
  echo include \"$file\"
  echo include \"$file\" >> $YaraPath/_YaraAll.yar
done
popd
