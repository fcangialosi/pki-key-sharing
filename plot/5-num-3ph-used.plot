load 'style.gnu'

set border 3
set xtics nomirror
set ytics nomirror
set grid

set xlabel "{/Helvetica-Bold Number of Third-Party Hosting Providers Used}"
set ylabel "{/Helvetica-Bold CDF}"

set yrange [0:*]
set logscale x 
set xrange [0.1:100000]
set xtics ("0" 0.1, "1" 1, "10" 10, "10^2" 100, "10^3" 1000, "10^4" 10000, "10^5" 100000)
set key bottom right

plot '< sort -nk1 ../parse/out/3ph-by-domain.txt' u 1:3 w st linestyle 1 lw 5 ti 'Domains',\
'< sort -nk1 ../parse/out/3ph-by-company.txt' u 1:3 w st linestyle 2 lw 2 ti 'Organizations'
