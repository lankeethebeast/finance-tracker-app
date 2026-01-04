# Quick Start Guide

## Prerequisites
- Python 3.8+ installed
- Node.js 14+ and npm installed

## Backend Setup (First Terminal)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Backend will run on: **http://localhost:5000**

## Frontend Setup (Second Terminal)

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm start
```

Frontend will run on: **http://localhost:3000**

## First Time Usage

1. Navigate to http://localhost:3000
2. Click "Register" to create a new account
3. Fill in username, email, and password
4. After registration, you'll be redirected to login
5. Login with your credentials
6. Start adding transactions!

## Tips

- Add at least **10 transactions** to see AI predictions
- Use different categories to see category breakdowns in charts
- Mix income and expenses to see your balance
- The prediction model improves with more data

## Troubleshooting

### Backend Issues

**"No module named 'flask_cors'"**
- Make sure you activated the virtual environment: `venv\Scripts\activate`
- Then run: `pip install -r requirements.txt`

**"Port 5000 already in use"**
- Stop any other Flask apps or change the port in `app.py`

### Frontend Issues

**"Cannot connect to backend"**
- Ensure backend is running on port 5000
- Check that CORS is enabled in Flask

**Compilation errors**
- Run `npm install` again
- Clear cache: `npm cache clean --force` then `npm install`

## Testing the API

You can test the API endpoints using curl or Postman:

### Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"password123\"}"
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"password\":\"password123\"}"
```

Copy the `access_token` from the response and use it in subsequent requests:

### Add Expense
```bash
curl -X POST http://localhost:5000/api/expenses/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d "{\"amount\":50.00,\"category\":\"Food & Dining\",\"description\":\"Lunch\",\"transaction_type\":\"expense\"}"
```

## Project Structure Overview

```
backend/
├── app.py              # Main Flask application
├── extensions.py       # Flask extensions (db, bcrypt, jwt)
├── models/            # Database models
├── routes/            # API endpoints
├── services/          # Business logic (predictions)
└── tests/             # Unit tests

frontend/
├── src/
│   ├── components/    # Reusable React components
│   ├── pages/         # Page components (Login, Dashboard)
│   ├── context/       # React Context (Auth)
│   └── services/      # API integration
```

## Next Steps

1. Add more sample transactions
2. Explore the charts and analytics
3. Test the prediction feature
4. Run the unit tests: `pytest tests/`
5. Customize categories in `ExpenseForm.js`
6. Add new features!

Happy tracking! 💰
