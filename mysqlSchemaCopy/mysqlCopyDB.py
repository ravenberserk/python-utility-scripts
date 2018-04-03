#!/usr/bin/env python
"""Utility script that will  create a copy schema in MySQL DB."""

__author__ = "Javier Grande Pérez"
__version__ = "1.0.0"
__maintainer__ = "Javier Grande Pérez"
__email__ = "raven.berserk@gmail.com"
__status__ = "Development"

import subprocess
import os


class DbConfig():
    """Default conection class."""

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

    def _generate_connection(self):
        return 'mysql -u{0} -p{1} -h{2} -P{3}'.format(self.db_user,
                                                      self.db_pass,
                                                      self.db_host,
                                                      self.db_port)


class LocalDB(DbConfig):
    """Connection params to local DB."""

    def __init__(self):
        self.db_host = 'localhost'
        self.db_port = '3306'
        self.db_name = 'local'
        self.db_user = 'root'
        self.db_pass = 'root'


class MirrorDB(LocalDB):
    """Connection params to mirror-local DB."""

    def __init__(self):
        LocalDB.__init__(self)
        self.db_name = 'mirror'


class CustomDB(DbConfig):
    """Connection params to custom DB."""

    def __init__(self):
        self.db_host = input('Indicate the host [localhost]: ') or 'localhost'
        self.db_port = input('Indicate the port [3306]: ') or '3306'
        self.db_name = input('Indicate the db name: ')
        self.db_user = input('Indicate the user: ')
        self.db_pass = input('Indicate the password: ')


def _check_db_connection(db_info: DbConfig):
    """Check the conection to the DB."""

    proc = subprocess.run(
        'mysql -u{0} -p{1} -h{2} -P{3} {4} -s --execute="SELECT 1 FROM DUAL"'
        .format(
            db_info.db_user, db_info.db_pass,
            db_info.db_host, db_info.db_port, db_info.db_name),
        shell=True, check=True)


def _get_bd(def_opt: str) -> DbConfig:
    """Auxiliar method, that will select the orig DB."""

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
                _check_db_connection(db_info)
                return db_info
            except subprocess.CalledProcessError as error:
                print('Connection info are not correct. ', error)

        else:
            print('Select a valid option.')


def _generate_dump(db_info: DbConfig):
    """Auxiliar method, that generate the dump file from orig DB."""
    print("-----------------------------------------")
    print("--------- Generating the Dump -----------")
    print("-----------------------------------------")
    print('')

    subprocess.run('mysqldump -u{0} -p{1} -h{2} -P{3} {4} > ./01.dump.sql'
                   .format(db_info.db_user, db_info.db_pass,
                           db_info.db_host, db_info.db_port, db_info.db_name),
                   shell=True)


def _create_copy(db_info: DbConfig):
    """Auxiliar method, that will copy the dump in the new DB."""
    print("-----------------------------------------")
    print("---------- Creating the copy ------------")
    print("-----------------------------------------")
    print('')

    delete_db = db_info._generate_connection()
    + ' --execute="DROP DATABASE IF EXISTS {0}"'.format(db_info.db_name)
    subprocess.run(delete_db, shell=True)

    create_db = db_info._generate_connection()
    + ' --execute="CREATE DATABASE {0}"'.format(db_info.db_name)
    subprocess.run(create_db, shell=True)

    restore_dump = db_info._generate_connection()
    + ' {0} < ./01.dump.sql'.format(db_info.db_name)
    subprocess.run(restore_dump, shell=True)


def _get_source_db() -> DbConfig:
    print("-----------------------------------------")
    print("---------- Enter the source DB ----------")
    print("-----------------------------------------")
    print('')

    return _get_bd('1')


def _get_dest_db(source_db: DbConfig) -> DbConfig:
    print("-----------------------------------------")
    print("------ Enter the destination DB ---------")
    print("-----------------------------------------")
    print('')

    dest_connection = _get_bd('2')

    while source_db == dest_connection:
        print('The selected DBs are the same.')
        dest_connection = _get_bd('2')

    return dest_connection


def main():
    """Main method, that will be responsible for create the new Schema."""
    print("-----------------------------------------")
    print("------- Starting the Copy Process -------")
    print("-----------------------------------------")
    print('')

    source_db = _get_source_db()

    dest_db = _get_dest_db(source_db)

    _generate_dump(source_db)

    _create_copy(dest_db)

    os.remove('./01.dump.sql')
    input('The process completed successfully. :)')


if __name__ == '__main__':
    main()
