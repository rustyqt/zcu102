#!/usr/bin/python3

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher


@dispatcher.add_method
def echo(message):
    return message

@dispatcher.add_method
def mult(a, b):
    return a*b


@Request.application
def application(request):

    # JSON RPC Request Handler
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)

    # Print Request and Response
    print("--> " + str(request.data.decode()))
    print("<-- " + str(response.json))

    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, application)
