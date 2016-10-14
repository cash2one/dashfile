#!/usr/bin/python
# vim: set fileencoding=gb2312

import sys

if len(sys.argv) > 1:
    f = open(sys.argv[1])
else:
    f = sys.stdin

table_data = []
col_count = -1
row_count = 0
for line in f.readlines():
    row = line.strip().split('\t')
    if col_count != -1 and len(row) != col_count:
        print >>sys.stderr, "invalid table data: diff column count"
        os.exit(1)
    table_data.append(row)
    col_count = len(row)
    row_count += 1

if row_count == 0:
    print >>sys.stderr, "invalid table data: no data"
    os.exit(1)

print "<table border=1>"
row_num = 0
for row in table_data:
    print "  <tr>"
    for i in range(0,col_count):
        print "    <td>%s</td>" % row[i]
    print "  </tr>"
    row_num += 1
print "</table>"

