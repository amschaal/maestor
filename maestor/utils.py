
def dictfetchall(sql,args=[]):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(sql, args)
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def fetchall(sql,args=[]):
    from django.db import connection
    cursor = connection.cursor()
    if len(args) > 0:
        cursor.execute(sql, args)
    else:
        cursor.execute(sql)
    return cursor.fetchall()
