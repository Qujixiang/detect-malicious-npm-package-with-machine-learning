import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from prettytable import PrettyTable

from .pickle_util import load_classifier, save_classifier
from .model_util import evaluate_model
from .commons import table_path, field_names, classifier_save_path, scoring
from conf.settings import MODEL_HYPER_PARAMETERS, DEFAULT_MODEL_HYPER_PARAMETERS


def train_classifier_RF_Validation(X, y):
   k = 4
   skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=10)
   table_validate_path = os.path.join(table_path, "RF_validation.csv")

   validate_table = PrettyTable()
   validate_table.field_names = field_names

   with open(table_validate_path, "w+") as validate_file:
      for estimator in MODEL_HYPER_PARAMETERS['RF']['N_ESTIMATORS']:
            for depth in MODEL_HYPER_PARAMETERS['RF']['MAX_DEPTH']:
               model = RandomForestClassifier(n_estimators=estimator, max_depth=depth)
               scores = cross_validate(model, X, y, cv=skf,scoring=scoring)
               validate_table.add_row([f'estimators = {estimator}; max_depth={depth}', scores["test_accu"].mean(), scores["test_prec"].mean(), scores["test_rec"].mean(), scores["test_f1"].mean(), scores["test_matt_cor"].mean()])
      validate_file.write(validate_table.get_csv_string())

def test_RF(X_train, y_train, X_test, y_test, n_estimators=DEFAULT_MODEL_HYPER_PARAMETERS['RF']['N_ESTIMATORS'], max_depth=DEFAULT_MODEL_HYPER_PARAMETERS['RF']['MAX_DEPTH']):
   model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
   model.fit(X_train, y_train)
   save_path = os.path.join(classifier_save_path, "RF.pkl")
   save_classifier(model, save_path)
   test_table_path = os.path.join(table_path, "RF_test.csv")
   table = PrettyTable()
   table.field_names = field_names
   y_pred = model.predict(X_test)
   [accuracy, precision, recall, f1, mcc] = evaluate_model(y_test, y_pred)
   table.add_row([f'estimators = {n_estimators}; max_depth={max_depth}', accuracy, precision, recall, f1, mcc])
   with open(test_table_path, "w+") as f:
      f.write(table.get_csv_string())

def test_RF_load(X_test, y_test):
   rf_classifier_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "classifier", "RF.pkl")
   model = load_classifier(rf_classifier_path)
   test_table_path = os.path.join(table_path, "RF_table_test.csv")
   table = PrettyTable()
   table.field_names = field_names
   y_pred = model.predict(X_test)
   [accuracy, precision, recall, f1, mcc] = evaluate_model(y_test, y_pred)
   table.add_row([f"estimators = {DEFAULT_MODEL_HYPER_PARAMETERS['RF']['N_ESTIMATORS']}; max_depth={DEFAULT_MODEL_HYPER_PARAMETERS['RF']['MAX_DEPTH']}", accuracy, precision, recall, f1, mcc])
   with open(test_table_path, "w+") as f:
      f.write(table.get_csv_string())