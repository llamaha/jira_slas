from jira.client import JIRA
from datetime import datetime, date, timedelta
from BusinessHours import BusinessHours
import sys

global jira
global jiraURL
global jiraUser
global jiraPass
global project
global jiraCreated
global jiraResolved

# Specify JIRA authentication here
jiraUser = ''
jiraPass = ''
project = ''
jiraURL = ''
def sla(severity,timeToRespond):
   # Standard SLA times per severity 
   sev1 = 4
   sev2 = 8
   sev345 = 24
   # Determine whether SLA's were met
   if (severity is not "Severity 1") and (severity is not "Severity 2") and \
      timeToRespond < sev345:
      slaMet = "yes"
   elif severity == "Severity 1" and timeToRespond < sev1:
      slaMet = "yes"
   elif severity == "Severity 2" and timeToRespond < sev2:
      slaMet = "yes"
   else:
      slaMet = "no"
   return slaMet

def getResults(firstDay, lastDay):
   jira = JIRA(options={'server': jiraURL}, basic_auth=(jiraUser, jiraPass))
   # Only created and resolved dates are required for the queries
   jqlCreated=('project = %s AND created >= %s AND created <= %s ORDER BY created DESC, key DESC') % (project, firstDay, lastDay)
   jqlResolved=('project = %s AND resolved >= %s AND resolved <= %s ORDER BY created DESC, key DESC') % (project, firstDay, lastDay)

   countCreate = 0
   countResolved = 0
   countOpen = 0
   print "%s - %s" % (firstDay, lastDay)
   print "Tickets created"
   print "Key,Summary,Severity,Hours until first response,SLA Met"
   for issue in jira.search_issues(jqlCreated):
      jira_key = issue.key
      summary = issue.fields.summary
      severity = issue.fields.customfield_10030.value
      if "," in jira_key or summary:
         jira_key = jira_key.replace(',', '')
         summary = summary.replace(',', '')
      if issue.fields.created:
         created = issue.fields.created.split('.')[0]
         created = datetime.strptime(created, '%Y-%m-%dT%H:%M:%S')
      else:
         created = "None"
      if issue.fields.customfield_11971:
         response = issue.fields.customfield_11971.split('.')[0]
         response = datetime.strptime(response, '%Y-%m-%d %H:%M:%S')
      else:
         response = "None"
      if response is not "None":
         timeToRespond = BusinessHours(created,response)
         timeToRespond = timeToRespond.gethours()
         slaMet = sla(severity,timeToRespond)
         timeToRespond = str(timeToRespond)
         timeToRespond = timeToRespond.split('.')[0]
      else:
         timeToRespond = "No Response"
         slaMet = "Unknown"
      countCreate+=1
      print jira_key + "," + summary + "," + severity + "," + timeToRespond + "," + slaMet
   print "Created ticket count: [ %s ]\n" % countCreate
   print "Tickets resolved"
   print "Key,Summary,Time until resolution"
   for issue in jira.search_issues(jqlResolved):
      jira_key = issue.key
      summary = issue.fields.summary
      if "," in jira_key or summary:
         jira_key = jira_key.replace(',', '')
         summary = summary.replace(',', '')
      if issue.fields.created:
         created = issue.fields.created.split('.')[0]
         created = datetime.strptime(created, '%Y-%m-%dT%H:%M:%S')
      else:
         created = "None"
      if issue.fields.customfield_10474:
         resolved = issue.fields.customfield_10474.split('.')[0]
         resolved = datetime.strptime(resolved, '%Y-%m-%dT%H:%M:%S')
      else:
         resolved = "None"
      if resolved is not "None":
         timeToResolve = BusinessHours(created,resolved)
         timeToResolve = timeToResolve.gethours()
         timeToResolve = str(timeToResolve)
         timeToResolve = timeToResolve.split('.')[0]
      else:
         timeToResolve = "None"
      print jira_key + "," + summary + "," + timeToResolve
      countResolved+=1
   print "Resolved ticket count: [ %s ]" % countResolved

def customerList():
   firstDay = raw_input('Please enter first day yyyy-mm-dd: >')
   lastDay = raw_input('Please enter last day yyyy-mm-dd: >')
   firstDay = str(firstDay)
   lastDay = str(lastDay)
   getResults(firstDay, lastDay)

if __name__ == "__main__":
   customerList()
