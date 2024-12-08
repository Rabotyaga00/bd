import aiomysql
import asyncio

dbname = str(input("Введите название базы данных: "))
dbtable = str(input("Введите название таблицы: "))


# Подключение к базе данных с использованием await
async def create_database():
    connection = await aiomysql.connect(
        host='localhost',
        user='root',
        password='password',
        charset='utf8mb4',
        cursorclass=aiomysql.cursors.DictCursor
    )
    print("Подключение к MySQL успешно")
    async with connection.cursor() as cursor:
        global dbname
        sql = f"CREATE DATABASE IF NOT EXISTS {dbname}"
        await cursor.execute(sql)
        await connection.commit()
        sql1 = "SHOW DATABASES"
        await cursor.execute(sql1)
        await connection.commit()
        print("Список баз данных:")
        async for db in cursor:
            print(db)
    connection.close()


async def create_table():
    global dbtable
    global dbname
    connection = await aiomysql.connect(
        host='localhost',
        user='root',
        password='password',
        charset='utf8mb4',
        db=dbname,
        cursorclass=aiomysql.cursors.DictCursor
    )
    print("Подключение к MySQL успешно")
    async with connection.cursor() as cursor:
        sql = f"""
        CREATE TABLE IF NOT EXISTS {dbtable} (
            P_ID INT PRIMARY KEY,
            LastName VARCHAR(255),
            FirstName VARCHAR(255),
            Address VARCHAR(255),
            City VARCHAR(255)
        )
        """
        await cursor.execute(sql)
        await connection.commit()
        sql1 = "SHOW TABLES"
        await cursor.execute(sql1)
        await connection.commit()
        print("Список таблиц:")
        async for tables in cursor:
            print(tables)
    connection.close()


async def mysql_input():
    global dbtable
    global dbname
    connection = await aiomysql.connect(
        host='localhost',
        user='root',
        password='password',
        charset='utf8mb4',
        db=dbname,
        cursorclass=aiomysql.cursors.DictCursor
    )
    print("Подключение к MySQL успешно")
    async with connection.cursor() as cursor:
        P_ID = int(input("Введите ID: "))
        LastName = str(input("Введите Фамилию: "))
        FirstName = str(input("Введите Имя: "))
        Address = str(input("Введите Адрес: "))
        City = str(input("Введите Город: "))
        sql = f"INSERT INTO {dbtable} (P_ID, LastName, FirstName, Address, City) VALUES (%s, %s, %s, %s, %s)"
        await cursor.execute(sql, (P_ID, LastName, FirstName, Address, City))
        await connection.commit()
    connection.close()
    print("Данные внесены успешно")


async def mysql_output():
    global dbtable
    global dbname
    connection = await aiomysql.connect(
        host='localhost',
        user='root',
        password='password',
        charset='utf8mb4',
        db=dbname,
        cursorclass=aiomysql.cursors.DictCursor
    )
    print("Подключение к MySQL успешно")
    async with connection.cursor() as cursor:
        print("Выберите, какие данные вывести:")
        filter_choice = input("Нужна ли фильтрация данных? (y/n): ")
        if filter_choice.lower() == 'y':
            filter_column = input("Введите имя столбца для фильтрации: ")
            filter_value = input(f"Введите значение для фильтрации по столбцу {filter_column}: ")
            sql = f"SELECT * FROM {dbtable} WHERE {filter_column} = %s"
            await cursor.execute(sql, (filter_value,))
        else:
            sql = f"SELECT * FROM {dbtable}"
            await cursor.execute(sql)

        result = await cursor.fetchall()
        if result:
            for row in result:
                print(row)
        else:
            print("Нет данных для вывода.")
    connection.close()


async def mysql_delete():
    global dbtable
    global dbname
    connection = await aiomysql.connect(
        host='localhost',
        user='root',
        password='password',
        charset='utf8mb4',
        db=dbname,
        cursorclass=aiomysql.cursors.DictCursor
    )
    print("Подключение к MySQL успешно")
    async with connection.cursor() as cursor:
        delete = str(input("Введите фамилию для удаления: "))
        sql = f"DELETE FROM {dbtable} WHERE LastName = %s"
        await cursor.execute(sql, (delete,))
        await connection.commit()
        sql1 = f"SELECT * FROM {dbtable}"
        await cursor.execute(sql1)
        result = await cursor.fetchall()
        if result:
            for row in result:
                print(row)
        else:
            print("Запись удалена.")
    connection.close()


async def mysql_truncate():
    global dbtable
    global dbname
    connection = await aiomysql.connect(
        host='localhost',
        user='root',
        password='password',
        charset='utf8mb4',
        db=dbname,
        cursorclass=aiomysql.cursors.DictCursor
    )
    print("Подключение к MySQL успешно")
    async with connection.cursor() as cursor:
        sql = f"TRUNCATE TABLE {dbtable}"
        await cursor.execute(sql)
        await connection.commit()
    connection.close()
    print("Таблица очищена.")


async def mysql_drop():
    global dbtable
    global dbname
    connection = await aiomysql.connect(
        host='localhost',
        user='root',
        password='password',
        charset='utf8mb4',
        db=dbname,
        cursorclass=aiomysql.cursors.DictCursor
    )
    print("Подключение к MySQL успешно")
    async with connection.cursor() as cursor:
        sql = f"DROP TABLE IF EXISTS {dbtable}"
        await cursor.execute(sql)
        await connection.commit()
    connection.close()
    print("Таблица удалена.")


async def main():
    print("Добро пожаловать в интерфейс работы с MySQL.")
    while True:
        print("\nДоступные команды:")
        print("1 - Создать базу данных")
        print("2 - Создать таблицу")
        print("3 - Вставить данные")
        print("4 - Вывести данные")
        print("5 - Удалить данные")
        print("6 - Очистить таблицу")
        print("7 - Удалить таблицу")
        print("Exit - Выход")

        cmd = input("Введите команду: ")

        if cmd == "1":
            await create_database()  # Используем await
        elif cmd == "2":
            await create_table()  # Используем await
        elif cmd == "3":
            await mysql_input()  # Используем await
        elif cmd == "4":
            await mysql_output()  # Используем await
        elif cmd == "5":
            await mysql_delete()  # Используем await
        elif cmd == "6":
            await mysql_truncate()  # Используем await
        elif cmd == "7":
            await mysql_drop()  # Используем await
        elif cmd.lower() == "exit":
            print("Выход из программы.")
            break
        else:
            print("Ошибка: Неизвестная команда.")


# Запуск программы
asyncio.run(main())
