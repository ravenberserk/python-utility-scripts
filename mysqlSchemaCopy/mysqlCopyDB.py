#!/usr/bin/env python
""" Utility script that will  create a copy schema in MySQL DB. """

import subprocess
import os

__author__ = "Javier Grande Pérez"
__version__ = "1.0.0"
__maintainer__ = "Javier Grande Pérez"
__email__ = "raven.berserk@gmail.com"
__status__ = "Development"


class DbConfig():
    """ Default conection class. """

    def __init__(self):
        self.db_host = ''
        self.db_port = ''
        self.db_name = ''
        self.db_user = ''
        self.db_pass = ''

    def __str__(self):
        return 'Host: {0} \nPort: {1} \nName: {2}'.format(
            self.db_host, self.db_port, self.db_name)

    def __eq__(self, other):
        return self.db_host == other.db_host and self.db_name == other.db_name


class LocalDB(DbConfig):
    """ Connection params to local DB. """

    def __init__(self):
        self.db_host = 'localhost'
        self.db_port = '3306'
        self.db_name = 'local'
        self.db_user = 'root'
        self.db_pass = 'root'


class MirrorDB(LocalDB):
    """ Connection params to mirror-local DB. """

    def __init__(self):
        LocalDB.__init__(self)
        self.db_name = 'mirror'


class CustomDB(DbConfig):
    """ Connection params to custom DB. """

    def __init__(self):
        self.db_host = input('Indicate the host: ')
        self.db_port = input('Indicate the port [3306]: ') or '3306'
        self.db_name = input('Indicate the db name: ')
        self.db_user = input('Indicate the user: ')
        self.db_pass = input('Indicate the password: ')


def __check_db_connection(db_info: DbConfig):
    """ Check the conection to the DB. """

    proc = subprocess.run(
        'mysql -u{0} -p{1} -h{2} -P{3} {4} -s --execute="SELECT 1 FROM DUAL"'
        .format(
            db_info.db_user, db_info.db_pass,
            db_info.db_host, db_info.db_port, db_info.db_name),
        shell=True, check=True)


def __get_bd(def_opt: str) -> DbConfig:
    """ Auxiliar method, that will select the orig DB. """

    while(True):
        print("1 - Mirror")
        print("2 - Local")
        print("3 - Specify connection info")
        print('')

        selected_db = input('Enter the DB you want to select [{0}]: '
                            .format(def_opt)) or def_opt

        if selected_db == '1':
            return MirrorDB()

        elif selected_db == '2':
            return LocalDB()

        elif selected_db == '3':
            db_info = CustomDB()

            # Check the connection info, that it given by the user
            try:
                __check_db_connection(db_info)
                return db_info
            except subprocess.CalledProcessError as error:
                print('Connection info are not correct. ', error)

        else:
            print('Select a valid option.')


def __generate_dump(db_info: DbConfig):
    """ Auxiliar method, that generate the dump file from orig DB. """

    subprocess.run('mysqldump -u{0} -p{1} -h{2} -P{3} {4} > ./01.dump.sql'
                   .format(db_info.db_user, db_info.db_pass,
                           db_info.db_host, db_info.db_port, db_info.db_name),
                   shell=True)


def __create_copy(db_info: DbConfig):
    """Auxiliar method, that will copy the dump in the new DB. """

    subprocess.run(
        'mysql -u{0} -p{1} -h{2} -P{3} --execute="DROP DATABASE IF EXISTS {4}"'
        .format(db_info.db_user, db_info.db_pass,
                db_info.db_host, db_info.db_port, db_info.db_name),
        shell=True)

    subprocess.run(
        'mysql -u{0} -p{1} -h{2} -P{3} --execute="CREATE DATABASE {4}"'
        .format(db_info.db_user, db_info.db_pass,
                db_info.db_host, db_info.db_port, db_info.db_name),
        shell=True)

    subprocess.run(
        'mysql -u{0} -p{1} -h{2} -P{3} {4} < ./01.dump.sql'
        .format(db_info.db_user, db_info.db_pass,
                db_info.db_host, db_info.db_port, db_info.db_name),
        shell=True)


def main():
    """ Main method, that will be responsible for create the new Schema. """

    print("-----------------------------------------")
    print("------- Starting the Copy Process -------")
    print("-----------------------------------------")
    print('')
    print("-----------------------------------------")
    print("---------- Enter the source DB ----------")
    print("-----------------------------------------")
    print('')

    orig_connection = __get_bd('1')

    print("-----------------------------------------")
    print("------ Enter the destination DB. --------")
    print("-----------------------------------------")
    print('')

    dest_connection = __get_bd('2')

    while orig_connection == dest_connection:
        print('The selected DBs are the same.')
        dest_connection = __get_bd()

    print("-----------------------------------------")
    print("--------- Generating the Dump -----------")
    print("-----------------------------------------")
    print('')

    __generate_dump(orig_connection)

    print("-----------------------------------------")
    print("---------- Creating the copy ------------")
    print("-----------------------------------------")
    print('')

    __create_copy(dest_connection)

    os.remove('./01.dump.sql')
    input('The process completed successfully. :)')

if __name__ == '__main__':
    main()
