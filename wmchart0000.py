# -*- coding: utf-8 -*-

# Copyright (C) 2014 emijrp <emijrp@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import MySQLdb
import os
import time

families = ["wikibooks", "wikipedia", "wiktionary", "wikimedia", "wikiquote", "wikisource", "wikinews", "wikiversity", "commons", "wikispecies"]
lastdays = 22 #3 weeks

def convert2unix(mwtimestamp):
    #2010-12-25T12:12:12Z
    [year, month, day] = [int(mwtimestamp[0:4]), int(mwtimestamp[5:7]), int(mwtimestamp[8:10])]
    [hour, minute, second] = [int(mwtimestamp[11:13]), int(mwtimestamp[14:16]), int(mwtimestamp[17:19])]
    d = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    return int((time.mktime(d.timetuple())+1e-6*d.microsecond)*1000)

def connectDB(dbserver, dbname):
    return MySQLdb.connect(host=dbserver, db=dbname, read_default_file='~/replica.my.cnf', use_unicode=True)

def createCursor(conn):
    return conn.cursor()

def getProjectDatabases(lang='', family=''):
    conn = connectDB(dbserver='s3.labsdb', dbname='meta_p')
    cursor = createCursor(conn=conn)
    if lang and family:
        cursor.execute("SELECT lang, family, slice, dbname FROM wiki WHERE lang='%s' AND family='%s';" % (lang, family))
    elif lang:
        cursor.execute("SELECT lang, family, slice, dbname FROM wiki WHERE lang='%s';" % (lang))
    elif family:
        cursor.execute("SELECT lang, family, slice, dbname FROM wiki WHERE family='%s';" % (family))
    else:
        cursor.execute("SELECT lang, family, slice, dbname FROM wiki WHERE 1;")
    result = cursor.fetchall()
    projectdbs = []
    for row in result:
        projectdbs.append([row[0], row[1], row[2], row[3]+'_p'])
    cursor.close()
    conn.close()
    return projectdbs

def runQueries(projectdbs, queries):
    projects = {}
    for lang, family, dbserver, dbname in projectdbs:
        time.sleep(0.1)
        if family not in families:
            continue
        
        try:
            conn = connectDB(dbserver=dbserver, dbname=dbname)
            cursor = createCursor(conn=conn)
            projects[dbname] = {}
            for queryname, query in queries:
                projects[dbname][queryname] = []
                cursor.execute(query)
                result = cursor.fetchall()
                for row in result:
                    timestamp = '%d' % convert2unix(row[0]) # '%d' to avoid L of long when str()
                    value = '%d' % int(row[1])
                    #print timestamp, edits
                    projects[dbname][queryname].append([timestamp, value])
                projects[dbname][queryname] = projects[dbname][queryname][1:] #trip first, it is incomplete
            cursor.close()
            conn.close()
            print "OK:", dbserver, dbname
        except:
            print "Error in", dbserver, dbname
        
    projects_list = [[k, v] for k, v in projects.items()] # order
    projects_list.sort()
    return projects_list

def generateHTMLSelect(projects=[]):
    c = 0
    select = ""
    selecteddone = False
    if projects:
        for project, values in projects:
            if project == 'enwiki_p' or project == 'all':
                if not selecteddone:
                    select += '<option value="%d" selected>%s</option>' % (c, project)
                    selecteddone = True
            else:
                select += '<option value="%d">%s</option>' % (c, project)
            c += 1
    else:
        select += '<option value="%d" selected>All</option>' % (c)
    return select

def generateHTML(title, description, select, js):
    return """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
 <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>wmcharts - %s</title>
    <link href="style.css" rel="stylesheet" type="text/css"></link>
    <!--[if IE]><script language="javascript" type="text/javascript" src="lib/flot/excanvas.min.js"></script><![endif]-->
    <script language="javascript" type="text/javascript" src="lib/flot/jquery.js"></script>
    <script language="javascript" type="text/javascript" src="lib/flot/jquery.flot.js"></script>
 </head>
    <body>
    <!-- start content -->
    <h1><a href="https://wikitech.wikimedia.org/wiki/User:Emijrp">emijrp's tools</a></h1>
    <hr/>
    <h2><a href="http://tools.wmflabs.org/wmcharts/">wmcharts</a> - %s</h2>
    
    <div id="placeholder" style="width:800px;height:350px;"></div>

    <p>%s</p>
    
    <p>Choose a project: <select id="projects" onChange="p()">%s</select></p>

<script id="source">
%s

//from http://people.iola.dk/olau/flot/examples/interacting.html
function showTooltip(x, y, contents) {
    $('<div id="tooltip">' + contents + '</div>').css( {
        position: 'absolute',
        display: 'none',
        top: y + 5,
        left: x + 12,
        border: '1px solid #fdd',
        padding: '2px',
        'background-color': '#fee',
        opacity: 0.80
    }).appendTo("body").fadeIn(200);
}

var previousPoint = null;
$("#placeholder").bind("plothover", function (event, pos, item) {
    $("#x").text(pos.x.toFixed(2));
    $("#y").text(pos.y.toFixed(2));
    
    if (item) {
        if (previousPoint != item.datapoint) {
            previousPoint = item.datapoint;
            
            $("#tooltip").remove();
            var x = item.datapoint[0].toFixed(2),
                y = item.datapoint[1].toFixed(2);
            
            showTooltip(item.pageX, item.pageY,
                        "y = "+Math.round(y));
        }
    } else {
        $("#tooltip").remove();
        previousPoint = null;            
    }
});
</script>

<hr/>
<p><i>This page was last modified on <!-- timestamp -->%s<!-- /timestamp --> (UTC).</i></p>
<!-- end content -->
</body>
</html>
""" % (title, title, description, select and select or "", js, datetime.datetime.now())

def writeHTML(filename, output):
    f = open(os.path.expanduser('~/public_html/%s' % (filename)), 'w')
    f.write(output)
    f.close()
