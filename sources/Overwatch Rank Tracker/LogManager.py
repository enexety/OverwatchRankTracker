import logging
import requests
import io
import re
import json


class LogManager:

    # set logging
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s], %(levelname)s: %(message)s in %(name)s.py', datefmt='%Y-%m-%d, %H:%M:%S')
    logger = logging.getLogger(__name__)

    def __init__(self, owner_name, token):
        self.owner_name = owner_name
        self.token = token

        self.log_title = None
        self.log_text = None

    def __get_logs(self, error):
        """Captures and formats error logs and stores them for further use."""

        log_buffer = io.StringIO()
        handler = logging.StreamHandler(log_buffer)
        handler.setFormatter(logging.Formatter('[%(asctime)s], %(levelname)s: %(message)s in %(name)s.py', datefmt='%Y-%m-%d, %H:%M:%S'))
        LogManager.logger.addHandler(handler)
        LogManager.logger.error(f'{error}', exc_info=True)
        self.log_text = log_buffer.getvalue()
        self.log_title = self.log_text.split('\n')[0]

    def sending_logs(self, error, status_code, api_response):
        """Sends captured logs to a remote server for further analysis."""

        self.__get_logs(error=error)

        try:

            # content
            data = {"Date": re.search(r'\[(.*?)]', self.log_text).group(1), "File": re.search(r'\w+\.py', self.log_text).group(0), "Error": re.search(r': (.*?)(?= in)', self.log_text).group(1),
                    "Traceback": {'content': self.log_text.splitlines()[1:], 'type': 'text/plain'}, "Response status code": status_code, "Response content": {'content': api_response, 'type': 'application/json'}}

            # send logs
            requests.post("https://api.github.com/gists", auth=(self.owner_name, self.token), json={"description": self.log_title, "public": False, "files": {"content.json": {"content": json.dumps(data, indent=4)}}})

        # error handling
        except requests.exceptions.HTTPError:
            pass
