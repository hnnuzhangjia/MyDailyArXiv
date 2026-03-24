import sys
import time
import pytz
from datetime import datetime
from utils import get_daily_papers_by_keyword_with_retries, generate_table, back_up_files,\
    restore_files, remove_backups, get_daily_date
print("DEBUG: Starting main.py execution...")
beijing_timezone = pytz.timezone('Asia/Shanghai')
# NOTE: arXiv API seems to sometimes return an unexpected empty list.
# get current beijing time date in the format of "2021-08-01"
print("DEBUG: Getting current date...")
current_date = datetime.now(beijing_timezone).strftime("%Y-%m-%d")
print(f"DEBUG: Current date is {current_date}")
# get last update date from README.md
print("DEBUG: Reading README.md to get last update date...")
with open("README.md", "r") as f:
    while True:
        line = f.readline()
        if "Last update:" in line: 
            break
    last_update_date = line.split(": ")[1].strip()
    print(f"DEBUG: Last update date from README: {last_update_date}")
    # if last_update_date == current_date:
        # sys.exit("Already updated today!")
print("DEBUG: Setting up keywords...")
keywords = ["Model Editing", "Knowledge Editing", "Sparse Autoencoder"] # TODO add more keywords
print(f"DEBUG: Keywords to process: {keywords}")
max_result = 20 # maximum query results from arXiv API for each keyword
issues_result = 1 # maximum papers to be included in the issue
print("DEBUG: Setting up column names...")
# all columns: Title, Authors, Abstract, Link, Tags, Comment, Date
# fixed_columns = ["Title", "Link", "Date"]
column_names = ["Title", "Link", "Abstract", "Date", "Comment"]
print("DEBUG: Backing up files...")
back_up_files() # back up README.md and ISSUE_TEMPLATE.md
print("DEBUG: Files backed up successfully")
# write to README.md
print("DEBUG: Writing to README.md...")
f_rm = open("README.md", "w") # file for README.md
f_rm.write("# Daily Papers\n")
f_rm.write("The project automatically fetches the latest papers from arXiv based on keywords.\n\nThe subheadings in the README file represent the search keywords.\n\nOnly the most recent articles for each keyword are retained, up to a maximum of 100 papers.\n\nYou can click the 'Watch' button to receive daily email notifications.\n\nLast update: {0}\n\n".format(current_date))
print("DEBUG: README.md header written")
# write to ISSUE_TEMPLATE.md
print("DEBUG: Writing to ISSUE_TEMPLATE.md...")
f_is = open(".github/ISSUE_TEMPLATE.md", "w") # file for ISSUE_TEMPLATE.md
f_is.write("---\n")
f_is.write("title: Latest {0} Papers - {1}\n".format(issues_result, get_daily_date()))
f_is.write("labels: documentation\n")
f_is.write("---\n")
f_is.write("**Please check the [Github](https://github.com/zezhishao/MTS_Daily_ArXiv) page for a better reading experience and more papers.**\n\n")
print("DEBUG: ISSUE_TEMPLATE.md written")
print("DEBUG: Starting keyword processing loop...")
for i, keyword in enumerate(keywords):
    print(f"DEBUG: Processing keyword {i+1}/{len(keywords)}: {keyword}")
    f_rm.write("## {0}\n".format(keyword))
    f_is.write("## {0}\n".format(keyword))
    if len(keyword.split()) == 1: 
        link = "AND" # for keyword with only one word, We search for papers containing this keyword in both the title and abstract.
        print(f"DEBUG: Using AND logic for keyword: {keyword}")
    else: 
        link = "OR"
        print(f"DEBUG: Using OR logic for keyword: {keyword}")
    
    print(f"DEBUG: Calling get_daily_papers_by_keyword_with_retries for {keyword}...")
    start_time = time.time()
    papers = get_daily_papers_by_keyword_with_retries(keyword, column_names, max_result, link)
    end_time = time.time()
    print(f"DEBUG: Paper retrieval for {keyword} took {end_time - start_time:.2f} seconds")
    
    if papers is None: # failed to get papers
        print("DEBUG: Failed to get papers!")
        f_rm.close()
        f_is.close()
        restore_files()
        sys.exit("Failed to get papers!")
    
    print(f"DEBUG: Generating table for {keyword} with {len(papers)} papers")
    rm_table = generate_table(papers)
    is_table = generate_table(papers[:issues_result], ignore_keys=["Abstract"])
    f_rm.write(rm_table)
    f_rm.write("\n\n")
    f_is.write(is_table)
    f_is.write("\n\n")
    print(f"DEBUG: Completed processing {keyword}")
    time.sleep(5) # avoid being blocked by arXiv API
print("DEBUG: Closing files...")
f_rm.close()
f_is.close()
print("DEBUG: Removing backups...")
remove_backups()
print("DEBUG: Main execution completed successfully!")
