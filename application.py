import boto3
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from flaskext.mysql import MySQL
import redis

application = Flask(__name__)

# cors
cors = CORS(application, resources={r"/*": {"origins": "*"}})

# mysql
mysql = MySQL()
application.config['MYSQL_DATABASE_USER'] = os.environ["MYSQL_DATABASE_USER"]
application.config['MYSQL_DATABASE_PASSWORD'] = os.environ["MYSQL_DATABASE_PASSWORD"]
application.config['MYSQL_DATABASE_DB'] = os.environ["MYSQL_DATABASE_DB"]
application.config['MYSQL_DATABASE_HOST'] = os.environ["MYSQL_DATABASE_HOST"]

# application.config['MYSQL_DATABASE_USER'] = 'admin'
# application.config['MYSQL_DATABASE_PASSWORD'] = '12345678'
# application.config['MYSQL_DATABASE_DB'] = 'sparta'
# application.config['MYSQL_DATABASE_HOST'] = 'database-1.cgbie0k3ndqh.ap-northeast-2.rds.amazonaws.com'
mysql.init_app(application)

# redis
db = redis.Redis('sparta-redis.8imnfo.0001.apn2.cache.amazonaws.com')


@application.route('/')
def main():
    return "hello python"

@application.route('/fileupload', methods=['POST'])
def file_upload():
    file = request.files['file']
    s3 = boto3.client('s3',
                      aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
                      )
    s3.put_object(
        ACL="public-read",
        Bucket=os.environ["BUCKET_NAME"],
        Body=file,
        Key=file.filename,
        ContentType=file.content_type
    )

    # mysql
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("insert into file(file_name) value('" + file.filename + "')")
    conn.commit()

    # redis
    cursor.execute("SELECT count(*) from file")
    data = cursor.fetchone()
    # db.set("fileCount", data[0])
    return jsonify({'result': 'success'})

@application.route('/file/count', methods=['GET'])
def file_count():
    return jsonify({'result': 'success', 'count': db.get("fileCount")})

if __name__ == '__main__':
    application.debug = True
    application.run()