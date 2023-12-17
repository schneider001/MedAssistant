import pickle5 as pickle
from typing import List, Any
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier


def save_model(obj : Any, path : str):
    with open(path, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(path : str):
    with open(path, 'rb') as handle:
        obj = pickle.load(handle)

    return obj


class DiseasePredModel:
    def __init__(self, path : str = ""):
        if path == "":
            self.__path_saved_model = "model_predict.pkl"
        else:
            self.__path_saved_model = "model_predict.pkl"

        disease_pred_model = load_pickle(self.__path_saved_model)
        self.model = disease_pred_model['model']
        # self.label_encoder = disease_pred_model['label_encoder']
        # self.features = disease_pred_model['features']

        self.count_symptoms = 17
        self.symptoms_weight_dict = self._get_weight_symptom()

    
    def predict(self, symptoms : List[str]) -> float:
        input_data = self._get_input(symptoms)

        result = self.model.predict(input_data.reshape(1, self.count_symptoms))

        return result

    
    def _get_weight_symptom(self):
        weight_symptoms = pd.read_csv('Symptom-severity.csv')
        symptoms_weight_dict = {symptom.lower() : weight_symptoms.loc[weight_symptoms['Symptom'] == symptom]['weight'] for symptom in weight_symptoms['Symptom']}
        symptoms_weight_dict['dischromic  patches'] = 0
        symptoms_weight_dict['spotting  urination'] = 0
        symptoms_weight_dict['foul smell of urine'] = 0

        return symptoms_weight_dict
        
    
    def _get_input(self, symptoms : List[str]) -> List[int]:
        input_data = np.zeros(self.count_symptoms)
        for idx, symptom in enumerate(symptoms[:17]):
            if type(symptom) == str:
                input_data[idx] = self.symptoms_weight_dict.get(symptom.replace(' ', '_').lower(), 0)
            else:
                input_data[idx] = 0
                
        return input_data