
import pymysql


def get_connection():
    host = '10.118.137.131'
    port = 3306
    user = 'root'
    pswd = 'root'
    dbname = 'test_platform'
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        passwd=pswd,
        db=dbname,
        charset='utf8'
    )
    return conn


if __name__ == '__main__':
    conn = get_connection()
    sql = "SELECT * from app_automation_android_suites"
    with conn.cursor() as cursor:
        cursor.execute(sql)
        print(cursor.description)
        for suite_name in cursor:
            print(suite_name)
        cursor.close()
