from jira.client import JIRA
from datetime import datetime, date, timedelta
from BusinessHours import BusinessHours
import sys

global jira
global jiraUser
global jiraPass
global project
global jiraCreated
global jiraResolved

# Specify JIRA authentication here
jiraUser = ''
jiraPass = ''
project = ''

def init_JIRA(firstDay, lastDay):
   # Add server for your jira server, i.e. https://jira.business.com.au
   jira = JIRA(options={'server': ''}, basic_auth=(jiraUser, jiraPass))
   # Only created and resolved dates are required for the queries
   jqlCreated = ('project = %s AND created >= %s AND created <= %s ORDER BY created DESC, key DESC') % (project, firstDay, lastDay)
   jqlResolved = ('project = %s AND resolved >= %s AND resolved <= %s ORDER BY created DESC, key DESC') % (project, firstDay, lastDay)
   return (jira, jqlCreated, jqlResolved)

def sla(severity, total_hours, slaType):
   # Standard SLA times per severity 
   if slaType == "response":
      limits = {
         'Severity 1':4,
         'Severity 2':8,
         'Severity 3':12,
         'other': 24,
      }
   elif slaType == "resolution":
      limits = {
         'Severity 1':24,
         'Severity 2':36,
         'Severity 3':72,
         'other':5000,
      }
   if severity not in limits:
      severity = 'other'
   if "None" in total_hours:
      return 'n/a'
   if int(total_hours) < limits[severity]:
      return 'yes'
   else:
      return 'no'

def parseCreated(created):
   created = created.split('.')[0]
   created = datetime.strptime(created, '%Y-%m-%dT%H:%M:%S')
   return created

def calcDuration(created, end_time):
   totalDuration = BusinessHours(created,end_time)
   totalDuration = totalDuration.gethours()
   totalDuration = str(totalDuration)
   totalDuration = totalDuration.split('.')[0]
   return totalDuration

def getCreated(firstDay, lastDay):
   jira = init_JIRA(firstDay, lastDay)[0]
   jqlCreated = init_JIRA(firstDay, lastDay)[1]
   # Only created and resolved dates are required for the queries
   countCreate = 0
   print "%s - %s" % (firstDay, lastDay)
   print "Tickets created"
   print "Key,Summary,Severity,Hours until first response,SLA Met"
   for issue in jira.search_issues(jqlCreated):
      jira_key = issue.key
      summary = issue.fields.summary
      severity = issue.fields.customfield_.value
      if "," in summary:
         summary = summary.replace(',', '')
      if issue.fields.created:
         created = parseCreated(issue.fields.created)
      else:
         sys.exit('Missing created date from %s') % ' '.join(jira_key, summary)
      if issue.fields.customfield_:
         response = issue.fields.customfield_.split('.')[0]
         response = datetime.strptime(response, '%Y-%m-%d %H:%M:%S')
      else:
         response = "None"
      if response is not "None":
         timeToRespond = calcDuration(created,response)
      else:
         timeToRespond = "No Response"
      slaMet = sla(severity, timeToRespond, "response")
      countCreate+=1
      print ','.join([jira_key, summary, severity, timeToRespond, slaMet])
   print "Created ticket count: [ %s ]\n" % countCreate

def getResolved(firstDay, lastDay):
   jira = init_JIRA(firstDay, lastDay)[0]
   jqlResolved= init_JIRA(firstDay, lastDay)[2]
   countResolved = 0
   print "Tickets resolved"
   print "Key,Summary,Time until resolution,SLA Met"
   for issue in jira.search_issues(jqlResolved):
      jira_key = issue.key
      summary = issue.fields.summary
      severity = issue.fields.customfield_.value
      if "," in summary:
         summary = summary.replace(',', '')
      if issue.fields.created:
         created = parseCreated(issue.fields.created)
      else:
         sys.exit('Missing created date from %s') % ' '.join(jira_key, summary)
      if issue.fields.customfield_:
         resolved = issue.fields.customfield_.split('.')[0]
         resolved = datetime.strptime(resolved, '%Y-%m-%dT%H:%M:%S')
      else:
         resolved = "None"
      if resolved is not "None":
         timeToResolve = calcDuration(created, resolved)
      else:
         timeToResolve = "None"
      slaMet = sla(severity, timeToResolve, "resolution")
      print ','.join([jira_key, summary, timeToResolve, slaMet])
      countResolved+=1
   print "Resolved ticket count: [ %s ]" % countResolved

def customerList():
   # If scheduling you'll probably want to configure these for current time -30d or something
   firstDay = raw_input('Please enter first day yyyy-mm-dd: >')
   lastDay = raw_input('Please enter last day yyyy-mm-dd: >')
   getCreated(firstDay, lastDay)
   getResolved(firstDay, lastDay)

if __name__ == "__main__":
   customerList()
