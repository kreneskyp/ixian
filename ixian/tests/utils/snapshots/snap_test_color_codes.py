# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from pysnap import Snapshot


snapshots = Snapshot()

snapshots['TestColorCodes.test_colors[color4] GRAY'] = '\x1b[90mtesting\x1b[0m'

snapshots['TestColorCodes.test_color_methods[red] 1'] = '\x1b[91mtesting\x1b[0m'

snapshots['TestColorCodes.test_color_methods[green] 1'] = '\x1b[92mtesting\x1b[0m'

snapshots['TestColorCodes.test_color_methods[yellow] 1'] = '\x1b[93mtesting\x1b[0m'

snapshots['TestColorCodes.test_color_methods[gray] 1'] = '\x1b[90mtesting\x1b[0m'

snapshots['TestColorCodes.test_color_methods[bold_white] 1'] = '\x1b[1mtesting\x1b[0m'

snapshots['TestColorCodes.test_colors[color0] BOLD_WHITE'] = '\x1b[1mtesting\x1b[0m'

snapshots['TestColorCodes.test_colors[color1] RED'] = '\x1b[91mtesting\x1b[0m'

snapshots['TestColorCodes.test_colors[color2] OK_GREEN'] = '\x1b[92mtesting\x1b[0m'

snapshots['TestColorCodes.test_colors[color3] YELLOW'] = '\x1b[93mtesting\x1b[0m'
