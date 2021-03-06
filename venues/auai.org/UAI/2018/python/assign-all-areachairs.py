import importlib
import openreview
import argparse
import csv

if __name__ == "__main__":

    ## Argument handling
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseurl', help="base url")
    parser.add_argument('--username')
    parser.add_argument('--password')

    args = parser.parse_args()
    client = openreview.Client(baseurl=args.baseurl, username=args.username, password=args.password)
    print "connecting to ", client.baseurl

    assignments = client.get_notes(invitation='auai.org/UAI/2018/-/Paper_Assignment')
    ac_assignments = [a for a in assignments if a.content['label'] == 'areachairs']
    papers = client.get_notes(invitation='auai.org/UAI/2018/-/Blind_Submission')
    papers_by_forum = {n.forum: n for n in papers}

    for assignment in ac_assignments:
        assignment_entries = assignment.content['assignedGroups']

        paper = papers_by_forum[assignment.forum]

        for entry in assignment_entries:
            openreview.tools.assign(client, paper.number, 'auai.org/UAI/2018',
                parent_group_params = {},
                reviewer_to_add = entry['userId'].encode('utf-8'),
                check_conflicts_invitation = None,
                parent_label = 'Area_Chairs',
                individual_label = 'Area_Chair')

