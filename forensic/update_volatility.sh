#!/bin/bash
echo "Update Volatility"
if [ -d volatility ]; then
    pushd .
    cd volatility
    git pull
    popd 
else
    git clone https://github.com/volatilityfoundation/volatility.git
fi

echo "Update Volatility Autoruns"
if [ -d volatility-autoruns ]; then
    pushd .
    cd volatility-autoruns
    git pull
    popd 
else
    git clone https://github.com/tomchop/volatility-autoruns.git
fi


echo "Update Volatility plugins"
if [ -d volatility_plugins ]; then
    pushd .
    cd volatility_plugins
    git pull
    popd 
else
    git clone https://github.com/arbor-jjones/volatility_plugins
fi

cp ./volatility_plugins/*.py ./volatility/volatility/plugins/
cp ./volatility-autoruns/autoruns.py ./volatility/volatility/plugins/

pushd .
cd volatility
sudo python setup.py install
popd 

