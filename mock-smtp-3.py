#!/usr/bin/python3

import sys
import os
import asyncio
import aiosmtpd.controller
from aiohttp import web
from aiojobs.aiohttp import setup
import logging
import time
import datetime
import email.utils
import platform

HOSTNAME = platform.node()

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

logging.basicConfig(stream=sys.stderr,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.DEBUG)

os.chdir(os.getenv('MOCK_SMTP_PATH', default='.'))

class SmtpHandler:
    def __init__(self):
        self.last_email = None

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'
    
    async def handle_DATA(self, server, session, envelope):
        print(f'Message from {envelope.mail_from}')
        print(f'Message for {envelope.rcpt_tos}')
        print('Message data:\n')
        for ln in envelope.content.decode('utf8', errors='replace').splitlines():
            print(f'> {ln}'.strip())
        print()
        print('End of message')

        today = time.time()
        rfc822_date = email.utils.formatdate(today, True)
        file = f'{datetime.datetime.fromtimestamp(today).strftime("%Y-%m-%dT%T.%f")}.eml'

        mailContent = []

        mailContent.append(f'Return-Path: <{envelope.mail_from}>')
        mailContent.append(f'Received: from [{session.peer}] by {HOSTNAME}')
        mailContent.append(f' (Mock SMTP -- https://github.com/mplattu/mock-smtp-3) with SMTP')
        mailContent.append(f' id {file}')
        mailContent.append(f' for <{envelope.rcpt_tos[0]}>; {rfc822_date}')

        for to in envelope.rcpt_tos:
            mailContent.append(f'Envelope-To: <{to}>')
        mailContent.append(f'Delivery-Date: {rfc822_date}')

        for ln in envelope.content.decode('utf8', errors='replace').splitlines():
            mailContent.append(ln)

        with open(file, "w") as mailFile:
            for line in mailContent:
                mailFile.write(f'{line}\n')

        self.last_email = "\n".join(mailContent)

        logging.info('%s => %s: %s', envelope.mail_from, envelope.rcpt_tos, file)

        return '250 Message accepted for delivery'
    
    def getLastEmail(self):
        if self.last_email is None:
            return "no last email"

        return self.last_email
    
    def waitLastEmail(self):
        while (self.last_email is None):
            time.sleep(1)
        
        return self.getLastEmail()

    def clearLastEmail(self):
        self.last_email = None

routes = web.RouteTableDef()

async def main():
    smtpHandler = SmtpHandler()

    smtpServer = aiosmtpd.controller.Controller(
        smtpHandler,
        hostname = os.getenv('MOCK_SMTP_ADDRESS', default='localhost'),
        port = os.getenv('MOCK_SMTP_PORT', default=25)
    )
    smtpServer.start()

    @routes.get('/')
    async def httpHandlerGetLastEmail(request):
        return web.Response(text=smtpHandler.getLastEmail())

    @routes.get('/wait')
    async def httpHandlerGetLastEmail(request):
        return web.Response(text=smtpHandler.waitLastEmail())

    @routes.get('/clear')
    async def httpHandlerClearLastEmail(request):
        smtpHandler.clearLastEmail()
        return web.Response(text="cleared")

    httpApp = web.Application()
    httpApp.add_routes(routes)
    httpRunner = web.AppRunner(httpApp)
    await httpRunner.setup()
    httpSite = web.TCPSite(
        httpRunner,
        host = os.getenv('MOCK_WEB_ADDRESS', default='localhost'),
        port = os.getenv('MOCK_WEB_PORT', default=8088)
    )
    await httpSite.start()

    while (True):
        await asyncio.sleep(3600)

    smtpServer.stop()
    await httpRunner.cleanup()

logging.info('Starting up Mock SMTP server')

if os.getuid() == 0:
    # Switch to UID/GID of owner of current path.
    stat = os.stat('.')
    os.setgroups([])

    os.setgid(stat.st_uid)
    os.setuid(stat.st_gid)
    os.umask(0o77)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('\nKeyboard interrupt\n')
    pass
