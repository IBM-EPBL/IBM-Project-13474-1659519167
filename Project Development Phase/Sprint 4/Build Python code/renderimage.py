import mysql.connector


def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)


def readBLOB(email, prediction_image):
    print("Reading BLOB data from python_employee table")

    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='test',
                                             user='root',
                                             password='')

        cursor = connection.cursor()
        sql_fetch_blob_query = """SELECT * from user_images where email = %s ORDER BY entry DESC LIMIT 1"""

        cursor.execute(sql_fetch_blob_query, (email,))
        record = cursor.fetchall()
        for row in record:
            image = row[2]
            write_file(image, prediction_image)

    except mysql.connector.Error as error:
        print("Failed to read BLOB data from MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

