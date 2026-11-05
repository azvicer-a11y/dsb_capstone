## Valora AI – Project Update (November 5, 2026)

### Project Progress

I continued working on my Valora AI project, an AI tool for estimating real estate prices in Montenegro.

The dataset currently contains 3,986 rows and 19 columns, including 1,986 real property listings and 2,000 simulated records.

### What I Worked On

**1. Exploratory Data Analysis (EDA)**
- Analyzed property prices, sizes, and locations.
- Created graphs to better understand the dataset.
- Checked missing values and data types.
- Explored relationships between property features and prices.

**2. Data Preprocessing**
- Checked the dataset structure using `df.shape` and `df.info()`.
- Identified missing values using `df.isnull().sum()`.
- Checked and prepared the data for machine learning.
- Reviewed the dataset to identify possible data quality issues.

**3. Machine Learning – Next Steps**
- Prepare features for the prediction model.
- Use Linear Regression as a first model.
- Split the dataset into training and testing sets.
- Evaluate model performance using MAE, RMSE, and R².
- Compare predictions with actual listing prices.

### Future Plans

My main goal is to predict the estimated market price of individual properties in Montenegro.

I also want to explore predicting general real estate price trends for the next six months. ARIMA could be used later if enough historical price data is available.

### Current Status

EDA completed. Data preprocessing in progress. Machine learning modeling is the next step.


