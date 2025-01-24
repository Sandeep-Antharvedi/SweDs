# Read Me
Hemorrhage Risk Prediction Demo
This project provides an interactive demonstration of predicting hemorrhage risk from patient lab values across three points in time. It uses a frontend built with Svelte and a backend powered by FastAPI and PyTorch.

Features
Adjust Lab Values via Sliders:
Change patient lab values (Hemoglobin, Hematocrit, Platelet Count, INR, and PTT) at three different time points using slider inputs.

Predict Button:
After adjusting the sliders, click "Predict" to send the data to the backend. The backend model returns hemorrhage risk predictions for each stage (after 1st, 2nd, and 3rd data points).

Dynamic Visualization:
A line chart (rendered with Chart.js) displays how hemorrhage risk changes as additional time points are considered. The final risk is shown numerically, and if the 3rd time point prediction exceeds 17%, a "WARNING" message appears.

No Exact Timestamp Needed:
The model interprets these time points as sequential measurements, not bound to real-world timestamps. It focuses on how the values evolve from one step to the next.

Technology Stack
Frontend: Svelte for building a reactive user interface, slider inputs, and chart rendering (Chart.js).
Backend: FastAPI for handling the prediction requests, serving a PyTorch model that processes the input data.
Model: PyTorch model for multi-step risk prediction, trained separately and loaded at runtime.
Scaling and Constants: The backend applies scaling to input values and provides some constant inputs behind the scenes, ensuring compatibility with the model’s training conditions.
For Running
You need the google cloud permissions from Eric, esimon10@jhu.edu
