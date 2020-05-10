# Copyright [2018-2020] Peter Krenesky
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from typing import List, Dict, Union


# TODO: type hints for arg_groups and return
def merge_parser_args(
    parser: argparse.ArgumentParser, *arg_groups: Union[List[str]]
) -> Dict[str, str]:
    """
    Parse multiple arg lists with the same parser and merged them.

    :param parser:
    :param arg_groups:
    :return:
    """
    merged_options = {}
    for args in arg_groups:
        options, _ = parser.parse_known_args(args)
        merged_options.update({k: v for k, v in vars(options).items() if v is not None})
    return merged_options


def argunparse(options: dict, parser: argparse.ArgumentParser) -> List[str]:
    """
    Convert a dict of flags back into a list of args.
    """
    args = []
    for argument in parser.arguments:
        single_dash_name = next((arg for arg in argument["args"] if arg.startswith("-")), None)
        double_dash_name = next((arg for arg in argument["args"] if arg.startswith("--")), None)
        has_double_dash = bool(double_dash_name)
        flag_name = double_dash_name if has_double_dash else single_dash_name

        if "dest" in argument:
            value = options[argument["dest"]]
        else:
            for flag in argument["args"]:
                flag_stripped = flag.lstrip("-").replace("-", "_")
                if flag_stripped in options:
                    value = options[flag_stripped]
                    break
            else:
                value = None

        if value:
            # flags without values
            # TODO: doesn't handle flags that set a non-bool const value
            if isinstance(value, bool):
                as_args = [flag_name]

            # flags with values
            else:
                if has_double_dash and not argument.get("nargs", None):
                    arg_template = "{flag}={value}".format(flag=flag_name, value="{value}")
                else:
                    arg_template = "{flag} {value}".format(flag=flag_name, value="{value}")

                if not isinstance(value, list):
                    as_args = [arg_template.format(value=value)]
                else:
                    # for now assume separate flags per value e.g. "--foo bar --foo xoo"
                    # also need to support single flag with multiple values "--foo bar xoo"
                    as_args = [arg_template.format(value=v) for v in value]
            args.extend(as_args)

    return args
