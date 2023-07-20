import os
import sys
import shutil
import tarfile
import traceback
from datetime import date, timedelta

from conf.settings import UNKOWN_DATASETS_PATH, FEATURES_PATH, FEATURE_POSITIONS_PATH, REPORTS_PATH
from training import predict_package_RF


def add_mode(dir: str):
    """
    检查文件夹是否具有读写执行权限，没有则添加
    检查文件是否具有读权限，没有则添加
    """
    for dirpath, dirnames, filenames in os.walk(dir):
        for dirname in dirnames:
            dir_path = os.path.join(dirpath, dirname)
            if not os.access(dir_path, os.R_OK | os.W_OK | os.X_OK):
                os.chmod(dir_path, 0o777)
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not os.access(file_path, os.R_OK | os.W_OK):
                os.chmod(file_path, 0o666)
                
def extract_cli(dataset_name: str):
    """提取特征"""
    dataset_path = os.path.join(UNKOWN_DATASETS_PATH, dataset_name)
    feature_path = os.path.join(FEATURES_PATH, dataset_name)
    feature_postion_path = os.path.join(FEATURE_POSITIONS_PATH, dataset_name)

    if os.path.exists(feature_path):
        try:
            shutil.rmtree(feature_path)
        except PermissionError:
            traceback.print_exc()
            add_mode(temp_dataset_path)
            shutil.rmtree(temp_dataset_path)
    os.makedirs(feature_path)

    temp_dataset_path = os.path.abspath(f'.decompressed-packages-dataset')
    if os.path.exists(temp_dataset_path):
        try:
            shutil.rmtree(temp_dataset_path)
        except PermissionError:
            traceback.print_exc()
            add_mode(temp_dataset_path)
            shutil.rmtree(temp_dataset_path)
    os.makedirs(temp_dataset_path)
    for file_name in os.listdir(dataset_path):
        file_path = os.path.join(dataset_path, file_name)
        try:
            # decompress .tgz file
            if file_name.endswith('.tgz'):
                tar = tarfile.open(file_path)
                temp_package_path = f'{temp_dataset_path}/{file_name[:-4]}'
                os.makedirs(temp_package_path)
                tar.extractall(path=temp_package_path)
                tar.close()
        except Exception:
            print(f'Error: {file_name}', file=sys.stderr)
            traceback.print_exc()
    add_mode(temp_dataset_path)
    try:
        cwd = os.getcwd()
        os.chdir('feature-extract')
        os.system(f'npm run start {temp_dataset_path} {feature_path} {feature_postion_path}')
        os.chdir(cwd)
    except Exception:
        print(f'Error: {dataset_name}')
        traceback.print_exc()
    # shutil.rmtree(temp_dataset_path)

def predict_cli(dataset_name: str):
    """预测包"""
    csv_dir_path = os.path.join(FEATURES_PATH, dataset_name)
    report_name = f'{dataset_name}-report.csv'
    report_content = 'package name, predict\n'
    for feature_file_name in os.listdir(csv_dir_path):
        feature_file_path = os.path.join(csv_dir_path, feature_file_name)
        result = predict_package_RF(feature_file_path)
        report_content += feature_file_name[:-4] + ', ' + result + '\n'
    with open(os.path.join(REPORTS_PATH, report_name), 'w') as f:
        f.write(report_content)

if __name__ == '__main__':
    today = date.today()
    yesterday = today - timedelta(days=1)
    malcious_dataset_name = f'{yesterday.year}-{yesterday.month}-{yesterday.day}'
    print('Extract features started.')
    extract_cli(malcious_dataset_name)
    print('Extract features finished.')
    print('Predict packages started.')
    predict_cli(malcious_dataset_name)
    print('Predict packages finished.')
