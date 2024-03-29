# Request object to handle http requests
import re
import os

class RequestParser:

    def __init__(self, raw_request):
        # make sure raw_request is a str
        if isinstance(raw_request, bytes):
            raw_request = raw_request.decode("utf-8")
        self.method = ""
        self.full_url = ""
        self.url = ""
        self.query_string = ""
        self.protocol = ""
        self.query_params = {}
        self.content = []
        self.post_data = {}
        
        self.parse_request(raw_request)

    def parse_request(self, raw_request):
        
        if len(raw_request) > 0:
            # Check end of line characters
            eol_char = '\r\n'  # Default as per HTTP protocol
            
            if raw_request.find('\r\n') == -1:
                eol_char = '\n' # Some systems may use single char newline
                
            # Split request into individual lines
            request_lines = raw_request.split(eol_char)

            # First line holds request verb, url and protocol
            self.parse_first_line(request_lines[0])
            
        else:
            return

    def parse_first_line(self, first_line):
        # Split up line at spaces to get words (should be into 3 parts)
        line_parts = first_line.split()
        
        if len(line_parts) == 3:
            self.method = line_parts[0]
            self.full_url = line_parts[1]
            
            # Try to split up full_url
            url_parts = line_parts[1].split('?', 1)
            self.url = url_parts[0]
            
            # Check for query string and decode if there
            if len(url_parts) > 1:
                self.query_string = url_parts[1]
                
                self.query_params = self.decode_query_string(self.query_string)
                
            self.protocol = line_parts[2]
            
        else:
            self.method = "ERROR" # Something is wrong!

    def decode_query_string(self, query_string):
        # Split query string on &, this gives key=value list
        param_strings = query_string.split('&')
        params = {}
        for param_string in param_strings:
            try:
                # Correctly formatted value splits into 2 on =
                key, value = param_string.split('=')
                
                # Values may be url encoded, decode special characters: replaces %20 with space, %0A with newline
                value = re.sub(r'%20', ' ', value)
                value = re.sub(r'%0A', '\n', value)

            except:
                # No value specified
                key = param_string
                value = False

            # save param in dictionary
            params[key] = value
        return params