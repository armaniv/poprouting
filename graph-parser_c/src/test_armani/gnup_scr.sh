#set yrange [-0.1:1]
set xrange [-0.3:*]
plot 'Brandes.dat' ps 3 pointtype 4, 'Euristica modif.dat' ps 3 pointtype 1, 'Cut_point.dat' ps 3 pointtype 2
pause -1 "Click to continue"
