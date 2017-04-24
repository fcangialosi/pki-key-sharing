load 'style.gnu'

set border 3
set xtics nomirror
set ytics nomirror
set grid

set key bottom right

set xlabel "{/Helvetica-Bold Number of Hosting Providers Compromised}"
set ylabel "{/Helvetica-Bold Cumulative Fraction of\n}{/Helvetica-Bold Domains' Keys Acquired}"

set logscale x
set format x "10^%T"
set yrange[0:*]

set datafile separator "\t"

plot '../parse/out/top-1k-compromise.tsv' u ($0+1):4 w st linestyle 1 ti 'Alexa Top 1k',\
'../parse/out/top-1m-compromise.tsv' u ($0+1):4 w st linestyle 2 ti 'Alexa Top 1m',\
'../parse/out/top-all-compromise.tsv' u ($0+1):4 w st linestyle 3 ti 'All Domains'
