import pandas as pd
import numpy as np
from typing import Dict
from dataclasses import dataclass

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, TimeSeriesSplit, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import roc_auc_score
import lightgbm
from lightgbm import LGBMClassifier


@dataclass
class TrainTestData:
    X_train: pd.DataFrame
    X_valid: pd.DataFrame
    y_train: pd.Series
    y_valid: pd.Series


class LGBModel:
    
    def init(self, lgb_params: Dict, test_size: float=.33):
        self.test_size = test_size
        self.lgb_params = lgb_params
        
        self.model = None       
    
    def _split_train_test(self, X: pd.DataFrame, y: pd.Series) -> TrainTestData:
        X_train, X_valid, y_train, y_valid = \
                    train_test_split(X, y, test_size=self.test_size, random_state=42)
        
        return TrainTestData(X_train, X_valid, y_train, y_valid)
    
    def predict(self, X: pd.DataFrame) -> np.array:
        return self.model.predict_proba(X)[:, 1]
    
    def calc_auc(self, X: pd.DataFrame, y: pd.Series) -> float:
        predictions = self.predict(X)
        return roc_auc_score(y, predictions)
        
    
    def fit(self, X: pd.DataFrame, y: pd.Series):
        
        data = self._split_train_test(X, y)
        
        model = LGBMClassifier(n_estimators = 10000, **self.lgb_params)
        model.fit(data.X_train, data.y_train, 
                  eval_set=[(data.X_train, data.y_train), (data.X_valid, data.y_valid)],
                  eval_names = ['train', 'valid'],
                  eval_metric='binary_logloss',
                  callbacks=[lightgbm.early_stopping(100), lightgbm.log_evaluation(100)])
        
        self.model = model
    
        auc_train = self.calc_auc(data.X_train, data.y_train)
        auc_test = self.calc_auc(data.X_valid, data.y_valid)
        
        print(f"\n\nauc_train = {auc_train:.3f}\nauc_test = {auc_test:.3f}\n")
        
        self._y_valid = data.y_valid
        self._pr_valid = self.predict(data.X_valid)
        self._columns = X.columns
        
    def fit_with_grid_search(self, X: pd.DataFrame, y: pd.Series, param_grid: dict, rc_params: dict):
        
        data = self._split_train_test(X, y)
        
        lg_train = lightgbm.Dataset(data.X_train, label=data.y_train)
        lg_valid = lightgbm.Dataset(data.X_valid, label=data.y_valid)
        
        
        grid_search_res = {}

        model = LGBMClassifier()

        # RandomizedSearchCV, GridSearchCV
        grid_search = RandomizedSearchCV(
            estimator=model,
            param_distributions=param_grid,
            scoring='roc_auc',
            n_iter=20,
            n_jobs=20,
            verbose=-1,
            **rc_params
        )

        grid_search.fit(
            data.X_train, data.y_train
        )
        
        self.model = grid_search.best_estimator_
        
        self._y_valid = data.y_valid
        self._pr_valid = self.predict(data.X_valid)
        self._columns = X.columns

        print(f'Best AUC: {grid_search.best_score_}')
        print('Best params:')
        print(grid_search.best_params_)
        
        auc_train = self.calc_auc(data.X_train, data.y_train)
        auc_test = self.calc_auc(data.X_valid, data.y_valid)
        
        print(f"\n\nauc_train = {auc_train:.3f}\nauc_test = {auc_test:.3f}\n")

    def get_prediction_table(self, num_buck: int=10) -> pd.DataFrame:
        
        buck_df = pd.DataFrame({'y':self._y_valid, 'pr': self._pr_valid})
        # print(buck_df.shape)
        buck_df = buck_df.sort_values('pr', ascending=False).reset_index(drop=True)
        # print(buck_df.head(50))
        buck_df['buck'] = buck_df.index * num_buck // len(buck_df)
        # print(buck_df.iloc[200:250].head(50))
        buck_df = buck_df.groupby('buck').agg({'pr': ['max'], 'y': ['mean', 'size']})
        buck_df.columns = ['max_pr', 'av_target', 'bucket_size']
        
        return buck_df
    
    def get_feature_inportance(self) -> pd.DataFrame:
        
        fi = pd.DataFrame({'fi': self.model.feature_importances_, 'col': self._columns}) \
            .sort_values('fi', ascending=False)
        
        return fi