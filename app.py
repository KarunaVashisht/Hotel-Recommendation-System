from flask import Flask, render_template, request
import pandas as pd
from sklearn.model_selection import train_test_split

app = Flask(__name__)

# Load the dataset and prepare it
df_hd = pd.read_csv("hotels.csv")
hotel_details = df_hd.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]

# Assume hotel_details is already prepared
X = hotel_details[['hotel_id', 'state', 'city', 'ratings', 'alcohol_availability', 'hotel_name', 'total_rooms', 'category', 'pricing', 'meals']]
y = hotel_details['hotel_name']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.26, random_state=42)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend_hotels', methods=['POST'])
def recommend_hotels():
    # Prompt user for input
    user_input = {
        'state': request.form['state'].lower(),
        'city': request.form['city'].lower(),
        'ratings': float(request.form['ratings']),
        'min_pricing': float(request.form['min_pricing']),
        'max_pricing': float(request.form['max_pricing'])
    }

    meals_option = request.form['meals_option']

    # Convert state and city to lowercase for case-insensitive comparison
    X_test['state'] = X_test['state'].str.lower()
    X_test['city'] = X_test['city'].str.lower()

    # Apply filtering conditions
    state_filter = X_test['state'] == user_input['state']
    city_filter = X_test['city'] == user_input['city']
    ratings_filter = X_test['ratings'] >= user_input['ratings']
    pricing_filter = (X_test['pricing'] >= user_input['min_pricing']) & (X_test['pricing'] <= user_input['max_pricing'])

    # Filtering by Meals Option
    if meals_option == '1':
        meals_filter = True  # No filtering based on meals
    elif meals_option == '2':
        meals_filter = X_test['meals'].str.contains('breakfast', case=False)
    elif meals_option == '3':
        meals_filter = X_test['meals'].str.contains('lunch', case=False)
    elif meals_option == '4':
        meals_filter = X_test['meals'].str.contains('dinner', case=False)
    else:
        print("Invalid option selected. Defaulting to 'All meals'.")
        meals_filter = True

    # Apply all filtering conditions
    filtered_data = X_test[state_filter & city_filter & ratings_filter & pricing_filter & meals_filter]

    if not filtered_data.empty:
        recommended_hotels = filtered_data['hotel_id'].tolist()  # Get recommended hotel IDs
        recommended_hotels_names = [y_test.loc[X_test[X_test['hotel_id'] == hotel_id].index[0]] for hotel_id in recommended_hotels]  # Get hotel names
        return render_template('result.html', recommended_hotels=recommended_hotels_names)
    else:
        return "No hotels match the specified criteria."

if __name__ == '__main__':
    app.run(debug=True)
