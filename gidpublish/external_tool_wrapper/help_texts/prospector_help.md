# PROSPECTOR

```console
usage: prospector [-h] [-0] [-A] [-u USES] [-B] [-D] [-T] [-8] [-m] [-F]
                  [--max-line-length MAX_LINE_LENGTH] [-M] [-S]
                  [-o OUTPUT_FORMAT] [--absolute-paths] [-t TOOLS]
                  [-w WITH_TOOLS] [-W WITHOUT_TOOLS] [-P PROFILES]
                  [--profile-path PROFILE_PATH]
                  [-s {veryhigh,high,medium,low,verylow}] [--show-profile]
                  [-E] [--pylint-config-file PYLINT_CONFIG_FILE] [-p PATH]
                  [-I IGNORE_PATTERNS] [-i IGNORE_PATHS] [-X]
                  [--include-tool-stdout] [--direct-tool-stdout] [--version]
                  [PATH ...]

Performs static analysis of Python code

positional arguments:
  PATH                  The path to a Python project to inspect. Defaults to
                        PWD if not specified. If multiple paths are specified,
                        they must all be files (no directories).

optional arguments:
  -h, --help            show this help message and exit
  -0, --zero-exit       Prospector will exit with a code of 1 (one) if any
                        messages are found. This makes automation easier; if
                        there are any problems at all, the exit code is non-
                        zero. However this behaviour is not always desirable,
                        so if this flag is set, prospector will exit with a
                        code of 0 if it ran successfully, and non-zero if it
                        failed to run.
  -A, --no-autodetect   Turn off auto-detection of frameworks and libraries
                        used. By default, autodetection will be used. To
                        specify manually, see the --uses option.
  -u USES, --uses USES  A list of one or more libraries or frameworks that the
                        project uses. Possible values are: django, celery,
                        flask. This will be autodetected by default, but if
                        autodetection doesn't work, manually specify them
                        using this flag.
  -B, --no-blending     Turn off blending of messages. Prospector will merge
                        together messages from different tools if they
                        represent the same error. Use this option to see all
                        unmerged messages.
  -D, --doc-warnings    Include warnings about documentation.
  -T, --test-warnings   Also check test modules and packages.
  -8, --no-style-warnings
                        Don't create any warnings about style. This disables
                        the PEP8 tool and similar checks for formatting.
  -m, --member-warnings
                        Attempt to warn when code tries to access an attribute
                        of a class or member of a module which does not exist.
                        This is disabled by default as it tends to be quite
                        inaccurate.
  -F, --full-pep8       Enables every PEP8 warning, so that all PEP8 style
                        violations will be reported.
  --max-line-length MAX_LINE_LENGTH
                        The maximum line length allowed. This will be set by
                        the strictness if no value is explicitly specified
  -M, --messages-only   Only output message information (don't output summary
                        information about the checks)
  -S, --summary-only    Only output summary information about the checks
                        (don'toutput message information)
  -o OUTPUT_FORMAT, --output-format OUTPUT_FORMAT
                        The output format. Valid values are: emacs, grouped,
                        json, pylint, text, vscode, xunit, yaml. This will
                        output to stdout by default, however a target file can
                        be used instead by adding :path-to-output-file, eg, -o
                        json:output.json
  --absolute-paths      Whether to output absolute paths when referencing
                        files in messages. By default, paths will be relative
                        to the project path
  -t TOOLS, --tool TOOLS
                        A list of tools to run. This lets you set exactly
                        which tools to run. To add extra tools to the
                        defaults, see --with-tool. Possible values are:
                        bandit, dodgy, frosted, mccabe, mypy, pep257, pep8,
                        profile-validator, pyflakes, pylint, pyroma, vulture.
                        By default, the following tools will be run: dodgy,
                        mccabe, pep257, pep8, profile-validator, pyflakes,
                        pylint
  -w WITH_TOOLS, --with-tool WITH_TOOLS
                        A list of tools to run in addition to the default
                        tools. To specify all tools explicitly, use the --tool
                        argument. Possible values are bandit, dodgy, frosted,
                        mccabe, mypy, pep257, pep8, profile-validator,
                        pyflakes, pylint, pyroma, vulture.
  -W WITHOUT_TOOLS, --without-tool WITHOUT_TOOLS
                        A list of tools that should not be run. Useful to turn
                        off only a single tool from the defaults. To specify
                        all tools explicitly, use the --tool argument.
                        Possible values are bandit, dodgy, frosted, mccabe,
                        mypy, pep257, pep8, profile-validator, pyflakes,
                        pylint, pyroma, vulture.
  -P PROFILES, --profile PROFILES
                        The list of profiles to load. A profile is a certain
                        'type' of behaviour for prospector, and is represented
                        by a YAML configuration file. Either a full path to
                        the YAML file describing the profile must be provided,
                        or it must be on the profile path (see --profile-path)
  --profile-path PROFILE_PATH
                        Additional paths to search for profile files. By
                        default this is the path that prospector will check,
                        and a directory called ".prospector" in the path that
                        prospector will check.
  -s {veryhigh,high,medium,low,verylow}, --strictness {veryhigh,high,medium,low,verylow}
                        How strict the checker should be. This affects how
                        harshly the checker will enforce coding guidelines.
                        The default value is "medium", possible values are
                        "veryhigh", "high", "medium", "low" and "verylow".
  --show-profile        Include the computed profile in the summary. This will
                        show what prospector has decided the overall profile
                        is once all profiles have been combined and inherited
                        from. This will produce a large output in most cases
                        so is only useful when trying to debug why prospector
                        is not behaving like you expect.
  -E, --no-external-config
                        Determines how prospector should behave when
                        configuration already exists for a tool. By default,
                        prospector will use existing configuration. This flag
                        will cause prospector to ignore existing configuration
                        and use its own settings for every tool. Note that
                        prospector will always use its own config for tools
                        which do not have custom configuration.
  --pylint-config-file PYLINT_CONFIG_FILE
                        The path to a pylintrc file to use to configure
                        pylint. Prospector will find .pylintrc files in the
                        root of the project, but you can use this option to
                        specify manually where it is.
  -p PATH, --path PATH  The path to a Python project to inspect. Defaults to
                        PWD if not specified. Note: This command line argument
                        is deprecated and will be removed in a future update.
                        Please use the positional PATH argument instead.
  -I IGNORE_PATTERNS, --ignore-patterns IGNORE_PATTERNS
                        A list of paths to ignore, as a list of regular
                        expressions. Files and folders will be ignored if
                        their full path contains any of these patterns.
  -i IGNORE_PATHS, --ignore-paths IGNORE_PATHS
                        A list of file or directory names to ignore. If the
                        complete name matches any of the items in this list,
                        the file or directory (and all subdirectories) will be
                        ignored.
  -X, --die-on-tool-error
                        If a tool fails to run, prospector will try to carry
                        on. Use this flag to cause prospector to die and raise
                        the exception the tool generated. Mostly useful for
                        development on prospector.
  --include-tool-stdout
  --direct-tool-stdout
  --version             show program's version number and exit

```