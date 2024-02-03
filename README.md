# Mock SMTP 3

_Mock SMTP 3_ is a SMTP server that does not deliver message, instead it save
the messages to files in your file system. It can also show the latest received
email by the internal web server making it a perfect companion for Playwright
testing.

This is a development tool, used to test email sending from apps.

The concept and code are heavily influenced by (read: almost a verbatim copy of) 
[flaviovs/mock-smtp](https://github.com/flaviovs/mock-smtp) with following
chamges
 - Upgraded to Python 3
 - The last email can be accessed via the web server

# How to Run via Command Line

Activate virtual environment, install requirements and execute the script:

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
# python mock-smtp-3.py
``````

By default the SMTP server will listen on port 25, and bind to `localhost`, plus
e-mails will be saved to the current directory. The httpd server listens port 8088,
and binds to `localhost`.

This behaviour can be changed by using the following environment variables, respectively:

 - `MOCK_SMTP_ADDRESS`
 - `MOCK_SMTP_PORT`
 - `MOCK_SMTP_PATH`
 - `MOCK_WEB_ADDRESS`
 - `MOCK_WEB_PORT`

**Note**: _Mock SMTP_ must be run as root for binding to ports below 1024,
otherwise you will get a _PermissionError_ exception. When run as root, the
daemon will drop privileges, and assume the same identify of the owner/group
of current directory or (the one specified in `MOCK_SMTP_PATH`), after the
SMTP socket is open.

# How to Run via Docker

```
$ mkdir emails
$ docker run --rm -p 25:25 -p 8088:8088 -v $(pwd)/emails:/var/lib/mock-smtp-3 -d mplattu/mock-smtp-3
$ telnet localhost 25
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
220 f58055922887 Python SMTP 1.4.4.post2
[after escaping and quitting telnet]
$ wget -q -O - http://localhost:8088
none
```

# Issues?

Visit https://github.com/mplattu/mock-smtp-3

# Acknowledgements

Thanks for [Flávio Veloso Soares](https://github.com/flaviovs) for an inspiring example.
