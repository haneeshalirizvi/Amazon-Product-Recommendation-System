# Amazon-Product-Recommendation-System
This project is a scalable real-time recommendation system built using Apache Spark (PySpark) and Alternating Least Squares (ALS). It integrates Kafka for streaming, MongoDB for storage, and a Flask web app for serving recommendations.
.

📌 Overview

The system recommends products based on user interaction data (Amazon reviews). It uses collaborative filtering to predict user preferences and generate personalized recommendations in real time.

🛠️ Tech Stack
Apache Spark (PySpark) – Distributed data processing & model training
ALS (Alternating Least Squares) – Recommendation algorithm
Apache Kafka – Real-time data streaming
MongoDB – Data storage
Flask – Web application backend
HTML/CSS – Frontend interface
⚙️ Features
📊 Collaborative Filtering Model using ALS
⚡ Real-time recommendation pipeline with Kafka
🧠 Model training & evaluation (RMSE, Accuracy, F1-score)
🔄 Data preprocessing & indexing using Spark ML
🌐 Web interface to display recommendations
💾 MongoDB integration for storing results
🧪 Model Performance
RMSE: 0.706
Accuracy: 25.7%
F1 Score: 0.19

(Metrics reflect implicit recommendation setup and sampled dataset)

🧩 System Architecture
Data is ingested from MongoDB
Preprocessed using PySpark
Model trained using ALS
Kafka producer sends input ASIN
Kafka consumer (Flask app) processes request
Recommendations generated using trained model
Results stored in MongoDB & displayed on UI
📂 Key Components
ALS Model Training – Spark-based recommendation engine
Kafka Producer/Consumer – Streaming pipeline
Flask App – API + UI rendering
MongoDB – Input/output storage
Batch Script – Automates system startup (Zookeeper, Kafka, services)
