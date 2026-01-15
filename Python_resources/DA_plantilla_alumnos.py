from  conectar_logger import connect_to_mysql
import mysql.connector
from mysql.connector import errorcode
from config import config

def drop_database(cur, db_name):
    '''Borra una BDA si existe.
    Args:
        cursor(mysql.connector.cursor.MySQLCursor):cursor
        db_name(str):nombre de la BDA a borrar
    Returns:
        True si todo va bien. En otro caso retorna None e informa del error por consola
    '''
    SQL = f"drop database if exists {db_name}"
    try:
        cur.execute(SQL)
    except mysql.connector.Error as err:
        print(f"Fallo al borrar la BDA: {err} (seguramente no existe)")
    else:
        print(f"BDA {DB_NAME} borrada")
        return True


def create_database(cur, db_name, cset, col):
    '''Compone un CREATE DATABASE estilo MySQL y lo ejecuta.
    Args:
        cur(mysql.connector.cursor.MySQLCursor):cursor
        db_name(str):Nombre de la BDA
        cset(str):charset de la BDA
        col(str):colación de la BDA
    Returns:
        True si va todo bien. En otro caso sale del programa informando del error por consola
    '''
    SQL = f"create database if not exists {db_name} \
        character set {cset} \
        collate {col}"
    try:
        cur.execute(SQL)
    except mysql.connector.Error as err:
        print(f"Fallo al crear la BDA: {err}")
        exit(1)
    else: return True

def use_database(conn, cur, DB_NAME):
    '''Cambia a la BDA que se pasa como parámetro.
    Args:
        cur(mysql.connector.cursor.MySQLCursor):cursor con el que se trabaja
        DB_NAME(str):Nombre de la BDA con la que se pretende trabajar
    Returns:
        True o sale del programa en caso de no poder usar la BDA informando del error por consola
    
    '''
    SQL = f"USE {DB_NAME}"
    try:
        cur.execute(SQL)
    except mysql.connector.Error as err:
        print(f"La BDA {DB_NAME} no existe")
        if err.errno == errorcode.ER_BAD_DB_ERROR: # en el manejo de la excepción creamos la BDA
            create_database(cur, DB_NAME, 'utf8mb4', 'utf8mb4_spanish_ci') 
            print("BDA {DB_NAME} creada con éxito")
            conn.database = DB_NAME # usamos la BDA
        else: # Si no se puede solucionar informamos y salimos
            print(err)
            exit(1) 
    else:
        return True

def insert_multiple(cur, tabla, valores):
    '''Inserta en una tabla una lista de tuplas
    Args:
        cur(mysql.connector.cursor.MySQLCursor):cursor
        tabla(str):Nombre de una tabla de la BDA en uso
        valores(list[tuple]):Lista de registros a insertar 
    Returns:
        True o None informando del error por consola
    '''
    N_CAMPOS = len(valores[0])
    SQL_INSERT = f"insert into {tabla} values ({'%s, ' * (N_CAMPOS -1) + '%s'})"

    try:
        cur.executemany(SQL_INSERT, valores)
    except mysql.connector.Error as Err:
        print(Err.msg)
    else:
        return True


def obtener_tablas(conn, cur, bda):
    '''Obtiene una lista de tuplas con los nombres de las tablas de la BDA
    Args:
        cur(mysql.connector.cursor.MySQLCursor):cursor
        bda(str):Nombre de la BDA
    Returns:
        list[tuple] | None con información del error por consola
    '''
    try:
        use_database(conn, cur, bda)
        SQL = f'show tables'
        cur.execute(SQL)
        tablas = cur.fetchall() #obtenemos lista de nombres de tablas
    except mysql.connector.Error as Err:
        print(Err.msg)
    else:
        return tablas


def obtener_cabecera(cur, tabla):
    '''Obtiene los nombres de las columnas de la tabla
    Args:
        cur(mysql.connector.cursor.MySQLCursor):cursor
        tabla(str):Nombre de la tabla
    Returns:
        list[str] | None con mensaje de error por consola
    '''
    try:
        SQL = f'select * from {tabla} limit 1'
        cur.execute(SQL)
        cols = cur.column_names
    except mysql.connector.Error as Err:
        print(Err.msg)
    else:
        return cols


def leer_fila(cur, tabla):
    '''función que retorna las filas de una tabla
    Args:
        cur(mysql.connector.cursor.MySQLCursor):cursor
        tabla(str):Nombre de la tabla
    Returns:
        list[tuple]|None :lista de filas de la tabla o None con mensaje de error por consola.
    '''
    try:
        SQL_SELECT = f'select * from {tabla}'
        cur.execute(SQL_SELECT)
        lista = cur.fetchall()
    except mysql.connector.Error as Err:
        print(Err.msg)
    else:
        return lista

def crea_funcion(cur, SQL):
    ''' función que crea una función en el servidor MySQL
    Args:
        cur(mysql.connector.cursor.MySQLCursor):cursor
        SQL(str):Cadena con el SQL para crear la función
    Returns:
        True|None con mensaje de error por consola
    '''
    try:
        cur.execute(SQL)
    except mysql.connector.Error as Err:
        print(Err.msg())
    else:
        return True

def comprueba_expediente(cur, exp):
    '''Función que ejecuta la función expediente_correcto del servidor MySQL
    Args:
        exp(str):String que representa un expediente
    Returns:
        bool|None:expediente correcto/incorrecto o None con mensaje de error por consola
    '''
    try:
        SQL = "select expediente_correcto(%s)"
        cur.execute(SQL, (exp,))
        res = cur.fetchone()
    except mysql.connector.Error as Err:
        print(Err.msg())
    else:
        return res[0]

def pasan_curso(cur):
    '''Función que obtiene alumnos que pasan a segundo y su porcentaje
    Requisitos para pasar a segundo: tener todos los módulos con nota y media >= 6
    Args:
        cur(mysql.connector.cursor.MySQLCursor):cursor
    Returns:
        dict:Diccionario con clave 'pasan':list[str] (lista de expedientes) y con clave 'porcentaje':float
    '''
    lista_expedientes_pasan = []
    SQL = '''
    select expediente, AVG(nota), count(nota)
        from notas
        where nota is not null
        group by expediente'''
    cur.execute(SQL)
    alumnos = cur.fetchall()
    total = len(alumnos)
    for alumno in alumnos:
        if alumno[2] == 5 and alumno[1] >= 6:
            lista_expedientes_pasan.append(alumno[0])
    dict = {}
    dict['pasan'] = lista_expedientes_pasan
    dict['porcentaje'] = len(lista_expedientes_pasan) / total

    return dict
    

if __name__ == '__main__': 

    # 1. Conectar al servidor MySQL
    pass


    # 2 y 3. Crear la BDA y usarla
    # Si usais el servidor la BDA ya estará creada 
    DB_NAME = "nombre_de_tu_BDA"
    pass

    # Borrar la BDA por comodidad durante el testeo
    drop_database(cur, DB_NAME)

    pass
    print(f'BDA {DB_NAME} creada')

    # 4. Crear las tablas de la BDA
    TABLES = {}
    TABLES['alumnos'] = '''
    create table if not exists alumnos(
        expediente char(8) PRIMARY KEY,
        nombre varchar(30) NOT NULL,
        apellidos varchar(50) NOT NULL
    )'''
    TABLES['modulos'] = '''
    create table if not exists modulos(
        codigo varchar(5) PRIMARY KEY,
        nombre varchar(30) NOT NULL
    )'''
    TABLES['notas'] = '''
    create table if not exists notas(
        expediente char(8),
        codigo varchar(5),
        nota integer unsigned,
        PRIMARY KEY (expediente, codigo),
        constraint fk_expediente 
            foreign key (expediente)
            references alumnos(expediente)
            on delete cascade on update cascade,
        constraint fk_codigo
            foreign key (codigo)
            references modulos(codigo)
            on delete cascade on update cascade
    )'''
    TABLES['auditoria_notas'] = '''
    create table if not exists auditoria_notas(
        id serial PRIMARY KEY, -- clave autoincremental
        expediente_old char(8), -- expediente viejo
        codigo_old varchar(5), -- módulo viejo
        nota_old integer unsigned, -- nota antigua
        expediente_new char(8), -- expediente nuevo
        codigo_new varchar(5), -- módulo nuevo
        nota_new integer unsigned, -- nota nueva
        usuario varchar(50) not null, -- usuario que hace la modificación
        cuando datetime not null, -- fecha y hora de la modificación
        operacion enum('insert', 'update', 'delete') not null -- operación DML utilizada
    )'''

    for table_name in TABLES:
        pass
        print(f"Creando tabla {table_name}: ", end='')
        pass
        
    # 5. Crear triggers auditoría notas
    TRIGGERS_AUDITORIA = {}
    TRIGGERS_AUDITORIA['auditoria_notas_insert'] = '''
    create trigger if not exists auditoria_notas_insert after insert on notas
    for each row
        insert into auditoria_notas 
        values(null,null,null,null,new.expediente, new.codigo, new.nota, user(), now(),'insert')'''
    TRIGGERS_AUDITORIA['auditoria_notas_update'] = '''
    create trigger if not exists auditoria_notas_update after update on notas
    for each row
        insert into auditoria_notas 
        values(null, old.expediente, old.codigo, old.nota, new.expediente, new.codigo, 
        new.nota, user(), now(), 'update')'''
    TRIGGERS_AUDITORIA['auditoria_notas_delete'] = '''
    create trigger if not exists auditoria_notas_delete after delete on notas
    for each row
        insert into auditoria_notas 
        values(null, old.expediente, old.codigo, old.nota, null,null,null, user(), now(), 'delete')'''

    for trigger in TRIGGERS_AUDITORIA:
        pass
        print(f"Creando trigger {trigger}: ", end='')
        pass

    # 6. Inserción de datos en las tablas
    valores_alumnos = [
        ('11111111', 'Alexia', 'Núñez Pérez'), 
        ('22222222', 'Rosa', 'Fernández Oliva'), 
        ('33333333', 'Peter', 'Linuesa Jiménez'), 
        ('44444444', 'Juan Carlos', 'Wesnoth The Second'), 
        ('55555555', 'Federico', 'Muñoz Ferrer')
    ]
    pass
    print(f"registros en tabla alumnos insertados correctamente")
    pass

    valores_modulos = [
        ('QP', 'Quirománcia Práctica'),
        ('MR', 'Mortum Redivivus'),
        ('RF', 'Refactorización Zómbica'),
        ('ARF', 'Ampliación de RF'),
        ('OP', 'Orquestación de Plagas')
    ]

    pass
    print(f"registros en tabla modulos insertados correctamente")
    pass

    # NULL debe pasarse a None (equivalente Python)
    valores_notas = [
        ('11111111', 'QP', 5), 	('11111111', 'MR', 7),
        ('11111111', 'RF', 6),	('11111111', 'ARF', 9),
        ('11111111', 'OP', 7),	('22222222', 'QP', None),
        ('22222222', 'MR', 5),	('22222222', 'RF', 5),
        ('22222222', 'ARF', 6),	('22222222', 'OP', None),
        ('33333333', 'QP', 9),	('33333333', 'MR', 5),
        ('33333333', 'RF', 6),	('33333333', 'ARF', 4),
        ('33333333', 'OP', 6),	('44444444', 'QP', 4),
        ('44444444', 'MR', 6),	('44444444', 'RF', 8),
        ('44444444', 'ARF', 6),	('44444444', 'OP', 5),
        ('55555555', 'QP', 8),	('55555555', 'MR', 4),
        ('55555555', 'RF', None),   ('55555555', 'ARF', None),
        ('55555555', 'OP', 4)
    ]

    pass
    print(f"registros en tabla notas insertados correctamente")
    pass

    # 7. Mostrar los datos de todas las tablas
    pass


    # 8. Función en el lado del servidor que comprueba si un expediente es correcto 
    SQL_FUNCION = '''
    create function expediente_correcto(exp char(8)) returns BOOLEAN
    DETERMINISTIC
    NO SQL
        return (exp regexp '^[0-9]{8}$')
    '''
    pass

    # 9. Probando la función
    # NOTA: si los expedientes pasan de 8 caracteres da error. Es por la función en el lado del servidor.
    EXPEDIENTES = ['11112222', 'XXXYYYZZ']

    pass

    # 10. Función pasan_segundo
    pass
    # cerrar todo
    pass