# VPROF

```console
usage: vprof [-h] (-r | -i INPUT_FILE | -c CONFIG SRC) [-H HOST] [-p PORT]
             [-n] [-o OUTPUT_FILE] [--debug] [--version]

Visual profiler for Python

optional arguments:
  -h, --help            show this help message and exit
  -r, --remote          launch in remote mode
  -i INPUT_FILE, --input-file INPUT_FILE
                        render UI from file
  -c CONFIG SRC, --config CONFIG SRC
                        profile program SRC with configuration CONFIG
                        available CONFIG options
                          c - flame graph
                          m - memory graph
                          h - code heatmap
  -H HOST, --host HOST  set internal webserver host
  -p PORT, --port PORT  set internal webserver port
  -n, --no-browser      don't start browser automatically
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        save profile to file
  --debug               don't suppress error messages
  --version             show program's version number and exit

```