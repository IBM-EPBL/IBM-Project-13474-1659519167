import mysql.connector


def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData




def insertBLOB(email,entry, prediction_image):
    print("Inserting BLOB into python_employee table")
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='test',
                                             user='root',
                                             password='')

        cursor = connection.cursor()
        sql_insert_blob_query = """ INSERT INTO user_images
                          (email, entry,prediction_image) VALUES (%s,%s,%s)"""

        empPicture = convertToBinaryData(prediction_image)

        # Convert data into tuple format
        insert_blob_tuple = (email, entry,empPicture)
        result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
        connection.commit()
        print("Image and file inserted successfully as a BLOB into python_employee table", result)

    except mysql.connector.Error as error:
        print("Failed inserting BLOB data into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")



