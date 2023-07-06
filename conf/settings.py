import os


# project root path
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# default datasets path
DATASETS_PATH =  os.path.join(ROOT_PATH, 'datasets', 'preprocessed-datasets')
MALICIOUS_DATASETS_PATH = os.path.join(DATASETS_PATH, 'malicious')
BENIGN_DATASETS_PATH = os.path.join(DATASETS_PATH, 'benign')
UNKOWN_DATASETS_PATH = os.path.join(os.path.dirname(ROOT_PATH), 'collect-npm-packages/packages')

# models path
MODELS_PATH = os.path.join(ROOT_PATH, 'models')

# features path
FEATURES_PATH = os.path.join(ROOT_PATH, 'features')

# feature positions path
FEATURE_POSITIONS_PATH = os.path.join(ROOT_PATH, 'feature-positions')

# reports path
REPORTS_PATH = os.path.join(ROOT_PATH, 'reports')

# supported models
MODEL_NAMES = ['MLP', 'NB', 'SVM', 'RF']

# supported preprocess methods
PREPROCESS_METHOD_NAMES = ['none', 'standardlize', 'min-max-scale']

# supported datasets
MALICIOUS_DATASET_NAMES = os.listdir(MALICIOUS_DATASETS_PATH)
BENIGN_DATASET_NAMES = os.listdir(BENIGN_DATASETS_PATH)
UNKOWN_DATASET_NAMES = os.listdir(UNKOWN_DATASETS_PATH)
DATASET_NAMES = MALICIOUS_DATASET_NAMES + BENIGN_DATASET_NAMES + UNKOWN_DATASET_NAMES

# supported package features
FEATURE_NAMES = os.listdir(FEATURES_PATH)

# hyper parameters for training models
MODEL_HYPER_PARAMETERS = {
    'RF': {
        'N_ESTIMATORS': [16, 32, 64, 100, 128, 256, 512],
        'MAX_DEPTH': [3, 5, 7, 11, 15]
    }
}

# default hyper parameters for saving models
DEFAULT_MODEL_HYPER_PARAMETERS = {
    'RF': {
        'N_ESTIMATORS': 128,
        'MAX_DEPTH': 32
    }
}