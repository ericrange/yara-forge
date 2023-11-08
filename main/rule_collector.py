import os
import shutil
from git import Repo
import plyara
import datetime
import logging

REPO_STAGING_DIR = "./repos"

YARA_REPOS = [
   {
      "name": "YARA Style Guide",  # used in headers and as prefix for each of the rules (so keep it short)
      "url": 'https://github.com/Neo23x0/YARA-Style-Guide',  # URL of the repository on GitHub
      "author": "Florian Roth",  # used when the author is not defined in the rule
      "quality": 80,  # 0-100 (0 = low, 100 = high) base value; indicates the quality of the rules in the repository
      "branch": "master"  # name of the branch to download
   },
   {
      "name": "ReversingLabs",
      "url": 'https://github.com/reversinglabs/reversinglabs-yara-rules/',
      "author": "ReversingLabs",
      "quality": 90,
      "branch": "develop"
   }
]

# Retrieve YARA rules from online repositories
def retrieve_yara_rule_sets(logger):
   
   # The list of YARA rule sets of all repositories
   yara_rule_repo_sets = []

   # Remove the existing repo directory and all its contents
   shutil.rmtree(os.path.join(REPO_STAGING_DIR), ignore_errors=True)
   
   # Loop over the repositories
   for repo in YARA_REPOS:
      
      # Output the repository information to the console in a single line
      logger.log(logging.INFO, "Retrieving YARA rules from repository: %s" % repo['name'])

      # Extract the owner and the repository name from the URL
      repo_url_parts = repo['url'].split("/")
      repo['owner'] = repo_url_parts[3]
      repo['repo'] = repo_url_parts[4].split(".")[0]

      # Clone the repository
      repo_folder = os.path.join(REPO_STAGING_DIR, repo['repo'])
      Repo.clone_from(repo['url'], repo_folder, branch=repo['branch'])

      # Walk through the extracted folders and find a LICENSE file and save it into the repository object
      for root, dirs, files in os.walk(os.path.join(REPO_STAGING_DIR, repo['repo'])):
         for file in files:
            if file == "LICENSE" or file == "LICENSE.txt" or file == "LICENSE.md":
               file_path = os.path.join(root, file)
               with open(file_path, "r") as f:
                  repo['license'] = f.read()
                  break

      # Walk through the extracted folders and find all YARA files
      yara_rule_sets = []
      for root, dirs, files in os.walk(repo_folder):
         for file in files:
            if file.endswith(".yar") or file.endswith(".yara"):
               file_path = os.path.join(root, file)

               # Debug output
               logger.log(logging.DEBUG, "Found YARA rule file: %s" % file_path)

               # Read the YARA file
               with open(file_path, "r") as f:
                  yara_file_content = f.read()
                  # Parse the rules in the file
                  try:
                     # Get the rule file path in the repository
                     relative_path = os.path.relpath(file_path, start=repo_folder)
                     # Parse the YARA rules in the file
                     yara_parser = plyara.Plyara()
                     yara_rules = yara_parser.parse_string(yara_file_content)
                     # Create a YARA rule set object
                     yara_rule_set = {
                        "rules": yara_rules,
                        "file_path": relative_path,
                     }
                     # Debug output
                     logger.log(logging.DEBUG, "Found %d YARA rules in file: %s" % (len(yara_rules), file_path))
                     # Append to list of YARA rule sets
                     yara_rule_sets.append(yara_rule_set)
                     
                  except Exception as e:
                     print(e)
                     logger.log(logging.ERROR, "Skipping YARA rule in the following file because of a syntax error: %s " % file_path)
      
      # Append the YARA rule repository
      yara_rule_repo = {
         "name": repo['name'],
         "url": repo['url'],
         "author": repo['author'],
         "owner": repo['owner'],
         "repo": repo['repo'],
         "branch": repo['branch'],
         "rules_sets": yara_rule_sets,
         "quality": repo['quality'],
         "license": repo['license'],
         "retrieval_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         "repo_path": repo_folder,
      }
      yara_rule_repo_sets.append(yara_rule_repo)

      logger.log(logging.INFO, "Retrieved %d YARA rules from repository: %s" % (len(yara_rule_sets), repo['name']))

   # Return the YARA rule sets
   return yara_rule_repo_sets


def check_yara_rule(yara_rule_string):
   yara_parser = plyara.Plyara()
   try:
      yara_parser.parse_string(yara_rule_string) 
      return True
   except Exception as e:
      print(e)
      return False
