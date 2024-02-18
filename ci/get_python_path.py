#!/bin/env python3

import sys

# obtain python interpreter path
python_path = sys.path

# print path as if we were to export it in bash
print(f'{":".join(python_path)}')
