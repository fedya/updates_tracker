import version_compare
import name_expander

import argparse
import requests
import os
import json
import subprocess
import re
import tempfile

headers = {'User-Agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.2171.95 Safari/537.36'}

name_expander.check_version('htop')

#get_nvs(spec_path):
