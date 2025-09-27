import pandas as pd
import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from ai_model import RouteScorer
import joblib

def prepare_data():
    """Load and prepare the vehicle emission dataset"""
    print("Loading vehicle emission dataset...")
    
    # Load the dataset
    df = pd.read_csv('../../vehicle_emission_dataset.csv')
    print(f"Loaded {len(df)} records")
    
    # Create mappings for categorical variables
    vehicle_map = {'Car': 0, 'Truck': 1, 'Bus': 2, 'Motorcycle': 3}
    fuel_map = {'Electric': 0, 'Hybrid': 1, 'Petrol': 2, 'Diesel': 3}
    road_map = {'City': 0, 'Highway': 1, 'Rural': 2}
    traffic_map = {'Free flow': 0, 'Moderate': 1, 'Heavy': 2}
    
    # Map categorical variables to numeric
    df['Vehicle_Encoded'] = df['Vehicle Type'].map(vehicle_map)
    df['Fuel_Encoded'] = df['Fuel Type'].map(fuel_map)
    df['Road_Encoded'] = df['Road Type'].map(road_map)
    df['Traffic_Encoded'] = df['Traffic Conditions'].map(traffic_map)
    
    # Add more features for better accuracy
    df['Speed_Squared'] = df['Speed'] ** 2  # Speed efficiency curve
    df['Engine_Vehicle'] = df['Engine Size'] * df['Vehicle_Encoded']  # Interaction
    df['Speed_Traffic'] = df['Speed'] * df['Traffic_Encoded']  # Speed-traffic interaction
    
    # Select enhanced features
    features = [
        'Speed',           # Average speed (km/h)
        'Engine Size',     # Engine size (L)
        'Traffic_Encoded', # Traffic conditions (0-2)
        'Vehicle_Encoded', # Vehicle type (0-3)
        'Fuel_Encoded',    # Fuel type (0-3)
        'Speed_Squared',   # Speed efficiency curve
        'Engine_Vehicle',  # Engine-vehicle interaction
        'Speed_Traffic'    # Speed-traffic interaction
    ]
    
    X = df[features].values
    y = df['CO2 Emissions'].values
    
    # Handle missing values
    X = np.nan_to_num(X)
    y = np.nan_to_num(y)
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    return X, y

def train_model():
    """Train the neural network on emission data"""
    print("=== Training AI Model on Real Emission Data ===")
    
    # Prepare data
    X, y = prepare_data()
    
    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features for better training
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Convert to PyTorch tensors
    X_train_tensor = torch.FloatTensor(X_train_scaled)
    y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1)
    X_test_tensor = torch.FloatTensor(X_test_scaled)
    y_test_tensor = torch.FloatTensor(y_test).unsqueeze(1)
    
    # Initialize model with correct input size
    model = RouteScorer(input_size=X.shape[1])
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)  # L2 regularization
    
    print("Training neural network...")
    
    # Training loop with early stopping
    epochs = 2000
    best_test_loss = float('inf')
    patience = 100
    patience_counter = 0
    
    for epoch in range(epochs):
        # Training
        model.train()
        optimizer.zero_grad()
        
        outputs = model(X_train_tensor)
        loss = criterion(outputs, y_train_tensor)
        loss.backward()
        optimizer.step()
        
        # Validation every 100 epochs
        if (epoch + 1) % 100 == 0:
            model.eval()
            with torch.no_grad():
                test_outputs = model(X_test_tensor)
                test_loss = criterion(test_outputs, y_test_tensor)
                
                if test_loss < best_test_loss:
                    best_test_loss = test_loss
                    patience_counter = 0
                    # Save best model
                    torch.save(model.state_dict(), 'best_route_scorer.pt')
                else:
                    patience_counter += 1
                
                print(f'Epoch [{epoch+1}/{epochs}] - Train Loss: {loss.item():.4f}, Test Loss: {test_loss.item():.4f}')
                
                # Early stopping
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch+1}")
                    break
    
    # Load best model and save
    try:
        model.load_state_dict(torch.load('best_route_scorer.pt', weights_only=True))
    except:
        pass  # Use current model if best not saved
    
    torch.save(model.state_dict(), 'route_scorer.pt')
    joblib.dump(scaler, 'feature_scaler.pkl')
    
    print(f"✅ Model training completed!")
    print(f"✅ Best test loss: {best_test_loss:.4f}")
    print(f"✅ Model saved as 'route_scorer.pt'")
    print(f"✅ Scaler saved as 'feature_scaler.pkl'")
    
    # Calculate accuracy metrics
    calculate_accuracy_metrics(model, scaler, X_test, y_test)
    
    # Test with sample predictions
    test_predictions(model, scaler)

def calculate_accuracy_metrics(model, scaler, X_test, y_test):
    """Calculate proper accuracy metrics"""
    model.eval()
    with torch.no_grad():
        X_test_scaled = scaler.transform(X_test)
        X_test_tensor = torch.FloatTensor(X_test_scaled)
        predictions = model(X_test_tensor).numpy().flatten()
        
        # Calculate metrics
        mse = np.mean((predictions - y_test) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - y_test))
        
        # Calculate percentage accuracy (within ±20% of actual)
        percentage_errors = np.abs((predictions - y_test) / y_test) * 100
        accuracy_20pct = np.mean(percentage_errors <= 20) * 100
        accuracy_30pct = np.mean(percentage_errors <= 30) * 100
        
        print(f"\n=== Model Accuracy Metrics ===")
        print(f"RMSE: {rmse:.2f} grams CO2")
        print(f"MAE: {mae:.2f} grams CO2")
        print(f"Accuracy (±20%): {accuracy_20pct:.1f}%")
        print(f"Accuracy (±30%): {accuracy_30pct:.1f}%")
        print(f"Average CO2 in dataset: {np.mean(y_test):.2f} grams")
        
        return rmse, mae, accuracy_20pct

def test_predictions(model, scaler):
    """Test the model with sample vehicle scenarios"""
    print("\n=== Testing Model Predictions ===")
    
    model.eval()
    
    test_cases = [
        # [Speed, Engine_Size, Traffic(0-2), Vehicle(0-3), Fuel(0-3), Speed^2, Engine*Vehicle, Speed*Traffic]
        [60.0, 2.0, 0, 0, 0, 3600.0, 0.0, 0.0],    # Car, Electric, Free flow, 60km/h
        [30.0, 2.0, 2, 0, 2, 900.0, 0.0, 60.0],    # Car, Petrol, Heavy traffic, 30km/h
        [80.0, 4.0, 1, 1, 3, 6400.0, 4.0, 80.0],   # Truck, Diesel, Moderate traffic, 80km/h
        [25.0, 6.0, 2, 2, 0, 625.0, 12.0, 50.0],   # Bus, Electric, Heavy traffic, 25km/h
    ]
    
    labels = [
        "Electric Car (Free Flow)",
        "Petrol Car (Heavy Traffic)",
        "Diesel Truck (Moderate Traffic)",
        "Electric Bus (Heavy Traffic)"
    ]
    
    expected_ranges = [
        "50-150g",   # Electric car should be low
        "200-400g",  # Petrol car in traffic
        "400-600g",  # Diesel truck
        "100-300g"   # Electric bus
    ]
    
    with torch.no_grad():
        for i, (case, label, expected) in enumerate(zip(test_cases, labels, expected_ranges)):
            # Scale input
            case_scaled = scaler.transform([case])
            case_tensor = torch.FloatTensor(case_scaled)
            
            # Predict (model outputs grams)
            prediction = model(case_tensor).item()
            
            print(f"{label}: {prediction:.0f}g CO2 (expected: {expected})")

if __name__ == "__main__":
    train_model()