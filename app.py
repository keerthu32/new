#!/usr/bin/env python3
"""Enhanced Dementia Prediction System: dataset + training + Flask UI."""

import json
import os
import sqlite3
from functools import wraps
from typing import Any

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from werkzeug.security import check_password_hash, generate_password_hash
from xgboost import XGBClassifier


class DementiaDatasetGenerator:
    def __init__(self, n_samples: int = 20000) -> None:
        self.n_samples = n_samples

    def generate_comprehensive_dataset(self) -> pd.DataFrame:
        age = np.random.beta(2, 3, self.n_samples) * 100
        age = np.clip(age, 0, 100).astype(int)

        missing = set(range(101)) - set(np.unique(age))
        if missing:
            age = np.append(age, list(missing))

        if len(age) > self.n_samples:
            age = age[: self.n_samples]
        elif len(age) < self.n_samples:
            age = np.append(age, np.random.choice(range(101), self.n_samples - len(age)))
        np.random.shuffle(age)

        gender = np.random.choice(["M", "F"], self.n_samples, p=[0.48, 0.52])
        hand = np.random.choice(["R", "L"], self.n_samples, p=[0.9, 0.1])

        education = np.where(
            age < 18,
            np.random.normal(8, 2, self.n_samples),
            np.where(
                age < 65,
                np.random.normal(13, 3, self.n_samples),
                np.random.normal(12, 4, self.n_samples),
            ),
        )
        education = np.clip(education, 0, 22).astype(int)
        ses = np.random.choice([1, 2, 3, 4, 5], self.n_samples, p=[0.12, 0.18, 0.35, 0.22, 0.13])

        mmse_base = 30 - np.maximum(0, (age - 30) * 0.08)
        mmse = mmse_base + np.random.normal(0, 1.5, self.n_samples) - (education - 12) * 0.1
        mmse = np.clip(mmse, 0, 30).round(1)

        cdr_prob = 1 / (1 + np.exp(-((age - 65) / 12) - (mmse - 27) / 4))
        cdr = np.where(cdr_prob < 0.2, 0, np.where(cdr_prob < 0.35, 0.5, np.where(cdr_prob < 0.55, 1, np.where(cdr_prob < 0.75, 2, 3))))

        etiv = np.random.normal(1450 + (gender == "M") * 120, 110, self.n_samples)
        etiv = np.clip(etiv, 1100, 2100).astype(int)

        nwbv = 0.78 - np.maximum(0, (age - 50) * 0.002) - (cdr * 0.06) + np.random.normal(0, 0.035, self.n_samples)
        nwbv = np.clip(nwbv, 0.48, 0.86).round(3)

        asf = np.clip(np.random.normal(1, 0.12, self.n_samples), 0.7, 1.3).round(3)
        hypertension = np.random.binomial(1, np.clip(0.05 + (age / 100) * 0.6, 0, 0.75))
        diabetes = np.random.binomial(1, np.clip(0.02 + (age / 100) * 0.35, 0, 0.35))
        family_history = np.random.binomial(1, 0.22)
        gds = np.clip(1.5 + (age / 100) * 8 + np.random.normal(0, 1.5, self.n_samples), 0, 15).round(1)
        adl = np.clip(6 - cdr * 1.2 - np.random.normal(0, 0.4, self.n_samples), 0, 6).round(1)

        diagnosis = np.where((cdr >= 1) | (mmse < 24), "Demented", "Nondemented")
        return pd.DataFrame(
            {
                "Patient_ID": [f"P_{i:05d}" for i in range(1, self.n_samples + 1)],
                "Age": age,
                "Gender": gender,
                "Handedness": hand,
                "Education_Years": education,
                "Socioeconomic_Status": ses,
                "MMSE_Score": mmse,
                "CDR_Score": cdr,
                "eTIV": etiv,
                "nWBV": nwbv,
                "ASF": asf,
                "Hypertension": hypertension,
                "Diabetes": diabetes,
                "Family_History_Dementia": family_history,
                "GDS_Score": gds,
                "ADL_Score": adl,
                "Diagnosis": diagnosis,
            }
        )


class DementiaAIModel:
    def __init__(self) -> None:
        self.scaler = StandardScaler()
        self.label_encoders: dict[str, LabelEncoder] = {}
        self.feature_columns = [
            "Age",
            "Education_Years",
            "Socioeconomic_Status",
            "MMSE_Score",
            "eTIV",
            "nWBV",
            "ASF",
            "Hypertension",
            "Diabetes",
            "Family_History_Dementia",
            "GDS_Score",
            "ADL_Score",
        ]
        self.models: dict[str, Any] = {}

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        x = df[self.feature_columns].copy()
        x["Age_MMSE"] = x["Age"] * x["MMSE_Score"]
        x["Age_Education"] = x["Age"] * x["Education_Years"]
        x["MMSE_Education"] = x["MMSE_Score"] * x["Education_Years"]
        x["GDS_ADL_Ratio"] = x["GDS_Score"] / (x["ADL_Score"] + 0.1)
        x["Age_Squared"] = x["Age"] ** 2
        x["MMSE_Squared"] = x["MMSE_Score"] ** 2

        if "Gender" in df.columns:
            le = LabelEncoder()
            x["Gender_Encoded"] = le.fit_transform(df["Gender"])
            self.label_encoders["Gender"] = le
        if "Handedness" in df.columns:
            le = LabelEncoder()
            x["Handedness_Encoded"] = le.fit_transform(df["Handedness"])
            self.label_encoders["Handedness"] = le
        return x

    def train(self, df: pd.DataFrame) -> dict[str, dict[str, float]]:
        x = self.prepare_features(df)
        y = (df["Diagnosis"] == "Demented").astype(int)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)
        x_train_scaled = self.scaler.fit_transform(x_train)
        x_test_scaled = self.scaler.transform(x_test)

        self.models["random_forest"] = RandomForestClassifier(n_estimators=160, max_depth=14, min_samples_split=10, random_state=42, n_jobs=-1, class_weight="balanced")
        self.models["random_forest"].fit(x_train_scaled, y_train)

        self.models["xgboost"] = XGBClassifier(n_estimators=180, max_depth=7, learning_rate=0.05, random_state=42, eval_metric="logloss")
        self.models["xgboost"].fit(x_train_scaled, y_train)

        self.models["gradient_boosting"] = GradientBoostingClassifier(n_estimators=140, learning_rate=0.05, random_state=42)
        self.models["gradient_boosting"].fit(x_train_scaled, y_train)

        self.models["voting"] = VotingClassifier(
            estimators=[("rf", self.models["random_forest"]), ("xgb", self.models["xgboost"]), ("gb", self.models["gradient_boosting"])],
            voting="soft",
        )
        self.models["voting"].fit(x_train_scaled, y_train)

        results = {}
        for name, model in self.models.items():
            pred = model.predict(x_test_scaled)
            prob = model.predict_proba(x_test_scaled)[:, 1]
            results[name] = {"accuracy": float(accuracy_score(y_test, pred)), "auc": float(roc_auc_score(y_test, prob))}
        return results

    def save_models(self) -> None:
        os.makedirs("models", exist_ok=True)
        for name, model in self.models.items():
            joblib.dump(model, f"models/{name}.pkl")
        joblib.dump(self.scaler, "models/scaler.pkl")
        joblib.dump(self.label_encoders, "models/label_encoders.pkl")

    def load_models(self) -> None:
        self.models["random_forest"] = joblib.load("models/random_forest.pkl")
        self.models["xgboost"] = joblib.load("models/xgboost.pkl")
        self.models["gradient_boosting"] = joblib.load("models/gradient_boosting.pkl")
        self.models["voting"] = joblib.load("models/voting.pkl")
        self.scaler = joblib.load("models/scaler.pkl")
        self.label_encoders = joblib.load("models/label_encoders.pkl")

    def predict(self, patient_data: dict[str, Any]) -> dict[str, Any]:
        input_df = pd.DataFrame([patient_data])
        x = self.prepare_features(input_df)
        x_scaled = self.scaler.transform(x)

        predictions: dict[str, float] = {}
        for name, model in self.models.items():
            proba = float(model.predict_proba(x_scaled)[0, 1])
            predictions[name] = proba

        if not predictions:
            raise RuntimeError("No models are loaded. Train or load model first.")

        final = float(np.mean(list(predictions.values())))
        if final < 0.3:
            risk, color = "Low Risk", "#198754"
        elif final < 0.6:
            risk, color = "Moderate Risk", "#fd7e14"
        elif final < 0.8:
            risk, color = "High Risk", "#dc3545"
        else:
            risk, color = "Very High Risk", "#7a0012"

        recs = [
            "Maintain a structured routine with physical, social, and cognitive activities.",
            "Schedule periodic neurological/cognitive follow-up with a clinician.",
            "Track memory changes and daily functioning weekly.",
            "Optimize blood pressure, glucose, sleep, and stress with your care team.",
        ]

        return {
            "dementia_probability": round(final * 100, 2),
            "risk_level": risk,
            "risk_color": color,
            "prediction": "Demented" if final > 0.5 else "Non-Demented",
            "confidence": round(abs(final - 0.5) * 200, 2),
            "model_predictions": {k: round(v * 100, 2) for k, v in predictions.items()},
            "recommendations": recs,
            "interpretation": f"AI-estimated dementia probability is {round(final*100,1)}% based on provided profile.",
        }


LOGIN_TEMPLATE = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Dementia AI - Login</title>
<style>
:root{--brand:#4f46e5;--brand2:#7c3aed;--bg:#f6f7fb;--card:#ffffff;--muted:#64748b}
*{box-sizing:border-box}body{margin:0;font-family:Inter,Segoe UI,sans-serif;background:linear-gradient(120deg,#eef2ff,#f8fafc);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
.wrap{display:grid;grid-template-columns:1.05fr 1fr;max-width:980px;width:100%;background:var(--card);border-radius:20px;overflow:hidden;box-shadow:0 15px 40px rgba(15,23,42,.15)}
.hero{background:linear-gradient(145deg,var(--brand),var(--brand2));color:#fff;padding:38px}.hero h1{margin-top:0}.hero p{opacity:.95;line-height:1.5}
.panel{padding:34px}.title{margin:0 0 20px}.fg{margin-bottom:14px}label{display:block;font-weight:600;margin-bottom:6px}
input,select{width:100%;padding:12px;border:1px solid #dbe2ea;border-radius:10px}.btn{width:100%;padding:12px;border:none;border-radius:10px;background:linear-gradient(135deg,var(--brand),var(--brand2));color:#fff;font-weight:700;cursor:pointer}
.alert{padding:10px;border-radius:10px;margin-bottom:12px}.err{background:#fee2e2;color:#991b1b}.ok{background:#dcfce7;color:#166534}.hint{color:var(--muted);margin-top:14px;text-align:center}
@media(max-width:840px){.wrap{grid-template-columns:1fr}}
</style></head><body>
<div class='wrap'><div class='hero'><h1>🧠 Dementia AI Assistant</h1><p>Enhanced UI for patient screening, clinician review, and longitudinal monitoring.</p><p>• Real-time risk scoring<br>• Recommendation engine<br>• Doctor oversight dashboard</p></div>
<div class='panel'><h2 class='title'>{{ mode|capitalize }}</h2>
{% if error %}<div class='alert err'>{{ error }}</div>{% endif %}{% if success %}<div class='alert ok'>{{ success }}</div>{% endif %}
<form method='POST'><div class='fg'><label>Email</label><input type='email' name='email' required></div><div class='fg'><label>Password</label><input type='password' name='password' required minlength='6'></div>
{% if mode == 'register' %}<div class='fg'><label>Full Name</label><input type='text' name='full_name' required></div><div class='fg'><label>Role</label><select name='role'><option value='patient'>Patient</option><option value='doctor'>Doctor</option></select></div>{% endif %}
<button class='btn' type='submit'>{{ 'Register' if mode == 'register' else 'Login' }}</button></form>
<div class='hint'>{% if mode=='login' %}<a href='?mode=register'>Need an account? Register</a>{% else %}<a href='?mode=login'>Already registered? Login</a>{% endif %}</div></div></div></body></html>
"""

PATIENT_TEMPLATE = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Patient Dashboard</title>
<style>
body{margin:0;font-family:Inter,Segoe UI,sans-serif;background:#f8fafc;color:#0f172a}.top{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:18px 24px;display:flex;justify-content:space-between;align-items:center}.logout{color:#fff;text-decoration:none;background:rgba(255,255,255,.2);padding:9px 12px;border-radius:8px}
.container{max-width:1200px;margin:22px auto;padding:0 16px}.card{background:#fff;border-radius:16px;padding:22px;box-shadow:0 8px 24px rgba(15,23,42,.08);margin-bottom:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
input,select{width:100%;padding:10px;border:1px solid #dbe2ea;border-radius:10px}.btn{margin-top:12px;width:100%;padding:12px;border:0;border-radius:12px;background:#4f46e5;color:#fff;font-weight:700;cursor:pointer}.result{display:none}
.metric{font-size:2rem;font-weight:800;text-align:center}.risk{font-weight:700;text-align:center;padding:10px;border-radius:10px;margin:10px 0}
small{color:#64748b}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}.stat{background:#eef2ff;border-radius:12px;padding:12px}.stat .v{font-size:1.4rem;font-weight:800;color:#4338ca}
table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #e2e8f0;text-align:left}th{background:#f8fafc}
</style></head><body>
<div class='top'><div><strong>🧠 Dementia AI</strong> · Patient</div><a class='logout' href='/logout'>Logout</a></div>
<div class='container'>
<div class='card'><h2>Welcome, {{ user.full_name }}</h2><small>Complete the assessment to get AI-supported cognitive risk insights.</small><div class='stats' style='margin-top:12px'><div class='stat'><div class='v' id='totalAssessments'>0</div><div>Total Assessments</div></div><div class='stat'><div class='v' id='avgRisk'>0%</div><div>Average Risk</div></div><div class='stat'><div class='v' id='latestRisk'>N/A</div><div>Latest Risk Level</div></div></div></div>
<div class='card'><h3>Cognitive Assessment</h3><div class='grid'>
<div><label>Age</label><input id='Age' type='number' min='0' max='120' required></div>
<div><label>Education Years</label><input id='Education_Years' type='number' min='0' max='25' required></div>
<div><label>MMSE Score</label><input id='MMSE_Score' type='number' min='0' max='30' step='0.5' required></div>
<div><label>Socioeconomic Status</label><select id='Socioeconomic_Status'><option>1</option><option>2</option><option selected>3</option><option>4</option><option>5</option></select></div>
<div><label>Gender</label><select id='Gender'><option value='F'>Female</option><option value='M'>Male</option></select></div>
<div><label>Handedness</label><select id='Handedness'><option value='R'>Right</option><option value='L'>Left</option></select></div>
<div><label>Hypertension</label><select id='Hypertension'><option value='0'>No</option><option value='1'>Yes</option></select></div>
<div><label>Diabetes</label><select id='Diabetes'><option value='0'>No</option><option value='1'>Yes</option></select></div>
<div><label>Family History Dementia</label><select id='Family_History_Dementia'><option value='0'>No</option><option value='1'>Yes</option></select></div>
<div><label>GDS</label><input id='GDS_Score' type='number' min='0' max='15' value='3'></div>
<div><label>ADL</label><input id='ADL_Score' type='number' min='0' max='6' value='6'></div>
<div><label>eTIV</label><input id='eTIV' type='number' min='1100' max='2100' value='1500'></div>
<div><label>nWBV</label><input id='nWBV' type='number' min='0.5' max='0.85' step='0.01' value='0.75'></div>
<div><label>ASF</label><input id='ASF' type='number' min='0.7' max='1.3' step='0.01' value='1'></div>
</div><button class='btn' onclick='predict()'>Predict Risk</button></div>
<div class='card result' id='result'><h3>Result</h3><div class='metric' id='prob'></div><div class='risk' id='risk'></div><p id='interp'></p><ul id='recs'></ul><button class='btn' onclick='savePred()'>Save Assessment</button></div>
<div class='card'><h3>Assessment History</h3><table><thead><tr><th>Date</th><th>Probability</th><th>Risk</th><th>Prediction</th></tr></thead><tbody id='historyBody'><tr><td colspan='4'>Loading...</td></tr></tbody></table></div>
<div class='card'><h3>Doctor Care Plan</h3><div><strong>Active Medications</strong><ul id='medicationsList'><li>Loading...</li></ul></div><div style='margin-top:10px'><strong>Care Tasks</strong><ul id='taskList'><li>Loading...</li></ul></div></div>
</div>
<script>
let lastResult = null;
function getData(){const ids=['Age','Education_Years','MMSE_Score','Socioeconomic_Status','Gender','Handedness','Hypertension','Diabetes','Family_History_Dementia','GDS_Score','ADL_Score','eTIV','nWBV','ASF'];const o={};ids.forEach(i=>{const v=document.getElementById(i).value;o[i]=isNaN(v)||['Gender','Handedness'].includes(i)?v:Number(v)});return o}
async function predict(){const res=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(getData())});const data=await res.json();if(data.error){alert(data.error);return;}lastResult=data;document.getElementById('result').style.display='block';document.getElementById('prob').textContent=`${data.dementia_probability}%`;const r=document.getElementById('risk');r.textContent=data.risk_level;r.style.background=data.risk_color+'25';r.style.color=data.risk_color;document.getElementById('interp').textContent=data.interpretation;document.getElementById('recs').innerHTML=data.recommendations.map(x=>`<li>${x}</li>`).join('')}
async function savePred(){if(!lastResult)return;const payload={...lastResult,input:getData()};const res=await fetch('/api/save-prediction',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await res.json();alert(data.success?'Saved successfully':'Error saving prediction');if(data.success){loadHistory();}}
async function loadHistory(){const res=await fetch('/api/prediction-history');const data=await res.json();const rows=data.predictions||[];const body=document.getElementById('historyBody');if(!rows.length){body.innerHTML=\"<tr><td colspan='4'>No assessments yet.</td></tr>\";document.getElementById('totalAssessments').textContent='0';document.getElementById('avgRisk').textContent='0%';document.getElementById('latestRisk').textContent='N/A';return;}body.innerHTML=rows.map(r=>`<tr><td>${new Date(r.date).toLocaleString()}</td><td>${r.probability}%</td><td>${r.risk_level}</td><td>${r.prediction}</td></tr>`).join('');const avg=(rows.reduce((a,b)=>a+Number(b.probability),0)/rows.length).toFixed(1);document.getElementById('totalAssessments').textContent=rows.length;document.getElementById('avgRisk').textContent=avg+'%';document.getElementById('latestRisk').textContent=rows[0].risk_level;}
async function loadCarePlan(){const res=await fetch('/api/patient/care-plan');const data=await res.json();document.getElementById('medicationsList').innerHTML=(data.medications||[]).map(m=>`<li><strong>${m.medicine_name}</strong> — ${m.dosage}, ${m.frequency} (${m.status})</li>`).join('')||'<li>No active medications assigned.</li>';document.getElementById('taskList').innerHTML=(data.tasks||[]).map(t=>`<li>${t.task_title}${t.due_date?` (Due: ${t.due_date})`:''}${t.completed?' ✅':''}</li>`).join('')||'<li>No care tasks assigned.</li>';}
loadHistory();
loadCarePlan();
</script></body></html>
"""

DOCTOR_TEMPLATE = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Doctor Dashboard</title>
<style>body{margin:0;font-family:Inter,Segoe UI,sans-serif;background:#f8fafc}.top{display:flex;justify-content:space-between;padding:18px 24px;background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff}.logout{color:#fff;text-decoration:none;background:rgba(255,255,255,.2);padding:8px 12px;border-radius:8px}.container{max-width:1200px;margin:24px auto;padding:0 16px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.card{background:#fff;padding:18px;border-radius:14px;box-shadow:0 8px 18px rgba(15,23,42,.07)}.num{font-size:1.8rem;font-weight:800;color:#4f46e5}.table{margin-top:16px;background:#fff;border-radius:14px;padding:16px;overflow:auto}table{width:100%;border-collapse:collapse}th,td{padding:10px;border-bottom:1px solid #eef2f7;text-align:left}.toolbar{display:flex;gap:10px;margin:10px 0}.toolbar input,.toolbar select{padding:8px;border:1px solid #dbe2ea;border-radius:8px}.btn{background:#4f46e5;color:white;border:0;border-radius:8px;padding:8px 10px;cursor:pointer}.modal{position:fixed;inset:0;background:rgba(15,23,42,.5);display:none;align-items:center;justify-content:center}.modal .content{width:min(800px,94vw);background:#fff;border-radius:12px;padding:16px;max-height:85vh;overflow:auto}</style>
</head><body><div class='top'><strong>👨‍⚕️ Doctor Dashboard</strong><a class='logout' href='/logout'>Logout</a></div>
<div class='container'><div class='cards'><div class='card'><div class='num' id='totalP'>0</div><div>Patients</div></div><div class='card'><div class='num' id='highR'>0</div><div>High Risk</div></div><div class='card'><div class='num' id='avgR'>0%</div><div>Average Risk</div></div><div class='card'><div class='num' id='totalA'>0</div><div>Assessments</div></div></div>
<div class='table'><h3>Patient List</h3><div class='toolbar'><input id='search' placeholder='Search patient by name/email'><select id='riskFilter'><option value=''>All risks</option><option>Low Risk</option><option>Moderate Risk</option><option>High Risk</option><option>Very High Risk</option><option>No data</option></select><button class='btn' onclick='load()'>Apply</button></div><table><thead><tr><th>Name</th><th>Email</th><th>Risk</th><th>Last Assessment</th><th>Actions</th></tr></thead><tbody id='body'><tr><td colspan='5'>Loading…</td></tr></tbody></table></div></div>
<div id='modal' class='modal' onclick='if(event.target.id==\"modal\"){closeModal()}'><div class='content'><button class='btn' onclick='closeModal()' style='float:right'>Close</button><div id='modalContent'></div></div></div>
<script>
async function load(){const search=(document.getElementById('search').value||'').toLowerCase();const riskFilter=document.getElementById('riskFilter').value;const res=await fetch('/api/doctor/dashboard');const d=await res.json();document.getElementById('totalP').textContent=d.total_patients;document.getElementById('highR').textContent=d.high_risk_patients;document.getElementById('avgR').textContent=d.avg_risk_score+'%';document.getElementById('totalA').textContent=d.total_assessments;const filtered=(d.patients||[]).filter(p=>(!riskFilter||p.risk_level===riskFilter)&&(`${p.full_name} ${p.email}`.toLowerCase().includes(search)));document.getElementById('body').innerHTML=filtered.map(p=>`<tr><td>${p.full_name}</td><td>${p.email}</td><td>${p.risk_level}</td><td>${p.last_assessment||'Never'}</td><td><button class='btn' onclick='openDetails(${p.id})'>Details</button></td></tr>`).join('')||\"<tr><td colspan='5'>No patients</td></tr>\"}
async function openDetails(patientId){const res=await fetch(`/api/doctor/patient/${patientId}`);const d=await res.json();const historyRows=(d.history||[]).map(h=>`<tr><td>${new Date(h.date).toLocaleString()}</td><td>${h.risk_level}</td><td>${h.probability}%</td></tr>`).join('')||\"<tr><td colspan='3'>No history</td></tr>\";const meds=(d.medications||[]).map(m=>`<li>${m.medicine_name} — ${m.dosage}, ${m.frequency} (${m.status})</li>`).join('')||'<li>No medications</li>';const tasks=(d.tasks||[]).map(t=>`<li>${t.task_title}${t.due_date?` (Due ${t.due_date})`:''}${t.completed?' ✅':''}</li>`).join('')||'<li>No tasks</li>';document.getElementById('modalContent').innerHTML=`<h3>${d.full_name}</h3><p><strong>Email:</strong> ${d.email}</p><p><strong>Age:</strong> ${d.age||'N/A'} | <strong>Gender:</strong> ${d.gender||'N/A'} | <strong>Education:</strong> ${d.education||'N/A'}</p><h4>Recent Assessments</h4><table><thead><tr><th>Date</th><th>Risk</th><th>Probability</th></tr></thead><tbody>${historyRows}</tbody></table><h4>Latest Recommendations</h4><ul>${(d.latest_recommendations||[]).map(x=>`<li>${x}</li>`).join('')||'<li>No recommendations</li>'}</ul><h4>Medication Plan</h4><ul>${meds}</ul><h4>Care Tasks</h4><ul>${tasks}</ul><div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px'><input id='medName' placeholder='Medicine name'><input id='medDose' placeholder='Dosage e.g. 10mg'><input id='medFreq' placeholder='Frequency e.g. once daily'><button class='btn' onclick='addMedication(${patientId})'>Add Medication</button><input id='taskTitle' placeholder='Task title'><input id='taskDue' placeholder='Due date YYYY-MM-DD'><button class='btn' onclick='addTask(${patientId})'>Add Task</button><textarea id='doctorNote' placeholder='Doctor note' style='grid-column:1/3;min-height:70px'></textarea><button class='btn' style='grid-column:1/3' onclick='addNote(${patientId})'>Save Clinical Note</button></div>`;document.getElementById('modal').style.display='flex';}
async function addMedication(patientId){const payload={medicine_name:document.getElementById('medName').value,dosage:document.getElementById('medDose').value,frequency:document.getElementById('medFreq').value,start_date:new Date().toISOString().slice(0,10)};const r=await fetch(`/api/doctor/patient/${patientId}/medication`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const d=await r.json();alert(d.success?'Medication saved':'Failed to save medication');if(d.success)openDetails(patientId);}
async function addTask(patientId){const payload={task_title:document.getElementById('taskTitle').value,due_date:document.getElementById('taskDue').value};const r=await fetch(`/api/doctor/patient/${patientId}/task`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const d=await r.json();alert(d.success?'Task saved':'Failed to save task');if(d.success)openDetails(patientId);}
async function addNote(patientId){const payload={note:document.getElementById('doctorNote').value};const r=await fetch(`/api/doctor/patient/${patientId}/note`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const d=await r.json();alert(d.success?'Note saved':'Failed to save note');if(d.success)openDetails(patientId);}
function closeModal(){document.getElementById('modal').style.display='none';}
load();setInterval(load,30000)
</script></body></html>
"""


app = Flask(__name__)
app.secret_key = os.getenv("DEMENTIA_APP_SECRET", "dev-dementia-secret-key")
ai_model = DementiaAIModel()


def init_database() -> None:
    conn = sqlite3.connect("dementia_system.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS patient_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        age INTEGER,
        gender TEXT,
        education_years INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        probability REAL NOT NULL,
        risk_level TEXT NOT NULL,
        prediction TEXT NOT NULL,
        input_data TEXT,
        recommendations TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS doctor_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        note TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        frequency TEXT NOT NULL,
        start_date TEXT,
        end_date TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS care_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        task_title TEXT NOT NULL,
        due_date TEXT,
        completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
    )
    conn.commit()
    conn.close()


def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", mode="login"))
        return f(*args, **kwargs)

    return inner


def role_required(role):
    def deco(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if "user_id" not in session or session.get("role") != role:
                return jsonify({"error": "Unauthorized"}), 403
            return f(*args, **kwargs)

        return inner

    return deco


def validate_prediction_input(data: dict[str, Any]) -> dict[str, Any]:
    schema = {
        "Age": (0, 120),
        "Education_Years": (0, 25),
        "MMSE_Score": (0, 30),
        "Socioeconomic_Status": (1, 5),
        "Hypertension": (0, 1),
        "Diabetes": (0, 1),
        "Family_History_Dementia": (0, 1),
        "GDS_Score": (0, 15),
        "ADL_Score": (0, 6),
        "eTIV": (1100, 2100),
        "nWBV": (0.48, 0.9),
        "ASF": (0.7, 1.3),
    }
    for key, bounds in schema.items():
        if key not in data:
            raise ValueError(f"Missing field: {key}")
        val = float(data[key])
        if val < bounds[0] or val > bounds[1]:
            raise ValueError(f"{key} must be between {bounds[0]} and {bounds[1]}")
    if data.get("Gender") not in {"M", "F"}:
        raise ValueError("Gender must be M or F")
    if data.get("Handedness") not in {"R", "L"}:
        raise ValueError("Handedness must be R or L")
    return data


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("doctor_dashboard" if session.get("role") == "doctor" else "patient_dashboard"))
    return redirect(url_for("login", mode="login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    mode = request.args.get("mode", "login")
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = sqlite3.connect("dementia_system.db")
        c = conn.cursor()
        if mode == "login":
            c.execute("SELECT id, password, full_name, role FROM users WHERE email = ?", (email,))
            user = c.fetchone()
            conn.close()
            if user and check_password_hash(user[1], password):
                session["user_id"], session["full_name"], session["role"] = user[0], user[2], user[3]
                return redirect(url_for("doctor_dashboard" if user[3] == "doctor" else "patient_dashboard"))
            return render_template_string(LOGIN_TEMPLATE, mode=mode, error="Invalid email or password.")

        full_name = request.form.get("full_name", "").strip()
        role = request.form.get("role", "patient")
        if role not in {"patient", "doctor"}:
            conn.close()
            return render_template_string(LOGIN_TEMPLATE, mode=mode, error="Invalid role selected.")
        try:
            c.execute("INSERT INTO users (email, password, full_name, role) VALUES (?, ?, ?, ?)", (email, generate_password_hash(password), full_name, role))
            conn.commit()
            return render_template_string(LOGIN_TEMPLATE, mode="login", success="Registration successful. Please login.")
        except sqlite3.IntegrityError:
            return render_template_string(LOGIN_TEMPLATE, mode=mode, error="Email already exists.")
        finally:
            conn.close()

    return render_template_string(LOGIN_TEMPLATE, mode=mode)


@app.route("/patient-dashboard")
@login_required
def patient_dashboard():
    if session.get("role") != "patient":
        return redirect(url_for("doctor_dashboard"))
    return render_template_string(PATIENT_TEMPLATE, user=session)


@app.route("/doctor-dashboard")
@login_required
def doctor_dashboard():
    if session.get("role") != "doctor":
        return redirect(url_for("patient_dashboard"))
    return render_template_string(DOCTOR_TEMPLATE, user=session)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login", mode="login"))


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "models_loaded": list(ai_model.models.keys())})


@app.route("/api/predict", methods=["POST"])
@login_required
def api_predict():
    payload = request.get_json(force=True)
    try:
        data = validate_prediction_input(payload)
        return jsonify(ai_model.predict(data))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/save-prediction", methods=["POST"])
@login_required
def save_prediction():
    data = request.get_json(force=True)
    conn = sqlite3.connect("dementia_system.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO predictions (user_id, probability, risk_level, prediction, input_data, recommendations) VALUES (?, ?, ?, ?, ?, ?)",
        (
            session["user_id"],
            data["dementia_probability"],
            data["risk_level"],
            data["prediction"],
            json.dumps(data),
            json.dumps(data.get("recommendations", [])),
        ),
    )
    raw_input = data.get("input", {})
    if raw_input:
        c.execute(
            "INSERT INTO patient_profiles (user_id, age, gender, education_years) VALUES (?, ?, ?, ?)",
            (session["user_id"], raw_input.get("Age"), raw_input.get("Gender"), raw_input.get("Education_Years")),
        )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/prediction-history", methods=["GET"])
@login_required
def prediction_history():
    conn = sqlite3.connect("dementia_system.db")
    c = conn.cursor()
    c.execute(
        "SELECT probability, risk_level, prediction, created_at FROM predictions WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
        (session["user_id"],),
    )
    rows = c.fetchall()
    conn.close()
    predictions = [{"probability": r[0], "risk_level": r[1], "prediction": r[2], "date": r[3]} for r in rows]
    return jsonify({"predictions": predictions})


@app.route("/api/patient/care-plan", methods=["GET"])
@login_required
def patient_care_plan():
    conn = sqlite3.connect("dementia_system.db")
    c = conn.cursor()
    c.execute(
        "SELECT medicine_name, dosage, frequency, status FROM medications WHERE patient_id = ? ORDER BY created_at DESC LIMIT 10",
        (session["user_id"],),
    )
    medications = [{"medicine_name": r[0], "dosage": r[1], "frequency": r[2], "status": r[3]} for r in c.fetchall()]
    c.execute("SELECT task_title, due_date, completed FROM care_tasks WHERE patient_id = ? ORDER BY created_at DESC LIMIT 10", (session["user_id"],))
    tasks = [{"task_title": r[0], "due_date": r[1], "completed": bool(r[2])} for r in c.fetchall()]
    conn.close()
    return jsonify({"medications": medications, "tasks": tasks})


@app.route("/api/doctor/dashboard")
@role_required("doctor")
def doctor_api_dashboard():
    conn = sqlite3.connect("dementia_system.db")
    c = conn.cursor()
    c.execute("SELECT id, full_name, email FROM users WHERE role = 'patient'")
    patients = c.fetchall()

    out = []
    total_risk = 0.0
    high = 0
    assessments = 0
    for pid, full_name, email in patients:
        c.execute("SELECT probability, risk_level, created_at FROM predictions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (pid,))
        latest = c.fetchone()
        c.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (pid,))
        pcount = c.fetchone()[0]
        assessments += pcount
        risk_level, prob, when = "No data", 0.0, None
        if latest:
            prob, risk_level, when = latest[0], latest[1], latest[2]
            total_risk += prob
            if prob >= 60:
                high += 1
        out.append({"id": pid, "full_name": full_name, "email": email, "risk_level": risk_level, "last_assessment": when})

    conn.close()
    avg = round((total_risk / len(out)) if out else 0.0, 1)
    return jsonify({"total_patients": len(out), "high_risk_patients": high, "avg_risk_score": avg, "total_assessments": assessments, "patients": out})


@app.route("/api/doctor/patient/<int:patient_id>", methods=["GET"])
@role_required("doctor")
def doctor_patient_details(patient_id: int):
    conn = sqlite3.connect("dementia_system.db")
    c = conn.cursor()
    c.execute("SELECT full_name, email FROM users WHERE id = ? AND role = 'patient'", (patient_id,))
    user = c.fetchone()
    c.execute(
        "SELECT age, gender, education_years FROM patient_profiles WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (patient_id,),
    )
    profile = c.fetchone()
    c.execute(
        "SELECT probability, risk_level, prediction, recommendations, created_at FROM predictions WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (patient_id,),
    )
    history_rows = c.fetchall()
    c.execute(
        "SELECT medicine_name, dosage, frequency, status, start_date, end_date FROM medications WHERE patient_id = ? ORDER BY created_at DESC LIMIT 10",
        (patient_id,),
    )
    medication_rows = c.fetchall()
    c.execute("SELECT task_title, due_date, completed FROM care_tasks WHERE patient_id = ? ORDER BY created_at DESC LIMIT 10", (patient_id,))
    task_rows = c.fetchall()
    conn.close()

    history = [{"probability": r[0], "risk_level": r[1], "prediction": r[2], "date": r[4]} for r in history_rows]
    medications = [{"medicine_name": r[0], "dosage": r[1], "frequency": r[2], "status": r[3], "start_date": r[4], "end_date": r[5]} for r in medication_rows]
    tasks = [{"task_title": r[0], "due_date": r[1], "completed": bool(r[2])} for r in task_rows]
    latest_recommendations = []
    if history_rows and history_rows[0][3]:
        try:
            latest_recommendations = json.loads(history_rows[0][3])[:5]
        except Exception:
            latest_recommendations = []

    return jsonify(
        {
            "full_name": user[0] if user else "Unknown",
            "email": user[1] if user else "Unknown",
            "age": profile[0] if profile else None,
            "gender": profile[1] if profile else None,
            "education": profile[2] if profile else None,
            "history": history,
            "medications": medications,
            "tasks": tasks,
            "latest_recommendations": latest_recommendations,
        }
    )


@app.route("/api/doctor/patient/<int:patient_id>/note", methods=["POST"])
@role_required("doctor")
def doctor_add_note(patient_id: int):
    data = request.get_json(force=True)
    note = data.get("note", "").strip()
    if not note:
        return jsonify({"success": False, "error": "Note is required"}), 400
    conn = sqlite3.connect("dementia_system.db")
    c = conn.cursor()
    c.execute("INSERT INTO doctor_notes (patient_id, doctor_id, note) VALUES (?, ?, ?)", (patient_id, session["user_id"], note))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/doctor/patient/<int:patient_id>/medication", methods=["POST"])
@role_required("doctor")
def doctor_add_medication(patient_id: int):
    data = request.get_json(force=True)
    required = ["medicine_name", "dosage", "frequency"]
    if any(not data.get(k) for k in required):
        return jsonify({"success": False, "error": "medicine_name, dosage and frequency are required"}), 400
    conn = sqlite3.connect("dementia_system.db")
    c = conn.cursor()
    c.execute(
        """INSERT INTO medications (patient_id, doctor_id, medicine_name, dosage, frequency, start_date, end_date, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            patient_id,
            session["user_id"],
            data["medicine_name"].strip(),
            data["dosage"].strip(),
            data["frequency"].strip(),
            data.get("start_date"),
            data.get("end_date"),
            data.get("status", "active"),
        ),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/doctor/patient/<int:patient_id>/task", methods=["POST"])
@role_required("doctor")
def doctor_add_task(patient_id: int):
    data = request.get_json(force=True)
    title = data.get("task_title", "").strip()
    if not title:
        return jsonify({"success": False, "error": "task_title is required"}), 400
    conn = sqlite3.connect("dementia_system.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO care_tasks (patient_id, doctor_id, task_title, due_date, completed) VALUES (?, ?, ?, ?, ?)",
        (patient_id, session["user_id"], title, data.get("due_date"), int(bool(data.get("completed", False)))),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


def bootstrap_demo_data() -> None:
    conn = sqlite3.connect("dementia_system.db")
    c = conn.cursor()
    demo = [
        ("doctor@demo.com", "doctor123", "Demo Doctor", "doctor"),
        ("patient@demo.com", "patient123", "Demo Patient", "patient"),
    ]
    for email, pwd, name, role in demo:
        c.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        if not c.fetchone():
            c.execute("INSERT INTO users (email, password, full_name, role) VALUES (?, ?, ?, ?)", (email, generate_password_hash(pwd), name, role))
    conn.commit()
    conn.close()


def train_or_load() -> None:
    if os.path.exists("models/scaler.pkl") and os.path.exists("models/random_forest.pkl"):
        ai_model.load_models()
        return
    generator = DementiaDatasetGenerator(n_samples=8000)
    df = generator.generate_comprehensive_dataset()
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/dementia_complete_dataset.csv", index=False)
    ai_model.train(df)
    ai_model.save_models()


if __name__ == "__main__":
    init_database()
    train_or_load()
    bootstrap_demo_data()
    app.run(host="0.0.0.0", port=5000, debug=True)
