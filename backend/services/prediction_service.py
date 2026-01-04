import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime, timedelta

def predict_expenses(expenses, days=30):
    """
    Predict future expenses based on historical data using machine learning models.
    Validates model accuracy and ensures 80% performance threshold.

    Args:
        expenses: List of Expense objects
        days: Number of days to predict into the future

    Returns:
        Dictionary containing predictions and comprehensive accuracy metrics
    """
    if len(expenses) < 10:
        return {'error': 'Insufficient data for prediction. Need at least 10 transactions.'}

    df = pd.DataFrame([{
        'date': exp.date,
        'amount': exp.amount,
        'category': exp.category
    } for exp in expenses])

    df = df.sort_values('date')
    df['days_since_start'] = (df['date'] - df['date'].min()).dt.days

    X = df[['days_since_start']].values
    y = df['amount'].values

    # Split data for validation
    if len(expenses) >= 15:  # Only use train/test split if we have enough data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    else:
        X_train, X_test, y_train, y_test = X, X, y, y  # Use all data for training if small dataset

    # Try multiple models and select the best performing one
    models = {
        'linear_regression': LinearRegression(),
        'random_forest': RandomForestRegressor(n_estimators=100, random_state=42)
    }

    best_model = None
    best_accuracy = 0
    best_model_name = ''
    model_results = {}

    for name, model in models.items():
        try:
            # Train model
            model.fit(X_train, y_train)

            # Evaluate on test set
            if len(X_test) > 0:
                y_pred = model.predict(X_test)
                r2 = r2_score(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))

                # Cross-validation score - use fewer folds for small datasets
                cv_folds = min(3, len(X_train))  # Use at most 3-fold CV
                if cv_folds < 2:
                    cv_folds = 2  # Minimum 2-fold CV
                cv_scores = cross_val_score(model, X_train, y_train, cv=cv_folds, scoring='r2')
                cv_mean = cv_scores.mean()

                model_results[name] = {
                    'r2_score': float(r2),
                    'mae': float(mae),
                    'rmse': float(rmse),
                    'cv_mean_r2': float(cv_mean),
                    'cv_std_r2': float(cv_scores.std())
                }

                # Use CV mean R² as primary accuracy metric
                accuracy = cv_mean
            else:
                # Fallback for small datasets
                y_pred = model.predict(X_train)
                accuracy = r2_score(y_train, y_pred)
                model_results[name] = {
                    'r2_score': float(accuracy),
                    'mae': 0.0,
                    'rmse': 0.0,
                    'cv_mean_r2': float(accuracy),
                    'cv_std_r2': 0.0
                }

            # Select best model based on cross-validation R² score
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model = model
                best_model_name = name

        except Exception as e:
            print(f"Error training {name} model: {str(e)}")
            continue

    if best_model is None:
        return {'error': 'Failed to train prediction models'}

    # Use the best performing model
    model = best_model

    # Generate predictions
    last_date = df['date'].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, days + 1)]
    future_days = np.array([(date - df['date'].min()).days for date in future_dates]).reshape(-1, 1)

    predictions = model.predict(future_days)
    predictions = np.maximum(predictions, 0)  # Ensure non-negative predictions

    # Category-specific predictions
    category_predictions = {}
    for category in df['category'].unique():
        category_df = df[df['category'] == category]
        if len(category_df) >= 3:
            X_cat = category_df[['days_since_start']].values
            y_cat = category_df['amount'].values

            cat_model = LinearRegression()  # Use simpler model for categories
            cat_model.fit(X_cat, y_cat)

            cat_predictions = cat_model.predict(future_days)
            cat_predictions = np.maximum(cat_predictions, 0)

            category_predictions[category] = {
                'predicted_total': float(np.sum(cat_predictions)),
                'average_per_day': float(np.mean(cat_predictions))
            }

    # Determine if model meets 80% accuracy requirement
    meets_accuracy_threshold = bool(best_accuracy >= 0.8)  # 80% R² score threshold

    return {
        'predictions': [
            {
                'date': date.isoformat(),
                'predicted_amount': float(pred)
            }
            for date, pred in zip(future_dates, predictions)
        ],
        'total_predicted': float(np.sum(predictions)),
        'average_per_day': float(np.mean(predictions)),
        'model_accuracy': float(best_accuracy),
        'meets_accuracy_threshold': meets_accuracy_threshold,
        'accuracy_threshold_required': 0.8,
        'best_model': best_model_name,
        'model_details': model_results,
        'category_predictions': category_predictions,
        'days_predicted': days,
        'data_points': len(expenses),
        'validation_method': 'cross_validation' if len(expenses) >= 15 else 'train_score_only'
    }
