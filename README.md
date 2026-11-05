Valora AI – Real Estate Price Estimation in Montenegro 

Valora AI is a data science project that explores property listings in Montenegro and uses machine learning to estimate asking prices in euros.
Project Goal
The goal is to understand how property size, number of bedrooms, location, and property type relate to listing prices, and to build a first price prediction model.
Dataset
- 3,986 records and 19 columns in the original dataset
- 1,986 real listings and 2,000 simulated records
- The EDA focuses on real apartment listings only. Simulated records are excluded from that analysis.
- After filtering and cleaning, 1,432 real apartment listings remain (from 1,473 before cleaning).
- Prices are asking prices, not confirmed sale prices.
Tools and Libraries
- Python and Google Colab
- Pandas and NumPy
- Matplotlib and Seaborn
- Scikit-learn
1. Data Exploration
I loaded the CSV dataset and checked its structure, column types, missing values, summary statistics, and duplicate rows using df.shape, df.head(), df.info(), df.isnull().sum(), df.describe(), and df.duplicated().sum().
2. Data Cleaning
I selected real apartment listings, standardized property-type labels, removed duplicate listing IDs within sources, and filtered unusual price and size values. I also checked city names because some are missing or inconsistent.
3. Exploratory Data Analysis (EDA)
I created charts to explore:
- Asking price and apartment size distributions
- Apartment size versus asking price
- Price per square meter and possible outliers
- Differences in median price per square meter between cities
- Correlations between numerical features
Most apartments in the cleaned sample are around 40–80 m². Larger apartments generally have higher asking prices, but there are outliers.
4. Data Preprocessing for Machine Learning
For the first model, I selected area_m2, bedrooms, bathrooms, city, and property_type as input features, with price_eur as the target.
- Removed bathrooms because 3,600 values were missing.
- Split the full dataset into 80% training (3,188 rows) and 20% testing (798 rows).
- Checked that the target prices had no missing values.
- Filled missing bedroom values with the training-set median.
- Filled missing city and property-type values with the most frequent training-set values.
- Used one-hot encoding for city and property_type, fitted on the training data.
- Combined 2 numerical features with 189 encoded categorical features.
The final feature matrices have 191 columns for both training and testing.
5. First Machine Learning Model
I used Linear Regression from Scikit-learn and fitted the model on the prepared training data.
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train_final, y_train)
The notebook includes model training, but it does not yet include predictions or evaluation metrics.

Important: The current first-model training split uses the full dataset, including simulated records. This is different from the real-apartment-only EDA. A future version should train and evaluate on real listings if the goal is to estimate actual market asking prices.
6. Next Steps
- Make predictions on the test set.
- Evaluate the model using MAE, RMSE, and R².
- Improve city names and check unusual values.
- Compare models and improve prediction quality.
- Explore general price trends over the next six months if suitable historical data becomes available. The current notebook does not forecast future prices.
Current Status
EDA and preprocessing completed in the notebook. The first Linear Regression model has been fitted. Model evaluation is the next step.

Last updated: November 5, 2026.


