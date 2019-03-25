from enum import Enum
from termcolor import colored
from datetime import datetime
from requests import Session
import os
import json


class LogLevel(Enum):
    DEBUG = 0,
    TRACE = 1,
    INFO = 2,
    WARN = 3,
    ERROR = 4,
    FATAL = 5


class HttpMethod(Enum):
    GET = 0,
    POST = 1


class LogFormat(Enum):
    TEXT = 0,
    JSON = 1


class LogDateFormat(Enum):
    LOCAL = 0,
    UTC = 1


class Log:
    def __init__(self, console_out=True, date_format=LogDateFormat.LOCAL, file_name=None,
                 file_rewrite=False, file_write_format=LogFormat.TEXT,
                 http_address=None, http_method=HttpMethod.GET, http_session=None,
                 http_format=LogFormat.TEXT, log_handler=None,
                 min_level_file=LogLevel.INFO, min_level_console=LogLevel.TRACE, min_level_http=LogLevel.INFO):
        self.console_flag = console_out
        self.file_flag = False
        self.http_flag = False
        self.handler_flag = log_handler is None

        if file_name is not None:
            self.file_name = file_name
            self.file_flag = True
            self.file_rewrite_flag = file_rewrite
            self.file_format = file_write_format
            self.min_level_file = min_level_file

            if self.file_rewrite_flag:
                self.control_file_flag = False

        if http_address is not None:
            self.http_address = http_address
            self.http_flag = True
            self.http_method = http_method
            self.http_send_format = http_format
            self.min_level_http = min_level_http

            if http_session is None:
                self.session = Session()
            else:
                self.session = http_session

            if log_handler is not None:
                self.handler = log_handler
                self.handler_flag = True


        if self.console_flag:
            self.min_level_console = min_level_console

        self.date_format = date_format

    def debug(self, message: str):
        pass

    def __main_writer(self, log_level: LogLevel ,message:str):
        if self.date_format == LogDateFormat.LOCAL:
            date_now = datetime.now()
        elif self.date_format == LogDateFormat.UTC:
            date_now = datetime.utcnow()
        else:
            raise ValueError('Wrong log date format')
        date_string = date_now.strftime("%d.%m.%Y %H:%M:%S.%f")

        level_string = self.__get_level_string(log_level)
        level_color = self.__get_level_color(log_level)

        log_string = f'{level_string.upper()}: [{date_string}]: {message}'
        log_object = {
            "date": date_now,
            "type": level_string,
            "message": message
        }
        log_json_string = json.dumps(log_object)

        if self.console_flag:
            if not log_level < self.min_level_console:
                print(colored(log_string, level_color))

        if self.http_flag:
            if not log_level < self.min_level_http:
                if self.http_method == HttpMethod.GET and self.http_send_format == LogFormat.JSON:
                    raise ValueError("We can\'t send GET with body. Use json type only with POST http method")
                else:
                    if self.http_send_format == LogFormat.JSON:
                        http_send_string = log_json_string
                    elif self.http_send_format == LogFormat.TEXT:
                        http_send_string = log_string
                    else:
                        raise ValueError("Wrong http log format")

                    if self.http_method == HttpMethod.GET:
                        self.session.get(self.http_address + self.__get_params_maker(log_object))
                    elif self.http_method == HttpMethod.POST:
                        self.session.post(self.http_address, data=http_send_string)
                    else:
                        raise ValueError("Wrong http method")

        if self.file_flag:
            if not log_level < self.min_level_file:
                if self.file_rewrite_flag and os.path.exists(self.file_name) and not self.control_file_flag:
                    os.remove(self.file_name)
                if self.file_rewrite_flag:
                    self.control_file_flag = True

                if self.file_format == LogFormat.JSON:
                    file_string = log_json_string
                elif self.file_format == LogFormat.TEXT:
                    file_string = log_string
                else:
                    raise ValueError("Wrong http log format")

                file = open(self.file_name, "a+")
                file.write(file_string)
                file.close()

        if self.handler_flag:
            self.handler(log_object)

    def __get_params_maker(self, log_object):
        arr = []
        for key in log_object:
            arr.append(f'{key}={log_object[key]}')
        return "?"+"&".join(arr)

    def __get_level_string(self, log_level: LogLevel):
        if log_level == LogLevel.DEBUG:
            return "debug"
        elif log_level == LogLevel.TRACE:
            return "trace"
        elif log_level == LogLevel.INFO:
            return "info"
        elif log_level == LogLevel.WARN:
            return "warn"
        elif log_level == LogLevel.ERROR:
            return "error"
        elif log_level == LogLevel.FATAL:
            return "fatal"
        else:
            raise ValueError("Wrong log level")

    def __get_level_color(self, log_level: LogLevel):
        if log_level == LogLevel.DEBUG:
            return "cyan"
        elif log_level == LogLevel.TRACE:
            return "grey"
        elif log_level == LogLevel.INFO:
            return "magenta"
        elif log_level == LogLevel.WARN:
            return "yellow"
        elif log_level == LogLevel.ERROR:
            return "red"
        elif log_level == LogLevel.FATAL:
            return "red"
        else:
            raise ValueError("Wrong log level")


