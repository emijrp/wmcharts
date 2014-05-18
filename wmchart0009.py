# -*- coding: utf-8 -*-

# Copyright (C) 2011-2014 emijrp <emijrp@gmail.com>
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

from wmchart0000 import *

def main():
    filename = 'wmchart0009.php'
    title = 'WikiLove'
    description = "This chart shows how many WikiLove messages were sent in the last days."

    projectdbs = getProjectDatabases(lang='en', family='wikipedia')

    wikilove = '(new [Ww]ikiLove message)'
    warnings = '([Ww]arning)'
    welcomes = '([Ww]elcome)'
    queries = [
        ["Total user talk edits", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges WHERE rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1 AND rc_namespace=3 GROUP BY date ORDER BY date ASC" % (lastdays)],
        ["WikiLove messages", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges WHERE rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1 AND rc_namespace=3 AND rc_comment rlike '%s' GROUP BY date ORDER BY date ASC" % (lastdays, wikilove)],
        ["Warnings", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges WHERE rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1 AND rc_namespace=3 AND rc_comment rlike '%s' GROUP BY date ORDER BY date ASC" % (lastdays, warnings)],
        ["Welcomes", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges WHERE rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1 AND rc_namespace=3 AND rc_comment rlike '%s' GROUP BY date ORDER BY date ASC" % (lastdays, welcomes)],
        
    ]
    projects = runQueries(projectdbs=projectdbs, queries=queries)
    select = generateHTMLSelect(projects)

    var1 = []
    var2 = []
    var3 = []
    var4 = []
    varother = []
    for project, values in projects:
        var1.append(values["Total user talk edits"])
        var2.append(values["WikiLove messages"])
        var3.append(values["Warnings"])
        var4.append(values["Welcomes"])

    js = """function p() {
        var d1 = %s;
        var d2 = %s;
        var d3 = %s;
        var d4 = %s;
        var placeholder = $("#placeholder");
        var selected = document.getElementById('projects').selectedIndex;
        var data = [{ data: d1[selected], label: "Total user talk edits"}, { data: d2[selected], label: "WikiLove messages"}, { data: d3[selected], label: "Warnings"}, { data: d4[selected], label: "Welcomes"}];
        var options = { xaxis: { mode: "time" }, lines: {show: true}, points: {show: true}, legend: {noColumns: 4}, grid: { hoverable: true }, };
        $.plot(placeholder, data, options);
    }
    p();""" % (str(var1), str(var2), str(var3), str(var4))

    output = generateHTML(title=title, description=description, select=select, js=js)
    writeHTML(filename=filename, output=output)

if __name__ == '__main__':
    main()
