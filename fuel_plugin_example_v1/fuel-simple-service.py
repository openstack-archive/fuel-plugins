#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from wsgiref.simple_server import make_server

def web_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]

    start_response(status, headers)

    return open('/etc/astute.yaml').read()


def start_server(host, port):
    httpd = make_server(host, port, web_app)
    print 'Started server 8234'
    httpd.serve_forever()


def main():
    start_server('', 8234)


if __name__ == '__main__':
    main()
