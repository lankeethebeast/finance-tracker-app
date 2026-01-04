# Personal Finance Tracker

A comprehensive web application for tracking personal expenses and income with machine learning-powered predictive analytics. Built with Flask (backend) and React (frontend), featuring secure authentication, interactive data visualizations, and intelligent expense forecasting.

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure JWT-based login/registration with role-based access control
- **Expense Tracking**: Add, edit, delete, and categorize income/expense transactions
- **Data Visualization**: Interactive charts showing spending trends and category breakdowns
- **Financial Analytics**: Comprehensive summaries and spending pattern analysis
- **ML Predictions**: AI-powered expense forecasting using scikit-learn models

### Security & Performance
- **Rate Limiting**: Prevents brute force attacks and API abuse
- **Input Validation**: Comprehensive data sanitization and validation
- **Security Headers**: Flask-Talisman for XSS and security protection
- **Environment Configuration**: Secure configuration management
- **Comprehensive Testing**: 29 test cases covering all functionality

### Machine Learning
- **Dual Model Architecture**: Linear Regression + Random Forest for optimal predictions
- **Cross-Validation**: Rigorous model validation with 80% accuracy threshold
- **Category-Specific Predictions**: Individual forecasts for spending categories
- **Real-time Accuracy Metrics**: R², MAE, and RMSE performance indicators

## 🛠 Technology Stack

### Backend
- **Flask**: Lightweight Python web framework
- **SQLAlchemy**: Database ORM with SQLite
- **Flask-JWT-Extended**: JWT authentication
- **Flask-Limiter**: Rate limiting
- **Flask-Talisman**: Security headers
- **scikit-learn**: Machine learning models
- **pandas**: Data manipulation and analysis

### Frontend
- **React**: Modern JavaScript UI framework
- **Chart.js**: Interactive data visualizations
- **Axios**: HTTP client for API calls
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing

### Development & Testing
- **pytest**: Comprehensive test suite
- **Flask-CORS**: Cross-origin resource sharing
- **python-dotenv**: Environment variable management

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **npm or yarn**
- **Git**

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd enifeshts
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your secret keys (see Environment Configuration below)
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
```

### 4. Database Initialization
```bash
cd backend
python app.py  # This creates the database automatically
```

## ⚙️ Environment Configuration

Create a `.env` file in the `backend/` directory:

```env
# Required: Generate strong random keys for production
SECRET_KEY=your-super-secret-key-here-minimum-32-characters
JWT_SECRET_KEY=your-jwt-secret-key-here-minimum-32-characters

# Optional: Customize as needed
DATABASE_URL=sqlite:///finance_tracker.db
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
LOG_LEVEL=INFO
JWT_ACCESS_TOKEN_EXPIRES=3600
```

## 🎯 Usage

### Starting the Application

#### Backend (Terminal 1)
```bash
cd backend
python app.py
```
**Runs on:** `http://localhost:5000`

#### Frontend (Terminal 2)
```bash
cd frontend
npm start
```
**Runs on:** `http://localhost:3000`

### Using the Application

1. **Register**: Create a new account with a strong password
2. **Login**: Access your personalized dashboard
3. **Add Transactions**: Use the expense form to add income/expenses
4. **View Analytics**: Explore charts and spending patterns
5. **Predictions**: View ML-powered expense forecasts (requires 10+ transactions)

### User Roles

- **User**: Standard access to personal finance tracking
- **Admin**: Can manage users and access administrative features

## 🤖 Machine Learning Predictions

The application uses sophisticated ML algorithms to forecast future expenses:

### How It Works

1. **Data Collection**: Minimum 10 transactions required for reliable predictions
2. **Model Training**: System trains both Linear Regression and Random Forest models
3. **Validation**: Cross-validation ensures model reliability (80%+ accuracy required)
4. **Prediction Generation**: Forecasts expenses for specified time periods
5. **Category Analysis**: Individual predictions for spending categories

### Prediction Features

- **Accuracy Metrics**: R² score, Mean Absolute Error, Root Mean Square Error
- **Model Selection**: Automatic selection of best-performing algorithm
- **Time-based Forecasting**: Predicts expenses over custom time periods
- **Category Breakdowns**: Separate forecasts for different spending categories

### Example Prediction Output
```json
{
  "model_accuracy": 0.85,
  "meets_accuracy_threshold": true,
  "best_model": "random_forest",
  "predictions": [
    {"date": "2025-01-16", "predicted_amount": 132.74}
  ],
  "total_predicted": 1044.75
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd backend
python -m pytest tests/ -v --tb=short
```

### Test Coverage
- **Authentication**: User registration, login, JWT validation
- **Expense Management**: CRUD operations, validation, filtering
- **Analytics**: Trend analysis, category breakdowns
- **ML Predictions**: Model training, accuracy validation
- **Integration**: End-to-end user workflows
- **Security**: Rate limiting, input validation, error handling

**Current Status:** 29/29 tests passing ✅

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication with secure token handling
- Password strength requirements (8+ chars, uppercase, lowercase, numbers)
- Role-based access control (User/Admin)
- Secure password hashing with bcrypt

### API Security
- Rate limiting (200/day, 50/hour global; stricter for auth endpoints)
- Input validation and sanitization
- CORS protection with configurable origins
- Security headers (CSP, HSTS, secure cookies)

### Data Protection
- SQL injection prevention via SQLAlchemy ORM
- XSS protection through input validation
- Secure environment variable management
- Comprehensive error handling without information leakage

## 📡 API Documentation

### Authentication Endpoints

#### POST `/api/auth/register`
Register a new user account.
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "role": "user"
}
```

#### POST `/api/auth/login`
Authenticate user and receive JWT token.
```json
{
  "username": "johndoe",
  "password": "SecurePass123"
}
```

### Expense Endpoints

#### GET `/api/expenses/`
Retrieve user's transactions with optional filtering.
**Query Parameters:** `category`, `type`, `start_date`, `end_date`

#### POST `/api/expenses/`
Create new expense/income transaction.
```json
{
  "amount": 50.00,
  "category": "Food",
  "transaction_type": "expense",
  "date": "2025-01-15",
  "description": "Lunch at restaurant"
}
```

#### GET `/api/expenses/summary`
Get financial summary and category breakdowns.

### Analytics Endpoints

#### GET `/api/analytics/predict`
Generate ML-powered expense predictions.
**Query Parameters:** `days` (default: 30)

#### GET `/api/analytics/trends`
Get spending trends over time.
**Query Parameters:** `period` (daily/monthly/weekly)

#### GET `/api/analytics/category-analysis`
Detailed spending analysis by category.

## 🏗 Project Structure

```
enifeshts/
├── backend/
│   ├── app.py                 # Flask application
│   ├── extensions.py          # Database and extensions
│   ├── models/
│   │   ├── user.py           # User model
│   │   └── expense.py        # Expense model
│   ├── routes/
│   │   ├── auth_routes.py    # Authentication endpoints
│   │   ├── expense_routes.py # Expense management
│   │   └── analytics_routes.py # Analytics & predictions
│   ├── services/
│   │   └── prediction_service.py # ML prediction logic
│   ├── tests/                # Comprehensive test suite
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example         # Environment template
│   └── instance/
│       └── finance_tracker.db # SQLite database
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   ├── context/         # React context
│   │   └── services/        # API services
│   ├── package.json         # Node dependencies
│   └── public/              # Static assets
└── README.md               # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Flask** for the robust backend framework
- **React** for the modern frontend experience
- **scikit-learn** for machine learning capabilities
- **Chart.js** for beautiful data visualizations
- **Tailwind CSS** for utility-first styling

## 📞 Support

For questions or issues:
1. Check the test suite: `python -m pytest tests/ -v`
2. Review the API documentation above
3. Check environment configuration
4. Open an issue with detailed information

---

**Built with ❤️ for personal finance management and machine learning education**
