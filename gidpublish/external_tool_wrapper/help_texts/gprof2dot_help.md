# GPROF2DOT

```console
Usage: 
	gprof2dot [options] [file] ...

Options:
  -h, --help            show this help message and exit
  -o FILE, --output=FILE
                        output filename [stdout]
  -n PERCENTAGE, --node-thres=PERCENTAGE
                        eliminate nodes below this threshold [default: 0.5]
  -e PERCENTAGE, --edge-thres=PERCENTAGE
                        eliminate edges below this threshold [default: 0.1]
  -f FORMAT, --format=FORMAT
                        profile format: axe, callgrind, dtrace, hprof, json,
                        oprofile, perf, prof, pstats, sleepy, sysprof or xperf
                        [default: prof]
  --total=TOTALMETHOD   preferred method of calculating total time: callratios
                        or callstacks (currently affects only perf format)
                        [default: callratios]
  -c THEME, --colormap=THEME
                        color map: bw, color, gray, pink or print [default:
                        color]
  -s, --strip           strip function parameters, template parameters, and
                        const modifiers from demangled C++ function names
  --color-nodes-by-selftime
                        color nodes by self time, rather than by total time
                        (sum of self and descendants)
  -w, --wrap            wrap function names
  --show-samples        show function samples
  --node-label=MEASURE  measurements to on show the node (can be specified
                        multiple times): self-time, self-time-percentage,
                        total-time or total-time-percentage [default: total-
                        time-percentage, self-time-percentage]
  -z ROOT, --root=ROOT  prune call graph to show only descendants of specified
                        root function
  -l LEAF, --leaf=LEAF  prune call graph to show only ancestors of specified
                        leaf function
  --depth=DEPTH         prune call graph to show only descendants or ancestors
                        until specified depth
  --skew=THEME_SKEW     skew the colorization curve.  Values < 1.0 give more
                        variety to lower percentages.  Values > 1.0 give less
                        variety to lower percentages
  -p FILTER_PATHS, --path=FILTER_PATHS
                        Filter all modules not in a specified path

```