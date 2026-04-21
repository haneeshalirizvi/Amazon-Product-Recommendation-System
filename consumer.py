import findspark
findspark.init("C:/spark")

import json
from kafka import KafkaConsumer
from flask import Flask, render_template
from flask_pymongo import PyMongo

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from pyspark.ml.feature import StringIndexerModel, IndexToString
from pyspark.ml.recommendation import ALSModel

# ------------------ Flask Setup ------------------
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/flask"
db = PyMongo(app)

# ------------------ Kafka Consumer ------------------
kafka_consumer = KafkaConsumer(
    'asins',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='recommendation-group',
    value_deserializer=lambda msg: json.loads(msg.decode('utf-8'))
)

# ------------------ Spark Session ------------------
def create_spark_session():
    return SparkSession.builder \
        .appName("ALS Recommendation Engine") \
        .config("spark.executor.memory", "8g") \
        .config("spark.driver.memory", "8g") \
        .config("spark.jars.packages",
                "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
        .getOrCreate()


# ------------------ Recommendation Logic ------------------
def generate_recommendations(input_asin):
    spark = create_spark_session()

    # Load temporary dataset
    data = spark.read.json("C:/Users/Mubashir/Desktop/Consumer/zource/Temp.json")

    # Load trained models
    user_indexer = StringIndexerModel.load(
        "C:/Users/Mubashir/Desktop/Consumer/zource/reviewer_indexer"
    ).setHandleInvalid("keep")

    item_indexer = StringIndexerModel.load(
        "C:/Users/Mubashir/Desktop/Consumer/zource/asin_indexer"
    ).setHandleInvalid("keep")

    als_model = ALSModel.load(
        "C:/Users/Mubashir/Desktop/Consumer/zource/als_modelFinal"
    )

    # Transform dataset
    indexed_df = user_indexer.transform(data)
    indexed_df = item_indexer.transform(indexed_df)

    # Convert input ASIN → index
    asin_index_value = item_indexer.transform(
        spark.createDataFrame([(input_asin,)], ["asin"])
    ).select("asin_index").collect()[0][0]

    # Get all unique items
    items_df = indexed_df.select("asin_index").distinct()

    # Predict scores
    predictions_df = als_model.transform(
        items_df.withColumn("reviewer_index", lit(asin_index_value))
    )

    # Convert indices back to ASIN
    converter = IndexToString(
        inputCol="asin_index",
        outputCol="asin",
        labels=item_indexer.labels
    )

    final_predictions = converter.transform(predictions_df)

    # Get top 3 recommendations
    top_items = final_predictions.orderBy(
        col("prediction").desc()
    ).limit(3)

    asin_list = [row["asin"] for row in top_items.collect()]

    return asin_list


# ------------------ Routes ------------------
@app.route('/')
def recommend():
    # Read one message from Kafka
    for msg in kafka_consumer:
        user_input = msg.value['input']
        break

    recommendations = generate_recommendations(user_input)

    result_string = ", ".join(recommendations)

    # Store in MongoDB
    db.db.userid.insert_one({
        "asin": user_input,
        "recommendations": result_string
    })

    return render_template('consumer.html', asin=result_string)


@app.route('/home')
def home():
    return render_template('consumer.html')


# ------------------ Run App ------------------
if __name__ == '__main__':
    app.run(debug=True)