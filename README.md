jira_slas
=========

JIRA SLA reporting script that calculates business hours between created date and hours to first response and time to resolution.

It's important that you set the custom fields in the script, they are currently in the code as customfield_ (this will be improved).  The custom fields are in the JSON data for the fields:

Severity

Time of first response

Time of resolution

If you don't have the 'Time of first response' field in JIRA then install the charting plugin 'Time of first response', it will create this field for you.  You will have to reindex JIRA afterwards.

Enter your JIRA login information and JIRA server, set your SLA levels (in hours).

Edit the queries using JQL from JIRA to refine the search results.

This script depends on the BusinessHours package found here:
https://github.com/dnel/BusinessHours

The BusinessHours package installed via Pip (1.01) is currently broken so don't use it!
_non_italic_word_part_
