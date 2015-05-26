# -*- coding: utf8 -*-
import utils;
import logging;
import mail;
import graphicsutil;
from multiprocessing import Process, Manager;

def getESSDZStatByTNS(dicTable, setting):
    logging.basicConfig(filename='ESSDZ_stat_log.log', format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.DEBUG);
    login = setting[0];
    password = setting[1];
    host = setting[2];
    port = setting[3];
    sid = setting[4];
    name = setting[5];
    logging.info("Start formatting zubaTable for "+name);
    result = [];
    #Собирание строки для таблицы Зубарева
    listQueryForZubaTable = ["""select nvl(sum(decode(processingstatus, 'S', 1, 0)),0) "Success",
   nvl(sum(decode(processingstatus, 'E', 1, 0)),0) "Error",
   nvl(sum(decode(processingstatus, 'W', 1, 0)),0) "Wait",
   nvl(sum(decode(processingstatus, 'D', 1, 0)),0) "Deleted"
    from mdm_events where processingstatus !='N' and lastprocessingtime between trunc(SYSDATE-1/24,'HH24') and trunc(SYSDATE,'HH24') -1/86400
    ""","""select count(1) "New_all" from mdm_events where operationtime between trunc(SYSDATE-1/24,'HH24') and trunc(SYSDATE,'HH24') -1/86400""","""select count(1) "New_processed" from mdm_events where operationtime between trunc(SYSDATE-1/24,'HH24') and trunc(SYSDATE,'HH24') -1/86400 and lastprocessingtime  between trunc(SYSDATE-1/24,'HH24') and trunc(SYSDATE,'HH24') -1/86400""","""select count(1) "All_processed" from mdm_events where lastprocessingtime  between trunc(SYSDATE-1/24,'HH24') and trunc(SYSDATE,'HH24') -1/86400"""];
    zubaRowTable = utils.getOneRowTableByListQuery(login, password, host, port, sid, listQueryForZubaTable, name);
    result.append(zubaRowTable);
    logging.info("Start formatting errorTable for "+name);
    #Собирание таблицы статистики ошибок
    listQuery = ["""SELECT  e.entitytypeid, me.name, e.operationtype, e.processingstatus, e.error_descr, count(*)
    FROM mdm_events e join mdm_entities me on e.entitytypeid=me.entitytypeid
    where e.entitytypeid not in (122,117,118,119,125,126,128) and e.processingstatus = 'E' and
    e.LASTPROCESSINGTIME BETWEEN trunc(SYSDATE-1/24,'HH24') and trunc(SYSDATE,'HH24')-1/86400
    group by e.entitytypeid, me.name, e.operationtype, e.processingstatus, e.error_descr order by e.entitytypeid, e.operationtype, e.processingstatus""",]
    statTables = utils.getStatByListQuery(login, password, host, port, sid, listQuery);
    stat = """<table>
    <tr>
        <th>ID сущности</th>
        <th>Название сущности</th>
        <th>Операция</th>
        <th>Статус</th>
        <th>Описание ошибки</th>
        <th>Количество</th>
    </tr>""";
    stat = stat + statTables[0] + "</table>";
    result.append(stat);
    logging.info("Start formatting points for "+name);
    graphs = utils.getPointsForGraphicsByListQuery(login, password, host, port, sid, ["""with temp_e as
        (select to_number(to_char(lastprocessingtime,'MI')) mi, count(1) cnt
         from mdm_events
         where lastprocessingtime between trunc(SYSDATE-1/24,'HH24') and trunc(SYSDATE,'HH24') -1/86400
         group by to_number(to_char(lastprocessingtime,'MI')))
    select t.mi, nvl(e.cnt, 0)
    from (select level-1 as mi
         from dual
         connect by level <= 60) t
    left join temp_e e
      on t.mi = e.mi
    order by t.mi""", """with temp_e as
        (select to_number(to_char(operationtime,'MI')) mi, count(1) cnt
         from mdm_events
         where operationtime between trunc(SYSDATE-1/24,'HH24') and trunc(SYSDATE,'HH24') -1/86400
         group by to_number(to_char(operationtime,'MI')))
    select t.mi, nvl(e.cnt, 0)
    from (select level-1 as mi
         from dual
         connect by level <= 60) t
    left join temp_e e
      on t.mi = e.mi
    order by t.mi"""], ['all processed per minute','all new per minute']);
    pic = '<img src="cid:'+name+'_pic.png" alt="график зависимости количества обработанных за минуту за последний час">';
    result.append(pic);
    logging.info("Start formatting graphics for "+name);
    picname = name+'_pic.png'
    graphicsutil.createGraphicByPoints(graphics = graphs, fileName = picname,lableX=u"minute",lableY=u"Count per minute", minX = 0, maxX = 59);
    logging.info("Add to dic for "+name);
    #Передача в основной поток
    if tuple(result) not in dicTable: dicTable[name] = tuple(result);
    logging.info("Finish getESSDZStatByTNS for "+name);


if __name__ == '__main__':
    #Список настроек подключений к БД. В картежах параметры подключения в седующем порядке: логин, пароль, хост, порт, сид, название региона (может быть на русском)
    settingList = [('login','password','localhost','port','sid', 'name'),('login','password','localhost','port','sid', 'name')];
    processList = [];
    logging.basicConfig(filename='ESSDZ_stat_log.log', format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.DEBUG);
    logging.info("Start getting statistic");
    manager = Manager();
    dicTable = manager.dict();
    #Запускаем на каждую БД свой поток.
    logging.info("Start threads");
    for setting in settingList:
        process = Process(target=getESSDZStatByTNS, args=(dicTable,setting));
        processList.append(process);
        process.start();
    for process in processList:
        process.join();
    logging.info("Finish threads");
    logging.info("Start building text mail");
    #Собираем текст письма из результатов
    emailText = """<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>ЕССДЗ Статистика</title>
        <style type="text/css">
            table {
                border-collapse: collapse;
            }
            th {
                background: #ccc;
                text-align: center;
            }
            td{
                text-align: right;
            }
            td, th {
                border: 1px solid #800;
                padding: 4px;
            }
        </style>
    </head>
        <body>
            <table style="border-collapse: collapse;">
                <tr>
                    <th rowspan="2">RF</th>
                    <th rowspan="2">Success</th>
                    <th rowspan="2">Error</th>
                    <th rowspan="2">Wait</th>
                    <th rowspan="2">Deleted</th>
                    <th colspan="2">New</th>
                    <th rowspan="2">All processed</th>
                </tr>
                <tr>
                    <th>all</th>
                    <th>processed</th>
                </tr>""";
    keys = dicTable.keys();
    errorTables = "";
    pics = [];
    for key in keys:
        emailText = emailText + dicTable[key][0];
        errorTables = errorTables + "\n <h2>" + key + "</h2>\n"+dicTable[key][1] + "<br>" +dicTable[key][2];
        pics.append(key + '_pic.png');
    emailText = emailText + "</table>\n" + errorTables + "</body></html>";
    #print emailText;
    logging.info("Finish building text mail");
    #Кому отправлять письмо
    to = 'to@mail.ru';
    #Тема письма
    subject = 'YESSDZ stats'
    logging.info("Start sending mail");
    mail.sent_mail(text = emailText, to = to, subj = subject, images = pics);
    logging.info("Finish sending mail");
