#!/bin/bash

cd feature-extract
npm install
cd ..

if [ ! -d "env" ]; then
    python3 -m venv env
    source env/bin/activate
    pip install -r training/requirements.txt
    deactivate
fi

folders=("datasets/preprocessed-datasets/benign" "datasets/preprocessed-datasets/malicious" "datasets/preprocessed-datasets/unknown" "models" "features" "feature-positions" "reports")
for folder in "${folders[@]}"
do
    if [ ! -d "$folder" ]; then
        mkdir -p "$folder"
    fi
done