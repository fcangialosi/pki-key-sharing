load 'style.gnu'

set border 3
set xtics nomirror
set ytics nomirror
set grid

set xlabel "{/Helvetica-Bold Rank-Order Third-Party Hosting Providers}"
set ylabel "{/Helvetica-Bold Number of Distinct\n}{/Helvetica-Bold Customers Served}"

set logscale x
set logscale y
set format y "10^%T"
set format x "10^%T"
set datafile separator "\t"


plot '../parse/out/orgs-per-host.txt' u ($0+1):2 w st linestyle 5 notitle, \
     '< head -n1 ../parse/out/orgs-per-host.txt' u ($0+1):2 w p linestyle 5 lw 1 ps 1.5 pt 6 notitle, \
    '< tail -n1 ../parse/out/orgs-per-host.txt' u (352834):(1) w p linestyle 5 lw 1 ps 1.5 pt 6 notitle
