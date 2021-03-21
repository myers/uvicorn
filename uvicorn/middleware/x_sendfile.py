"""
This middleware will look for request that have X-Sendfile header
and serve the file using with the zerocopysend ASGI extension.

This allows the python package django-sendfile2 to work with uvicorn.

https://tn123.org/mod_xsendfile/
https://asgi.readthedocs.io/en/latest/extensions.html#zero-copy-send
"""
from typing import List


# TODO: handle http range requests https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests

class XSendfileMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        async def send_wrapper(message):
            if message.get("type", "") == "http.response.start":
                for header in message.get("headers", []):
                    if header[0] == b"x-sendfile":
                        filepath = header[1]
                        message["headers"].remove(header)
                        await send(message)
                        with open(filepath, "rb") as file:
                            return await send(
                                {
                                    "type": "http.response.zerocopysend",
                                    "file": file
                                }
                            )
            return await send(message)

        return await self.app(scope, receive, send_wrapper)
