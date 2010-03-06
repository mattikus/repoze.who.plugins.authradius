===========
 whoradius
===========

Plugin for repoze.who that queries RADIUS backend for authentication.

There are plenty of ISP and enterprise-level RADIUS servers, and their
number seems to be increasing as the demand for centralized
authentication of WiFi access points grows.

My motivation in writing this was to allow WSGI apps to authenticate
against our RSA SecurID token based authentication service which is
accessible thorugh a RADIUS interface, in addition to it's painful
native mechanism.  

Popular RADIUS servers include FreeRADIUS, GNU RADIUS, and the
venerable Cistron; I prefer FreeRADIUS these days.  Commercial servers
include Radiator and the delightfully named Steel Belted RADIUS
server.

Non-functionality
=================

It doesn't do anything with RADIUS accounting.

In order to avoid the need for full RADIUS dictionary -- which maps
protocol attribute numbers to names -- we define locally only the
minimum we need for authentication.  I've not been able to parse with
pyrad dictionaries from FreeRADIUS-1.7, FreeRADIUS-2.0.3, GNU RADIUS,
or Cistron RADIUS, but was able to parse one from an old version I had
deployed elsewhere, perhaps FreeRADIUS-1.6 or earlier.

Lack of dictionary means we can't decode reply packets, which might
provide useful information for subsequent functionality.
