import cgi

from google.appengine.api import users
from urlparse import urlparse

from sets import Set

from google.appengine.ext import ndb

import json
import random

import webapp2

def decode(s):
  vector = s.split("&")

  params = {}

  for v in vector:
    aux = v.split("=")
    params[aux[0]] = aux[1]

  return params

class Route(ndb.Model):
  id_remote = ndb.StringProperty()
  endpoint_address = ndb.StringProperty()

  def _pre_put_hook(self):
    routes = Route.query(Route.id_remote==self.id_remote, Route.endpoint_address==self.endpoint_address).fetch()

    for route in routes:
      route.key.delete()


class Lookup:
  def __init__(self):
    self.remote_objects = {}

  def register_remote_object(self, id, endpoint):
    st = id + endpoint
    route = Route(id_remote=id, endpoint_address=endpoint)

    route.put()

    return 200, "Object " + id + " registered at endpoint " + endpoint

  def servers_by_remote_object(self, id):
    routes = Route.query(Route.id_remote==id).fetch()

    result = []

    for v in routes:
      result.append(str(v.endpoint_address))

    return 200, str(result).replace("'", "\"")

  def get_server(self, id):
    routes = Route.query(Route.id_remote==id).fetch()

    if len(routes) == 0:
      return 404, '"%s"' % "Not found"

    route = random.choice(routes)

    return 200, '"%s"' % route.endpoint_address


class MainPage(webapp2.RequestHandler):
  def __init__(self, request, response):
    self.initialize(request, response)
    self.lookup = Lookup()

  def get(self):
    status = 404
    body = ""

    if self.request.path == "/objects/get_server":
      query = decode(self.request.query)
      status, body = self.lookup.get_server(query['id'])
    elif self.request.path == "/objects/get_servers":
      query = decode(self.request.query)
      status, body = self.lookup.servers_by_remote_object(query['id'])

    self.response.set_status(status)
    self.response.write(body)

  def post(self):
    status = 404
    body = ""

    if self.request.path == "/objects/add":
      hsh = decode(self.request.body)
      status, body = self.lookup.register_remote_object(hsh['id'], hsh['endpoint'])

    self.response.set_status(status)
    self.response.write(body)

application = webapp2.WSGIApplication([
    ('/objects/all', MainPage),
    ('/objects/get_server', MainPage),
    ('/objects/get_servers', MainPage),
    ('/objects/add', MainPage)
], debug=True)