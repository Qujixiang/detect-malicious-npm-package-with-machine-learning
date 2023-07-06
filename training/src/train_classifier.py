from enum import Enum

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from .read_feature import read_features
from .train_MLP import train_MLP_validation, test_MLP
from .train_NB import test_NB, train_NB_Validate
from .train_RF import test_RF, train_classifier_RF_Validation
from .train_SVM import test_SVM, train_SVM_validate
from .test import test
from .pickle_util import save_scaler
from .commons import rf_scaler_save_path, mlp_scaler_save_path, nb_scaler_save_path, svm_scaler_save_path


class PreprocessMethodEnum(Enum):
    """数据预处理方法枚举"""
    NONE = 1
    STANDARDLIZE = 2
    MIN_MAX_SCALE = 3

class ModelEnum(Enum):
    """模型枚举"""
    RF = 1
    MLP = 2
    NB = 3
    SVM = 4

class ActionEnum(Enum):
    """动作枚举"""
    TRAINING = 1
    SAVE = 2
    TEST = 3

def preprocess(X_train, X_test, scaler_save_path: str, preprocess_method: PreprocessMethodEnum) -> list:
    """
    数据预处理
    :param X_train: 训练集
    :param X_test: 测试集
    :param scaler_save_path: scaler保存路径
    :param preprocess_method: 数据预处理方法
    :return: 预处理后的训练集和测试集
    """
    if preprocess_method == PreprocessMethodEnum.NONE:
        return [X_train, X_test]
    if preprocess_method == PreprocessMethodEnum.STANDARDLIZE:
        scaler = StandardScaler()

        # Fit the scaler to the training data
        scaler.fit(X_train)

        # Transform the training and test data using the fitted scaler
        X_train_scaled = scaler.transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        save_scaler(scaler, scaler_save_path)
        return [X_train_scaled, X_test_scaled]
    if preprocess_method == PreprocessMethodEnum.MIN_MAX_SCALE:
        scaler = MinMaxScaler()
        scaler.fit(X_train)
        X_train_scaled = scaler.transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        save_scaler(scaler, scaler_save_path)
        
        return [X_train_scaled, X_test_scaled]

def train(malcious_features_dir_path: str, normal_features_dir_path: str, preprocess_method: PreprocessMethodEnum, model: ModelEnum, action: ActionEnum, hyper_parameters={}):
    """
    训练分类器
    :param malcious_features_dir_path: 包含多个恶意样本特征文件的文件夹路径
    :param normal_features_dir_path: 包含多个正常样本特征文件的文件夹路径
    :param preprocess_method: 数据预处理方法
    :param model: 使用的模型
    :param action: 动作
    """
    [X, y, _] = read_features(malcious_features_dir_path, normal_features_dir_path)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)

    # preprocess
    if model == ModelEnum.RF:
        scaler_save_path = rf_scaler_save_path
    elif model == ModelEnum.MLP:
        scaler_save_path = mlp_scaler_save_path
    elif model == ModelEnum.NB:
        scaler_save_path = nb_scaler_save_path
    elif model == ModelEnum.SVM:
        scaler_save_path = svm_scaler_save_path
    [X_train, X_test] = preprocess(X_train, X_test, scaler_save_path, preprocess_method)

    # training and validation
    if action == ActionEnum.TRAINING:
        if model == ModelEnum.RF:
            train_classifier_RF_Validation(X_train, y_train)
        elif model == ModelEnum.MLP:
            train_MLP_validation(X_train, y_train)
        elif model == ModelEnum.NB:
            train_NB_Validate(X_train, y_train)
        elif model == ModelEnum.SVM:
            train_SVM_validate(X_train, y_train)

    # save model
    elif action == ActionEnum.SAVE:
        if model == ModelEnum.RF:
            if hyper_parameters.get('n_estimators') is None or hyper_parameters.get('max_depth') is None:
                raise Exception('estimators and max_depth cannot be None')
            test_RF(X_train, y_train, X_test, y_test, n_estimators=hyper_parameters.get('n_estimators'), max_depth=hyper_parameters.get('max_depth'))
        elif model == ModelEnum.MLP:
            test_MLP(X_train, y_train, X_test, y_test)
        elif model == ModelEnum.NB:
            test_NB(X_train, y_train, X_test, y_test)
        elif model == ModelEnum.SVM:
            test_SVM(X_train, y_train, X_test, y_test)
    elif action == ActionEnum.TEST:
        test(X_test, y_test)