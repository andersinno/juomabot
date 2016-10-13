import os

if __name__ == '__main__':
    os.environ.setdefault(
        'DATABASE_URL',
        'sqlite:///%s/juomabot.sqlite3' % os.path.realpath(os.path.dirname(__file__))
    )
    print('*' * 80)
    print('DATABASE_URL: %s' % os.environ['DATABASE_URL'])
    print('*' * 80)
    from juomabot.wsgi import application
    application.run(debug=True, port=45032)
