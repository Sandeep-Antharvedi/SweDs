from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import List

app = FastAPI()

origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MultiTaskLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int):
        super(MultiTaskLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(
            input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True, dropout=0.2
        )
        self.fc_hemorrhage = nn.Linear(hidden_size, 1)
        self.fc_icu = nn.Linear(hidden_size, 1)

    def forward(self, x: torch.Tensor):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        shared_features = out[:, -1, :]
        hemorrhage_output = torch.sigmoid(self.fc_hemorrhage(shared_features))
        icu_output = torch.sigmoid(self.fc_icu(shared_features))
        return hemorrhage_output, icu_output

MODEL_PATH = 'model/multitask_lstm.pth'
model = MultiTaskLSTM(input_size=7, hidden_size=256, num_layers=4)
state_dict = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
model.load_state_dict(state_dict)
model.eval()

scaler = MinMaxScaler()
scaler.fit(np.array([
    [0, 0, 0, 0, 0, 0, 0],     
    [20, 60, 1000, 100, 10, 200, 1000]  
]))

class TimePoint(BaseModel):
    Hemoglobin: float
    Hematocrit: float
    Platelet_Count: float
    INR_PT: float
    PTT: float

class PredictionRequest(BaseModel):
    time_series: List[TimePoint]

class PredictionResponse(BaseModel):
    hemorrhage_risk: float
    icu_admission_risk: float

@app.post("/predict", response_model=PredictionResponse)
def predict(data: PredictionRequest):
    if len(data.time_series) != 3:
        raise HTTPException(status_code=400, detail="Exactly 3 time points are required.")

    PROTHROMBIN_TIME_PT = 12.0
    FIBRINOGEN = 300.0

    input_data = np.array([
        [
            point.Hemoglobin,
            point.Hematocrit,
            point.Platelet_Count,
            PROTHROMBIN_TIME_PT,
            point.INR_PT,
            point.PTT,
            FIBRINOGEN
        ]
        for point in data.time_series
    ])

    scaled_input = scaler.transform(input_data)
    input_tensor = torch.tensor(scaled_input, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        hemorrhage_pred, icu_pred = model(input_tensor)
        hemo_prob = hemorrhage_pred.item() * 100
        icu_prob = icu_pred.item() * 100

    return PredictionResponse(
        hemorrhage_risk=round(hemo_prob, 2),
        icu_admission_risk=round(icu_prob, 2)
    )

@app.get("/")
def read_root():
    return {"message": "ICU Admission and Hemorrhage Risk Prediction API"}
