#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -*- coding: utf-8 -*-
#
# YARA Forge
# A YARA Rule Concentrator
# Florian Roth
# November 2023

__version__ = '0.1.0'

import argparse
import pprint
import logging

from main.rule_collector import retrieve_yara_rule_sets
from main.rule_processors import process_yara_rules
from main.rule_output import write_yara_packages
from qa.rule_qa import evaluate_rules_quality


# Write a section header with dividers
def write_section_header(title, divider_with=72):
   print("\n" + "=" * divider_with)
   print(title.center(divider_with).upper())
   print("=" * divider_with + "\n")


if __name__ == "__main__":

   print(r'  __  _____    ____  ___       ______                     ');
   print(r'  \ \/ /   |  / __ \/   |     / ____/___  _________ ____  ');
   print(r'   \  / /| | / /_/ / /| |    / /_  / __ \/ ___/ __ `/ _ \ ');
   print(r'   / / ___ |/ _, _/ ___ |   / __/ / /_/ / /  / /_/ /  __/ ');
   print(r'  /_/_/  |_/_/ |_/_/  |_|  /_/    \____/_/   \__, /\___/  ');
   print(r'                                            /____/        ');
   print(r'  YARA Forge                                              ');
   print(r'  Aligning hundreds of YARA rules to a common standard    ');
   print(r'  Florian Roth, November 2023                             ');

   parser = argparse.ArgumentParser()
   parser.add_argument("--debug", help="enable debug output", action="store_true")
   args = parser.parse_args()

   # Create a new logger to log into the command line and a log file name yara-forge.log
   # (only set the level to debug if the debug argument is set)
   logger = logging.getLogger()
   logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
   # Set the level of the plyara logger to warning
   logging.getLogger('plyara').setLevel(logging.WARNING)
   logging.getLogger('tzlocal').setLevel(logging.CRITICAL)
   # Create a handler for the command line
   ch = logging.StreamHandler()
   ch.setLevel(logging.DEBUG if args.debug else logging.INFO)
   # Create a handler for the log file
   fh = logging.FileHandler("yara-forge.log")
   fh.setLevel(logging.DEBUG)
   # Create a formatter for the log messages that go to the log file
   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   # Create a formatter for the log messages that go to the command line
   formatter_cmd = logging.Formatter('%(message)s')
   # Add the formatter to the handlers
   ch.setFormatter(formatter_cmd)
   fh.setFormatter(formatter)
   # Add the handlers to the logger
   logger.addHandler(ch)
   logger.addHandler(fh)

   # Retrieve the YARA rule sets
   write_section_header("Retrieving YARA rule sets")
   yara_rule_repo_sets = retrieve_yara_rule_sets(logger=logger)
   #pprint.pprint(yara_rule_repo_sets)

   # Process the YARA rules
   write_section_header("Processing YARA rules")
   processed_yara_repos = process_yara_rules(yara_rule_repo_sets, logger=logger)

   # Evaluate the quality of the rules
   write_section_header("Evaluating YARA rules")
   evaluate_rules_quality(processed_yara_repos, logger=logger)

   # Write the YARA packages
   write_section_header
   write_yara_packages(processed_yara_repos, logger=logger)
