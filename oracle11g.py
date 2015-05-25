# coding=utf-8
u'''
Created on 7.05.2013
Last update on 13.05.2015

@author: alkarps

oracle11g - библиотека для работы с СУБД Oracle 11g. Функции, входящие в состав библиотеки:
	1)getResult - функция получения результата вызова select-запроса. Для более подробное описание в docstring функции. 

Требования для работы: необходим установленны модуль cx_Oracle, а так же клиент Oracle 11g.

List changes on 13.05.2015
	1) Добавлено docstring для библиотеки.
'''

def getResult(login,password,host,port,sid,query):
	u"""Функция получения результата вызова select-запроса.
	Входные параметры: 
		login - логин для подключения к БД.
		password - пароль для подключения к БД.
		host - адрес БД.
		port - порт БД.
		sid - СИД БД.
		query - select-запрос.
	Выходные параметры: результат выполнения запроса в виде списка кортежей.
	"""
	#import os;
	#os.environ('ORACLE_HOME') = '/home/coder/rcuHome/';
	tns = cx_Oracle.makedsn(host,port,sid);
	con = cx_Oracle.connect(login,password,tns,threaded=True);
	cur = con.cursor();
	cur.execute(query);
	result = cur.fetchall();
	con.close();
	return result;
	
if __name__ == '__main__':
	print 'Please, read docstring for more information.';
else:
	import cx_Oracle;