import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, 
                           classification_report,
                           confusion_matrix)
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy as np

# Load and prepare data
def load_data():
    """Load dataset with validation"""
    df = pd.read_csv("speech_dataset.csv")
    
    # Check for missing values
    if df.isnull().values.any():
        print("Warning: Dataset contains missing values - dropping rows")
        df = df.dropna()
    
    # Validate label distribution
    print("\nLabel distribution:")
    print(df['label'].value_counts())
    
    return df

# Main training function
def train_and_evaluate():
    df = load_data()
    
    # Separate features and labels
    X = df.drop('label', axis=1)
    y = df['label']
    
    # Encode labels if they're strings
    if isinstance(y.iloc[0], str):
        le = LabelEncoder()
        y = le.fit_transform(y)
        print("\nEncoded labels:")
        print(f"0: {le.classes_[0]}")
        print(f"1: {le.classes_[1]}")
    
    # Train-test split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=42,
        stratify=y
    )
    
    # Initialize model with improved parameters
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight='balanced',
        max_depth=10,
        min_samples_split=5,
        n_jobs=-1
    )
    
    # Cross-validation
    print("\nCross-validation results:")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    print(f"Mean CV accuracy: {cv_scores.mean():.2f} (±{cv_scores.std():.2f})")
    
    # Train final model
    model.fit(X_train, y_train)
    
    # Evaluation
    y_pred = model.predict(X_test)
    print("\nTest set performance:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Feature importance
    print("\nTop 10 Important Features:")
    feature_imp = pd.Series(model.feature_importances_, index=X.columns)
    print(feature_imp.sort_values(ascending=False).head(10))
    
    return model, X_test  # Return both model and X_test

if __name__ == "__main__":
    print("=== Speech Disorder Model Training ===")
    model, X_test = train_and_evaluate()  # Now receiving both returns
    
    # Save model and metadata
    joblib.dump(model, 'speech_disorder_model.pkl')
    print("\nModel saved as speech_disorder_model.pkl")
    
    # Sample prediction test
    sample = X_test.iloc[0:1]
    pred = model.predict(sample)
    proba = model.predict_proba(sample)
    print(f"\nSample prediction test:")
    print(f"Features: {sample.values.tolist()[0]}")
    print(f"Prediction: {pred[0]} (Probability: {np.max(proba):.2f})")