u'''
Created on 13.10.2013
Last update on 13.05.2015

@author: alkarps

mail - модуль отправки письма. Может выступать и как библеотека, и как приложение. Для получения справки по работе в качестве приложения, пожалуйста, выполните команду "python mail.py -h"

List changes on 13.05.2015:
    1) Добавлен режим работы в качестве приложения.
    2) Добавлены входные параметры для работы в качестве приложения.
    3) Добавлено описание модуля и функций.

List changes on 20.05.2015:
    1) Добавлена поддержка изображений. 
'''
# -*- coding: utf8 -*-

def sent_mail(text, to, subj, server = None, port = None, user_name = None, user_passwd = None, images = None):
    u'''Функция отправки письма.
    На вход принимает следующие значения: to, text, subj [, server, port, user_name, user_passwd].
    Параметры server, port, user_name, user_passwd не обязательны. Передаются через ключи при каждом вызове функции.
    Параметры text, to, subj являются обязательными. ''';
    import smtplib;
    from email.MIMEText import MIMEText;
    from email.mime.multipart import MIMEMultipart;
    if server is None:
        server = default_server;
    if port is None:
        port = default_port;
    if user_name is None:
        user_name = default_user;
    if user_passwd is None:
        user_passwd = default_passwd;
    # формирование сообщения
    msgRoot = MIMEMultipart('related');
    msgRoot['Subject'] = subj
    msgRoot['From'] = user_name
    msgRoot['To'] = to
    msgText = MIMEMultipart('alternative')
    msgText = MIMEText(text, "html", "utf-8")
    msgText['Content-Type'] = "text/html; charset=utf8"
    msgRoot.attach(msgText)
    #Аттачим картинки
    if images is not None:
        from email.mime.image import MIMEImage;
        for image in images:
            fp = open(image, 'rb');
            img = MIMEImage(fp.read());
            fp.close();
            img.add_header('Content-ID', image);
            msgRoot.attach(img);
    # отправка
    s = smtplib.SMTP(server, port)
    try:
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(user_name, user_passwd)
        s.sendmail(user_name, to, msgRoot.as_string())
    finally:
        s.quit()


def main():
    u'''Основная функция модуля в режиме приложения. Выполняет парсинг входных параметров и вызывает функцию sent_mail. Для получения справки по работе в данном режиме выполните, пожалуйста, следующую команду "python mail.py -h" из командной строки''';
    import argparse;
    arg_parser = argparse.ArgumentParser(description = 'Модуль отправки email. Может выступать и как библеотека, и как приложение.', prog='sent_email');
    arg_parser.add_argument('to', type=str, help="Email'ы получателей");
    arg_parser.add_argument('subj', type=str, help='Тема сообщения.');
    arg_parser.add_argument('text', type=str, help='Текст сообщения.');
    arg_parser.add_argument('-s','--server', type=str, default=default_server, required=False, help="Адрес сервера почты. Значение по-умолчанию: %(default)s");
    arg_parser.add_argument('-p','--port', type=int, default=default_port, required=False, help="Порт сервера почты. Значение по-умолчанию: %(default)s");
    arg_parser.add_argument('-u','--user', type=str, default=default_user, required=False, help="Email отправителя, а так же логин для авторизации на сервере почты. Значение по-умолчанию: %(default)s");
    arg_parser.add_argument('-up','--user_passwd', type=str, default=default_passwd, required=False, help="Пароль для авторизации на сервере почты.");
    args = vars(arg_parser.parse_args());
    sent_mail(args['text'], args['to'], args['subj'], args['server'], args['port'], args['user'], args['user_passwd']);
    

default_server = 'outlook.office365.com';
default_port = 587;
default_user = 'default';
default_passwd = 'default';
if __name__ == '__main__':
    main();