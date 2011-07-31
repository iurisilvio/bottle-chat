#!/usr/bin/python
import uuid
import inspect

from gevent import monkey; monkey.patch_all()
from gevent.event import Event
from beaker.middleware import SessionMiddleware
import bottle
from bottle import route, request, static_file, template

cache_size = 200
cache = []
new_message_event = Event()

class BeakerPlugin(object):
    name = 'beaker'

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, BeakerPlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another beaker session plugin "\
                "with conflicting settings (non-unique keyword).")

    def apply(self, callback, context):
        args = inspect.getargspec(context['callback'])[0]
        keyword = 'session'
        if keyword not in args:
            return callback
        def wrapper(*a, **ka):
            session = request.environ.get('beaker.session')
            ka[keyword] = session
            rv = callback(*a, **ka)
            session.save()
            return rv
        return wrapper


@route("/",template='index')
def main(session):
    global cache
    if cache:
        session['cursor'] = cache[-1]['id']
    return {'messages': cache}

@route('/a/message/new', method='POST')
def message_new():
    global cache
    global cache_size
    global new_message_event
    name = request.environ.get('REMOTE_ADDR') or 'Anonymous'
    forwarded_for = request.environ.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for and name == '127.0.0.1':
        name = forwarded_for
    msg = create_message(name, request.POST.get('body'))
    cache.append(msg)
    if len(cache) > cache_size:
        cache = cache[-cache_size:]
    new_message_event.set()
    new_message_event.clear()
    return msg

@route('/a/message/updates', method='POST')
def message_updates(session):
    global cache
    global new_message_event
    cursor = session.get('cursor')
    if not cache or cursor == cache[-1]['id']:
         new_message_event.wait()
    assert cursor != cache[-1]['id'], cursor
    try:
        for index, m in enumerate(cache):
           if m['id'] == cursor:
               return {'messages': cache[index + 1:]}
        return {'messages': cache}
    finally:
        if cache:
            session['cursor'] = cache[-1]['id']
        else:
            session.pop('cursor', None)

@route('/static/:filename', name='static')
def static_files(filename):
    return static_file(filename, root='./static/')

def create_message(from_, body):
    data = {'id': str(uuid.uuid4()), 'from': from_, 'body': body}
    data['html'] = template('message', message=data)
    return data


app = bottle.app()
app.install(BeakerPlugin())

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(app, session_opts)


if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(app=app, server='gevent')