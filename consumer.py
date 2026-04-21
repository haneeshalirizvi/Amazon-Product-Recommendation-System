import findspark

findspark.init("C:/spark")
from kafka import KafkaConsumer
import json
from flask import Flask,render_template ,request
from flask_pymongo import PyMongo
from pyspark.sql import SparkSession
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.feature import StringIndexerModel
from pyspark.ml.feature import StringIndexer
from pyspark.ml.recommendation import ALSModel

#"B000068O4E"

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/flask"
mongo = PyMongo(app)



# Initialize Kafka consumer
consumer = KafkaConsumer('asins', bootstrap_servers=['localhost:9092'],
                         auto_offset_reset='latest',
                         enable_auto_commit=True,
                         group_id='my-group',
                         value_deserializer=lambda x:
                         json.loads(x.decode('utf-8')))


@app.route('/')
def get_recommendations():
    for message in consumer:
        output = message.value['input']
        print(output)
        break
    spark = SparkSession.builder \
    .appName("Amazon Recommendation Model with ALS") \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "8g") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()
    df_s = spark.read.json("C:/Users/Mubashir/Desktop/Consumer/zource/Temp.json") 
    #df_s.show()
    reviewer_indexer = StringIndexer(inputCol="reviewerID", outputCol="reviewer_index").fit(df_s)
    asin_indexer = StringIndexer(inputCol="asin", outputCol="asin_index").fit(df_s)
    overall_indexer = StringIndexer(inputCol="overall", outputCol="overall_index").fit(df_s)
    indexed_data = reviewer_indexer.transform(df_s)
    indexed_data = asin_indexer.transform(indexed_data)
    indexed_data = overall_indexer.transform(indexed_data)

    # Load the saved indexer and ALS models
    reviewer_indexer = StringIndexerModel.load("C:/Users/Mubashir/Desktop/Consumer/zource/reviewer_indexer").setHandleInvalid("keep")
    asin_indexer = StringIndexerModel.load("C:/Users/Mubashir/Desktop/Consumer/zource/asin_indexer").setHandleInvalid("keep")
    model = ALSModel.load("C:/Users/Mubashir/Desktop/Consumer/zource/als_modelFinal")

    input_asin = output
    print(input_asin)
    # Convert the input ASIN to its corresponding index
    input_asin_index = asin_indexer.transform(
        spark.createDataFrame([(input_asin,)] * indexed_data.count(), ["asin"])
    ).select("asin_index").collect()[0][0]
    #print("Yellow")

    # Make predictions for all the items in the dataset
    all_items = indexed_data.select("asin_index").distinct()
    predictions = model.transform(all_items.withColumn("reviewer_index", lit(input_asin_index)))
    #predictions.show()

    from pyspark.ml.feature import IndexToString

    # Extract the asin_index and prediction columns from the predictions dataframe
    predicted_asins = predictions.select("asin_index", "prediction")

    # Convert the asin_index values to asin strings
    converter = IndexToString(inputCol="asin_index", outputCol="asin", labels=asin_indexer.labels)
    predicted_asins = converter.transform(predicted_asins).select("asin")

    # Show the resulting asin values
   # predicted_asins.show()

    predicted_asins.orderBy(col("prediction").desc()).limit(3).show()


    top_asins = predicted_asins.limit(3).rdd.map(lambda x: x[0]).collect()

    # Concatenate the ASINs into a comma-separated string
    asins_string = ", ".join(top_asins)
   # print(type(asins_string))

    # Print the string
    #print(asins_string)
    mongo.db.userid.insert_one({
        "asin": input_asin,
        "Recommendations": asins_string,
    })
    
     
    #return asins_string
    return render_template('consumer.html', asin=asins_string)
   # return asins_string



@app.route('/')
def index():
    return render_template('consumer.html')



if __name__ == '__main__':
    app.run()
