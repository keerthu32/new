# Cattle Marketplace App (Single Folder)

## Features
- Role-based users: `admin`, `seller`, `buyer`
- Login / Register (JWT)
- Seller cattle image upload + ML breed prediction
- Buyer dummy purchase flow
- Notification to seller after purchase

## Folder Layout
- `backend/` FastAPI API
- `frontend/` React app
- `ml_model/` place your `cattle_model.h5`

## Use your provided model path
`backend/ml.py` defaults to:
`C:\Users\kumareshwary23\Desktop\cattle_marketplace_app\backend\models\cattle_model.h5`

You can override via env var:

```bash
export CATTLE_MODEL_PATH="/absolute/path/to/cattle_model.h5"
```

## Run Backend
```bash
cd cattle_app/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Run Frontend
```bash
cd cattle_app/frontend
npm install
npm run dev
```
