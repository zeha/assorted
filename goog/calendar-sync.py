#!/usr/bin/env python2.6
import gdata, gdata.gauth, gdata.calendar, gdata.calendar.client, gdata.calendar.service
import atom.data
import json
import sys, os

config = {'user': '', 'password': '', 'source': 'default', 'dest': ''}
configfile = os.path.expanduser('~/.calendar-sync.json')
try:
    config = json.load(file(configfile,'r'))
except:
    print "E: Could not read config file %s - writing defaults to %s and exiting." % (configfile, configfile+'.new')
    json.dump(config, file(configfile+'.new','w'))
    sys.exit(1)

client = gdata.calendar.client.CalendarClient(source='at.zeha.google-cal-sync-v0-github')
client.ClientLogin(config['user'], config['password'], source=client.source)

cal_source = client.GetCalendarEventFeedUri(calendar=config['source'])
cal_dest = client.GetCalendarEventFeedUri(calendar=config['dest'])

print 'Syncing from %s to %s' % (cal_source, cal_dest)

feed = client.GetCalendarEventFeed(uri=cal_source)
for i, source_event in enumerate(feed.entry):
    if len(source_event.when) == 0:
        print '* [%s] "%s" Skipping, empty when list' % (i, source_event.title.text)
        continue
    when = source_event.when[0]
    print '* [%s] "%s" from %s to %s' % (i, source_event.title.text, when.start, when.end)
    event_ref = 'ref=%s' % source_event.id.text.split('/events/')[1]
    query = gdata.calendar.client.CalendarEventQuery(text_query='"%s"' % event_ref)
    queriedfeed = client.GetCalendarEventFeed(uri=cal_dest, q=query)
    found_dest_event = False
    for i, event in enumerate(queriedfeed.entry):
        print '\t* "%s" from %s to %s' % (event.title.text, event.when[0].start, event.when[0].end,)
        if event.when[0].start != source_event.when[0].start or event.when[0].end != source_event.when[0].end:
            event.when = source_event.when
            print '\tSyncing times'
            client.Update(event)
        found_dest_event = True
        break
    if not found_dest_event:
        event = gdata.calendar.data.CalendarEventEntry()
        event.title = atom.data.Title(text="Away [synced]")
        event.content = atom.data.Content(text=event_ref)
        event.when = source_event.when
        new_event = client.InsertEvent(event, insert_uri=cal_dest)
        print '\tNew event inserted: %s' % (new_event.GetHtmlLink().href,)


