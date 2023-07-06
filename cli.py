import os
import shutil
import argparse
import traceback

from conf.settings import (
    FEATURES_PATH,
    FEATURE_POSITIONS_PATH,
    REPORTS_PATH,
    MALICIOUS_DATASETS_PATH,
    BENIGN_DATASETS_PATH,
    UNKOWN_DATASETS_PATH,
    DATASET_NAMES,
    MALICIOUS_DATASET_NAMES,
    BENIGN_DATASET_NAMES,
    UNKOWN_DATASET_NAMES,
    FEATURE_NAMES,
    MODEL_NAMES,
    PREPROCESS_METHOD_NAMES,
    MODEL_HYPER_PARAMETERS
)
from training import (
    PreprocessMethodEnum,
    ModelEnum,
    ActionEnum,
    train,
    predict_package_MLP,
    predict_package_NB,
    predict_package_SVM,
    predict_package_RF
)


def extract_cli():
    """提取特征"""
    dataset_name = args.dataset
    if dataset_name in MALICIOUS_DATASET_NAMES:
        dataset_path = os.path.join(MALICIOUS_DATASETS_PATH, dataset_name)
    elif dataset_name in BENIGN_DATASET_NAMES:
        dataset_path = os.path.join(BENIGN_DATASETS_PATH, dataset_name)
    elif dataset_name in UNKOWN_DATASET_NAMES:
        dataset_path = os.path.join(UNKOWN_DATASETS_PATH, dataset_name)
    else:
        print('Dataset name error!')
        exit(1)
    feature_path = os.path.join(FEATURES_PATH, dataset_name)
    feature_position_path = os.path.join(FEATURE_POSITIONS_PATH, dataset_name)

    if os.path.exists(feature_path):
        shutil.rmtree(feature_path)
    os.makedirs(feature_path)

    try:
        cwd = os.getcwd()
        os.chdir('feature-extract')
        os.system(f'npm run start {dataset_path} {feature_path} {feature_position_path}')
        os.chdir(cwd)
    except Exception:
        print(f'Error: {dataset_name}')
        traceback.print_exc()

def train_cli():
    """训练模型"""
    malicious_dataset_name = args.malicious
    benign_dataset_name = args.benign
    model_name = args.model
    preprocess_method = args.preprocess
    action_name = args.action
    malicous_csv_dir_path = os.path.join(FEATURES_PATH, malicious_dataset_name)
    normal_csv_dir_path = os.path.join(FEATURES_PATH, benign_dataset_name)
    hyper_parameters = {}

    if preprocess_method == 'none':
        preprocess = PreprocessMethodEnum.NONE
    elif preprocess_method == 'standardlize':
        preprocess = PreprocessMethodEnum.STANDARDLIZE
    elif preprocess_method == 'min-max-scale':
        preprocess = PreprocessMethodEnum.MIN_MAX_SCALE

    if action_name == 'training':
        action = ActionEnum.TRAINING
    elif action_name == 'save':
        action = ActionEnum.SAVE
    elif action_name == 'test':
        action = ActionEnum.TEST

    if model_name == 'MLP':
        model = ModelEnum.MLP
    elif model_name == 'NB':
        model = ModelEnum.NB
    elif model_name == 'SVM':
        model = ModelEnum.SVM
    elif model_name == 'RF':
        model = ModelEnum.RF
        hyper_parameters['n_estimators'] = args.hyper_estimators
        hyper_parameters['max_depth'] = args.hyper_depth

    train(malicous_csv_dir_path, normal_csv_dir_path, preprocess, model, action, hyper_parameters)

def test_cli():
    """测试模型
    使用恶意包数据集和良性包数据集对模型进行测试，并对模型进行评估（准确率、召回率、F1值）
    """
    malicious_dataset_name = args.malicious
    benign_dataset_name = args.benign
    model_name = args.model
    malicous_csv_dir_path = os.path.join(FEATURES_PATH, malicious_dataset_name)
    normal_csv_dir_path = os.path.join(FEATURES_PATH, benign_dataset_name)

    report_name = f'{malicious_dataset_name}-{benign_dataset_name}-{model_name}-report-1.csv'
    report_content = 'package name, package path, actual, predict\n'
    report_data = []
    for feature_file_name in os.listdir(malicous_csv_dir_path):
        feature_file_path = os.path.join(malicous_csv_dir_path, feature_file_name)
        if model_name == 'MLP':
            result = predict_package_MLP(feature_file_path)
        elif model_name == 'NB':
            result = predict_package_NB(feature_file_path)
        elif model_name == 'SVM':
            result = predict_package_SVM(feature_file_path)
        elif model_name == 'RF':
            result = predict_package_RF(feature_file_path)
        report_content += feature_file_name + ', ' + feature_file_path + ', ' + 'malicious' + ', ' + result + '\n'
        report_data.append((feature_file_name, feature_file_path, 'malicious', result))
    
    for feature_file_name in os.listdir(normal_csv_dir_path):
        feature_file_path = os.path.join(normal_csv_dir_path, feature_file_name)
        if model_name == 'MLP':
            result = predict_package_MLP(feature_file_path)
        elif model_name == 'NB':
            result = predict_package_NB(feature_file_path)
        elif model_name == 'SVM':
            result = predict_package_SVM(feature_file_path)
        elif model_name == 'RF':
            result = predict_package_RF(feature_file_path)
        report_content += feature_file_name + ', ' + feature_file_path + ', ' + 'benign' + ', ' + result + '\n'
        report_data.append((feature_file_name, feature_file_path, 'benign', result))

    with open(os.path.join(REPORTS_PATH, report_name), 'w') as f:
        f.write(report_content)
    
    # calculate evaluation metrics
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    for data in report_data:
        if data[2] == 'malicious' and data[3] == 'malicious':
            TP += 1
        elif data[2] == 'malicious' and data[3] == 'benign':
            FN += 1
        elif data[2] == 'benign' and data[3] == 'malicious':
            FP += 1
        elif data[2] == 'benign' and data[3] == 'benign':
            TN += 1
    accuracy = (TP + TN) / (TP + TN + FP + FN)
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1_score = 2 * precision * recall / (precision + recall)

    report_name = f'{malicious_dataset_name}-{benign_dataset_name}-{model_name}-report-2.csv'
    report_content = 'TP, FP, TN, FN, accuracy, precision, recall, f1_score\n'
    report_content += f'{TP}, {FP}, {TN}, {FN}, {accuracy}, {precision}, {recall}, {f1_score}\n'

    with open(os.path.join(REPORTS_PATH, report_name), 'w') as f:
        f.write(report_content)

def predict_cli():
    """预测包
    对指定的数据集进行预测（恶意包或良性包）
    """
    dataset_name = args.dataset
    model_name = args.model

    report_name = f'{dataset_name}-{model_name}-report.csv'
    report_content = 'package name, predict\n'
    csv_dir_path = os.path.join(FEATURES_PATH, dataset_name)
    for feature_file_name in os.listdir(csv_dir_path):
        feature_file_path = os.path.join(csv_dir_path, feature_file_name)
        if model_name == 'MLP':
            result = predict_package_MLP(feature_file_path)
        elif model_name == 'NB':
            result = predict_package_NB(feature_file_path)
        elif model_name == 'SVM':
            result = predict_package_SVM(feature_file_path)
        elif model_name == 'RF':
            result = predict_package_RF(feature_file_path)
        report_content += feature_file_name[:-4] + ', ' + result + '\n'

    with open(os.path.join(REPORTS_PATH, report_name), 'w') as f:
        f.write(report_content)

if __name__ == '__main__':
    hyper_parameters = {}
    parser = argparse.ArgumentParser(description='Extract, train, test or predict PyPI package.')
    subparsers = parser.add_subparsers(help='sub-command help', dest='subparser_name')

    # extract CLI parameters
    parser_extract = subparsers.add_parser('extract', help='extract features', description='Extract features from given dataset.')
    parser_extract.add_argument('-d', '--dataset', type=str, required=True, help='dataset name', choices=DATASET_NAMES)

    # train CLI parameters
    parser_train = subparsers.add_parser('train', help='train model', description='Train model with given dataset.')
    parser_train.add_argument('-m', '--malicious', type=str, required=True, help='malicious dataset name', choices=MALICIOUS_DATASET_NAMES)
    parser_train.add_argument('-b', '--benign', type=str, required=True, help='benign dataset name', choices=BENIGN_DATASET_NAMES)
    parser_train.add_argument('-o', '--model', type=str, required=True, help='model name', choices=MODEL_NAMES)
    parser_train.add_argument('-p', '--preprocess', type=str, required=True, help='preprocess method', choices=PREPROCESS_METHOD_NAMES)
    parser_train.add_argument('-a', '--action', type=str, required=True, help='action', choices=['training', 'save', 'test'])
    parser_train.add_argument('-he', '--hyper-estimators', type=int, help='number of estimators of model to save', choices=MODEL_HYPER_PARAMETERS['RF']['N_ESTIMATORS'])
    parser_train.add_argument('-hd', '--hyper-depth', type=int, help='max depth of model to save', choices=MODEL_HYPER_PARAMETERS['RF']['MAX_DEPTH'])

    # test CLI parameters
    parser_test = subparsers.add_parser('test', help='test model', description='Test model with given dataset.')
    parser_test.add_argument('-m', '--malicious', type=str, required=True, help='malicious dataset name', choices=MALICIOUS_DATASET_NAMES)
    parser_test.add_argument('-b', '--benign', type=str, required=True, help='benign dataset name', choices=BENIGN_DATASET_NAMES)
    parser_test.add_argument('-o', '--model', type=str, required=True, help='model name', choices=MODEL_NAMES)

    # predict CLI parameters
    parser_predict = subparsers.add_parser('predict', help='predict package', description='Predict package with given model.')
    parser_predict.add_argument('-d', '--dataset', type=str, help='dataset name', choices=FEATURE_NAMES)
    parser_predict.add_argument('-o', '--model', type=str, required=True, help='model name', choices=MODEL_NAMES)

    args = parser.parse_args()
    subparser_name = args.subparser_name
    if subparser_name == 'extract':
        extract_cli()
    elif subparser_name == 'train':
        train_cli()
    elif subparser_name == 'test':
        test_cli()
    elif subparser_name == 'predict':
        predict_cli()