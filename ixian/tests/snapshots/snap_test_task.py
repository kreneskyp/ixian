# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from pysnap import Snapshot


snapshots = Snapshot()

snapshots['TestTaskTree.test_tree[nested_single_dependency_nodes] 1'] = {
    'dependencies': [
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild'
                }
            ],
            'name': 'child'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree[single_dependency_node_at_end_of_branch_1] 1'] = {
    'dependencies': [
        {
            'dependencies': [
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1'
                }
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree[single_dependency_node_at_end_of_branch_2] 1'] = {
    'dependencies': [
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1'
                }
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree[single_dependency_in_middle_of_branch] 1'] = {
    'dependencies': [
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1'
                },
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2'
                }
            ],
            'name': 'child_A'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree[nested_multiple_dependency_nodes] 1'] = {
    'dependencies': [
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1'
                },
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2'
                }
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1'
                },
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_B2'
                }
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree[common_dependency] 1'] = {
    'dependencies': [
        {
            'dependencies': [
            ],
            'name': 'common_setup'
        },
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'common_setup'
                },
                {
                    'dependencies': [
                        {
                            'dependencies': [
                            ],
                            'name': 'common_setup'
                        }
                    ],
                    'name': 'grandchild_B1'
                }
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'common_setup'
                }
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree_deduped[nested_single_dependency_nodes] 1'] = {
    'dependencies': [
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild'
                }
            ],
            'name': 'child'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree_deduped[single_dependency_node_at_end_of_branch_1] 1'] = {
    'dependencies': [
        {
            'dependencies': [
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1'
                }
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree_deduped[single_dependency_node_at_end_of_branch_2] 1'] = {
    'dependencies': [
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1'
                }
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree_deduped[single_dependency_in_middle_of_branch] 1'] = {
    'dependencies': [
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1'
                },
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2'
                }
            ],
            'name': 'child_A'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree_deduped[nested_multiple_dependency_nodes] 1'] = {
    'dependencies': [
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1'
                },
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2'
                }
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1'
                },
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_B2'
                }
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree_deduped[common_dependency] 1'] = {
    'dependencies': [
        {
            'dependencies': [
            ],
            'name': 'common_setup'
        },
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1'
                }
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree_flattened[nested_single_dependency_nodes] 1'] = {
    'dependencies': [
        {
            'dependencies': [
            ],
            'name': 'grandchild'
        },
        {
            'dependencies': [
            ],
            'name': 'child'
        },
        {
            'dependencies': [
            ],
            'name': 'root'
        }
    ],
    'name': None
}

snapshots['TestTaskTree.test_tree_flattened[single_dependency_node_at_end_of_branch_1] 1'] = {
    'dependencies': [
        {
            'dependencies': [
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
            ],
            'name': 'grandchild_B1'
        },
        {
            'dependencies': [
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree_flattened[single_dependency_node_at_end_of_branch_2] 1'] = {
    'dependencies': [
        {
            'dependencies': [
            ],
            'name': 'grandchild_A1'
        },
        {
            'dependencies': [
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree_flattened[single_dependency_in_middle_of_branch] 1'] = {
    'dependencies': [
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1'
                },
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2'
                }
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
            ],
            'name': 'root'
        }
    ],
    'name': None
}

snapshots['TestTaskTree.test_tree_flattened[nested_multiple_dependency_nodes] 1'] = {
    'dependencies': [
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1'
                },
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2'
                }
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1'
                },
                {
                    'dependencies': [
                    ],
                    'name': 'grandchild_B2'
                }
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_tree_flattened[common_dependency] 1'] = {
    'dependencies': [
        {
            'dependencies': [
            ],
            'name': 'common_setup'
        },
        {
            'dependencies': [
            ],
            'name': 'grandchild_B1'
        },
        {
            'dependencies': [
            ],
            'name': 'child_A'
        },
        {
            'dependencies': [
            ],
            'name': 'child_B'
        }
    ],
    'name': 'root'
}

snapshots['TestTaskTree.test_status[nested_single_dependency_nodes] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild',
                    'passes': False
                }
            ],
            'name': 'child',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status[single_dependency_node_at_end_of_branch_1] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1',
                    'passes': False
                }
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status[single_dependency_node_at_end_of_branch_2] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1',
                    'passes': False
                }
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status[single_dependency_in_middle_of_branch] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1',
                    'passes': False
                },
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2',
                    'passes': False
                }
            ],
            'name': 'child_A',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status[nested_multiple_dependency_nodes] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1',
                    'passes': False
                },
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2',
                    'passes': False
                }
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1',
                    'passes': False
                },
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_B2',
                    'passes': False
                }
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status[common_dependency] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'common_setup',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'common_setup',
                    'passes': False
                },
                {
                    'checkers': None,
                    'dependencies': [
                        {
                            'checkers': None,
                            'dependencies': [
                            ],
                            'name': 'common_setup',
                            'passes': False
                        }
                    ],
                    'name': 'grandchild_B1',
                    'passes': False
                }
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'common_setup',
                    'passes': False
                }
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status_deduped[nested_single_dependency_nodes] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild',
                    'passes': False
                }
            ],
            'name': 'child',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status_deduped[single_dependency_node_at_end_of_branch_1] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1',
                    'passes': False
                }
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status_deduped[single_dependency_node_at_end_of_branch_2] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1',
                    'passes': False
                }
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status_deduped[single_dependency_in_middle_of_branch] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1',
                    'passes': False
                },
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2',
                    'passes': False
                }
            ],
            'name': 'child_A',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status_deduped[nested_multiple_dependency_nodes] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1',
                    'passes': False
                },
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2',
                    'passes': False
                }
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1',
                    'passes': False
                },
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_B2',
                    'passes': False
                }
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status_deduped[common_dependency] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'common_setup',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1',
                    'passes': False
                }
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status_flattened[nested_single_dependency_nodes] 1'] = {
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'grandchild',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'root',
            'passes': False
        }
    ],
    'name': None
}

snapshots['TestTaskTree.test_status_flattened[single_dependency_node_at_end_of_branch_1] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'grandchild_B1',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status_flattened[single_dependency_node_at_end_of_branch_2] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'grandchild_A1',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status_flattened[single_dependency_in_middle_of_branch] 1'] = {
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1',
                    'passes': False
                },
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2',
                    'passes': False
                }
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'root',
            'passes': False
        }
    ],
    'name': None
}

snapshots['TestTaskTree.test_status_flattened[nested_multiple_dependency_nodes] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A1',
                    'passes': False
                },
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_A2',
                    'passes': False
                }
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_B1',
                    'passes': False
                },
                {
                    'checkers': None,
                    'dependencies': [
                    ],
                    'name': 'grandchild_B2',
                    'passes': False
                }
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskTree.test_status_flattened[common_dependency] 1'] = {
    'checkers': None,
    'dependencies': [
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'common_setup',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'grandchild_B1',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child_A',
            'passes': False
        },
        {
            'checkers': None,
            'dependencies': [
            ],
            'name': 'child_B',
            'passes': False
        }
    ],
    'name': 'root',
    'passes': False
}

snapshots['TestTaskHelp.test_render_help 1'] = '''
\x1b[1mNAME
\x1b[0m    mock_test -- 
\x1b[1m
DESCRIPTION
\x1b[0mThis is a mock test\x1b[1m
CONFIGURATION
\x1b[0m    - IXIAN:         /home/runner/work/ixian/ixian/ixian
    - PROJECT_NAME:  unittests
\x1b[1m

STATUS
\x1b[0m\x1b[90m○\x1b[0m mock_test
'''

snapshots['TestTaskHelp.test_render_help_no_docstring 1'] = '''
\x1b[1mNAME
\x1b[0m    mock_test -- 
\x1b[1m
DESCRIPTION
\x1b[0m\x1b[1m
CONFIGURATION
\x1b[0m    - IXIAN:         /home/runner/work/ixian/ixian/ixian
    - PROJECT_NAME:  unittests
\x1b[1m

STATUS
\x1b[0m\x1b[90m○\x1b[0m mock_test
'''

snapshots['TestTaskHelp.test_render_help_no_config 1'] = '''
\x1b[1mNAME
\x1b[0m    mock_test -- 
\x1b[1m
DESCRIPTION
\x1b[0mThis is a mock test\x1b[1m

STATUS
\x1b[0m\x1b[90m○\x1b[0m mock_test
'''

snapshots['TestTaskHelp.test_render_status[nested_single_dependency_nodes] 1'] = '''
\x1b[90m○\x1b[0m grandchild
\x1b[90m○\x1b[0m child
\x1b[90m○\x1b[0m root
'''

snapshots['TestTaskHelp.test_render_status[single_dependency_node_at_end_of_branch_1] 1'] = '''
\x1b[90m○\x1b[0m root
    \x1b[90m○\x1b[0m child_A
    \x1b[90m○\x1b[0m grandchild_B1
    \x1b[90m○\x1b[0m child_B
'''

snapshots['TestTaskHelp.test_render_status[single_dependency_node_at_end_of_branch_2] 1'] = '''
\x1b[90m○\x1b[0m root
    \x1b[90m○\x1b[0m grandchild_A1
    \x1b[90m○\x1b[0m child_A
    \x1b[90m○\x1b[0m child_B
'''

snapshots['TestTaskHelp.test_render_status[single_dependency_in_middle_of_branch] 1'] = '''
\x1b[90m○\x1b[0m child_A
    \x1b[90m○\x1b[0m grandchild_A1
    \x1b[90m○\x1b[0m grandchild_A2
\x1b[90m○\x1b[0m root
'''

snapshots['TestTaskHelp.test_render_status[nested_multiple_dependency_nodes] 1'] = '''
\x1b[90m○\x1b[0m root
    \x1b[90m○\x1b[0m child_A
        \x1b[90m○\x1b[0m grandchild_A1
        \x1b[90m○\x1b[0m grandchild_A2
    \x1b[90m○\x1b[0m child_B
        \x1b[90m○\x1b[0m grandchild_B1
        \x1b[90m○\x1b[0m grandchild_B2
'''

snapshots['TestTaskHelp.test_render_status[common_dependency] 1'] = '''
\x1b[90m○\x1b[0m root
    \x1b[90m○\x1b[0m common_setup
    \x1b[90m○\x1b[0m grandchild_B1
    \x1b[90m○\x1b[0m child_A
    \x1b[90m○\x1b[0m child_B
'''

snapshots['TestTaskHelp.test_render_status_passing_checks 1'] = '''
\x1b[92m✔\x1b[0m grandchild
\x1b[92m✔\x1b[0m child
\x1b[92m✔\x1b[0m root
'''
