#!/usr/bin/python
# 
#
#
#
# Based on:
# dhcpd_leases_parser.py
#
# Copyright 2008, Paul McGuire
#
# Sample parser to parse a dhcpd.leases file to extract leases 
# and lease attributes
#
# format ref: http://www.linuxmanpages.com/man5/dhcpd.leases.5.php
#
from pyparsing import *
import sys
import datetime,time

def createParser():
  LBRACE,RBRACE,SEMI,QUOTE = map(Suppress,'{};"')
  ipAddress = Combine(Word(nums) + ('.' + Word(nums))*3)
  hexint = Word(hexnums,exact=2)
  macAddress = Combine(hexint + (':'+hexint)*5)
  hdwType = Word(alphanums)

  yyyymmdd = Combine((Word(nums,exact=4)|Word(nums,exact=2))+
                      ('/'+Word(nums,exact=2))*2)
  hhmmss = Combine(Word(nums,exact=2)+(':'+Word(nums,exact=2))*2)
  dateRef = oneOf(list("0123456"))("weekday") + yyyymmdd("date") + \
                                                          hhmmss("time")

  def utcToLocalTime(tokens):
      utctime = datetime.datetime.strptime("%(date)s %(time)s" % tokens,
                                                      "%Y/%m/%d %H:%M:%S")
      localtime = utctime-datetime.timedelta(0,time.timezone,0)
      tokens["utcdate"],tokens["utctime"] = tokens["date"],tokens["time"]
      tokens["localdate"],tokens["localtime"] = str(localtime).split()
      del tokens["date"]
      del tokens["time"]
  dateRef.setParseAction(utcToLocalTime)

  startsStmt = "starts" + dateRef + SEMI
  endsStmt = "ends" + (dateRef | "never") + SEMI
  tstpStmt = "tstp" + dateRef + SEMI
  tsfpStmt = "tsfp" + dateRef + SEMI
  clttStmt = "cltt" + dateRef + SEMI
  hdwStmt = "hardware" + hdwType("type") + macAddress("mac") + SEMI
  uidStmt = "uid" + QuotedString('"')("uid") + SEMI
  hostnameStmt = "client-hostname" + QuotedString('"')("hostname") + SEMI
  bindingStmt = "binding" + Word(alphanums) + Word(alphanums) + SEMI
  nextbindingStmt = "next binding" + Word(alphanums) + Word(alphanums) + SEMI

  leaseStatement = startsStmt | endsStmt | tstpStmt | clttStmt | tsfpStmt | hdwStmt | \
                   uidStmt | hostnameStmt | bindingStmt | nextbindingStmt
  leaseDef = "lease" + ipAddress("ipaddress") + LBRACE + \
                              Dict(ZeroOrMore(Group(leaseStatement))) + RBRACE
  return leaseDef


hosts = {}
domain = sys.argv[1] + '.'
leaseDef = createParser()
for lease in leaseDef.searchString(file('/var/lib/dhcp3/dhcpd.leases').read()):
    if not 'client-hostname' in lease.keys(): continue
    if not lease.binding[1] == 'active': continue
    hosts[lease["client-hostname"]] = lease.ipaddress

print '; AUTO-GENERATED'
print domain + ' IN SOA ns-local.'+domain+' hostmaster.'+domain+' (1 300 300 300 300)'
for host in hosts.keys():
    print host+'.'+domain,' 1200 IN A ',hosts[host]
    octets = hosts[host].split('.')
    print '%s.%s.%s.%s.in-addr.arpa. 1200 IN PTR %s.%s' % (octets[3], octets[2], octets[1], octets[0], host, domain)

