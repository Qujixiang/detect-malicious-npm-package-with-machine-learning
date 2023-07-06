# detect-malicious-npm-package-with-machine-learning
> Predicting npm packages with the model training by machine learning method.

## environment

- ubuntu 22.04
- node.js 18.16.0
- python 3.10.6

## install

1. Clone the repository.
2. Install the project.

```bash
./install.sh
```

## usage

For convenience, please use `cli.py` to extract features and predict.


```bash
# Get the help.
python3 cli.py -h

# Get the help of extracting features.
python3 cli.py extract -h

# Extract features from malicious dataset "npm-malicious-20230512".
python3 cli.py extract -d npm-malicious-20230512

# Get the help of predicting.
python3 cli.py predict -h

# Predict the malicious dataset "npm-malicious-20230512".
python3 cli.py predict -d npm-malicious-20230512 -o RF
```

**Note**:

`npm-malicious-20230512` is a malicious dataset used in our experiments. There is no this dataset here. You should put your dataset here in the specified format which used by `conf/settings.py`.

Briefly, you should put malicious datasets in `datasets/preprocessed-datasets/malicious` directory. And other datasets you want to predict in `datasets/preprocessed-datasets/unknown` directory.

If you want to specify other directory as malicious datasets directory, you should change variable `MALICIOUS_DATASETS_PATH` in `conf/settings.py` to your malicious datasets directory. The same is true for benign and unknown datasets.

## architecture
```bash
├── README.md
├── cli.py
├── conf
│   └── settings.py: settings about datasets and models, etc
├── datasets
│   └── preprocessed-datasets
│       ├── benign: default benign npm package datasets
│       ├── malicious: default malicious npm package datasets, you should put your malicious dataset here
│       │   └── npm-malicious-20230512: a malicious npm package dataset
│       └── unknown: default unknown npm package datasets, you should put your unknown dataset here
├── feature-extract: extract features from package
│   ├── README.md
│   ├── jest.config.ts
│   ├── log
│   ├── material
│   ├── node_modules
│   ├── dist
│   ├── package-lock.json
│   ├── package.json
│   ├── src
│   └── tsconfig.json
├── features: extracted features
│   ├── npm-malicious-20230512
├── models
│   ├── MLP.pkl
│   ├── MLP_scaler.pkl
│   ├── NB.pkl
│   ├── NB_scaler.pkl
│   ├── RF.pkl
│   ├── RF_scaler.pkl
│   ├── SVM.pkl
│   └── SVM_scaler.pkl
├── reports
│   ├── npm-malicious-20230512-RF-report.csv
└── training
    ├── __init__.py
    ├── requirements.txt
    ├── results
    └── src
```

## documentation

### feature-extract directory

This program can analyze if a package is a malicious package or not. The  directory of feature value file is output_feature.  

This program is used to extract feature values from npm package originally. It scans all the file in the package and use [babel](https://github.com/babel/babel) and regular expression to give a static analysis of package source code.

### training directory

This project is used to traing classifier model and evaluate the performance of the model. At this time, MLP,RF, NB, Kernel SVM are used as classifier.  

The train set is material/training_set. Malicious-dedupli subdirecotry contains malicous package feature vectors. Normal subdirectory contains benign package feature vectors.  


The test set is material/test_set. Malicious-dedupli subdirectory contains malicous package feature vector. Normal subdirectory contains benign package feature vectors.

**Note**:

- You can download benign npm package in [npm registry](https://www.npmjs.com/).
- The malicious package in train set is from [ohm](https://dasfreak.github.io/Backstabbers-Knife-Collection/).  
- The malicious package in test set is from [Duan](https://github.com/osssanitizer/maloss).