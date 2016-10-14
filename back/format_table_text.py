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

column_size = []
for i in range(0,col_count):
    column_size.append(0)
for row in table_data:
    for i in range(0,col_count):
        if len(row[i]) > column_size[i]:
            column_size[i] = len(row[i])

total_size = col_count + 1
for i in range(0,col_count):
    total_size += column_size[i] + 2

print "="*total_size
row_num = 0
for row in table_data:
    print "|",
    for i in range(0,col_count):
        print ("%-"+str(column_size[i])+"s") % row[i],
        print "|",
    print
    if row_num == 0:
        print "="*total_size
    row_num += 1
print "="*total_size

