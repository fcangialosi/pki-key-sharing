load 'style.gnu'

set grid
set logscale y

set xlabel "{/Helvetica-Bold Number of Distinct Certificates per Organization}"
set ylabel "{/Helvetica-Bold Frequency}"

set border 3
set xtics nomirror
set ytics nomirror

set format y "10^%T"
set format x "10^%T"
set logscale x

plot "../parse/out/certs-per-org.txt" u 2:1 w p linestyle 5 lw 2 pt 6 ps 0.8 title ""
