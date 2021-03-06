#!/usr/bin/python

"""
A script for managing groups with parameters that depend on the papers to which
they are attached.

Usage:

python groups.py Reviewers
python groups.py Reviewers --overwrite
"""

import openreview
import argparse
import akbc19 as conference_config
import openreview.tools
import numpy as np
import random

def getBibtex(client, note):
    firstWord = note.content["title"].split(' ')[0].lower();
    url = client.baseurl + '/forums?id=' + note.forum
    return '@inproceedings{\
    \nanonymous2019' + firstWord + ',\
    \ntitle={' + note.content["title"] + '},\
    \nauthor={Anonymous},\
    \njournal={International Conference on Learning Representations},\
    \nyear={2019},\
    \nurl={' + url + '},\
    \nnote={under review}\
    \n}'

def create_blind_note(note):
    return openreview.Note(
        original= note.id,
        invitation= conference_config.BLIND_SUBMISSION_ID,
        forum= None,
        signatures= [conference_config.CONFERENCE_ID],
        writers= [conference_config.CONFERENCE_ID],
        readers= ['everyone'],
        content= {
            "authors": ['Anonymous'],
            "authorids": [],
            "_bibtex": None
        })

def freeze_note(note, writers=[conference_config.CONFERENCE_ID]):
    note.writers = writers
    return note

def freeze_and_post(client, note):
    client.post_note(freeze_note(note))

def post_blind_note(client, original_note):
    blind_note = client.post_note(create_blind_note(original_note))
    bibtex_entry = getBibtex(client, blind_note)
    paper_group_id = conference_config.CONFERENCE_ID + "/Paper{}".format(blind_note.number)
    author_group_id = conference_config.CONFERENCE_ID + "/Paper{}/Authors".format(blind_note.number)

    blind_note.content = {
        "authors": ['Anonymous'],
        "authorids": [author_group_id],
        "_bibtex": bibtex_entry
    }

    return client.post_note(blind_note)

def _append_manual_conflicts(profile, manual_user_conflicts):
    for conflict_domain in manual_user_conflicts:
        manual_entry = {
            "end": None,
            "start": None,
            "position": "Manual Entry",
            "institution": {
                "name": "Manual Entry",
                "domain": conflict_domain
            }
        }
        profile.content['history'].append(manual_entry)
    return profile

def _build_entries(author_profiles, reviewer_profiles, paper_bid_jsons, scores_by_reviewer, manual_conflicts_by_id):
    entries = []
    for profile in reviewer_profiles:
        bid_score_map = {
            'Very High': 1.0,
            'High': 0.5,
            'Neutral': 0.0,
            'Low': -0.5,
            'Very Low': -1.0
        }
        try:
            reviewer_bids = sorted([t for t in [j for j in paper_bid_jsons if j['tcdate']] if profile.id in t['signatures']], key=lambda t: t.get('tcdate',0), reverse=True)
        except TypeError as e:
            print(paper_bid_jsons)
            raise e
        reviewer_scores = scores_by_reviewer.get(profile.id, {})

        # find conflicts between the reviewer's profile and the paper's authors' profiles
        user_entry = {
            'userid': profile.id,
            'scores': reviewer_scores
        }

        if reviewer_bids:
            bid_score = bid_score_map.get(reviewer_bids[0]['tag'], 0.0)
            if bid_score != 0.0:
                user_entry['scores']['bid'] = bid_score

        manual_user_conflicts = manual_conflicts_by_id.get(profile.id, [])
        if manual_user_conflicts:
            profile = _append_manual_conflicts(profile, manual_user_conflicts)
        conflicts = openreview.tools.get_conflicts(author_profiles, profile)

        if conflicts:
            user_entry['conflicts'] = conflicts

        entries.append(user_entry)

    return entries

def post_metadata_note(client,
    blind_note,
    reviewer_profiles,
    metadata_inv,
    scores_by_reviewer,
    manual_conflicts_by_id):

    original_authorids = blind_note.details['original']['content']['authorids']
    paper_bid_jsons = blind_note.details['tags']
    paper_author_profiles = client.get_profiles(original_authorids)
    entries = _build_entries(
        paper_author_profiles,
        reviewer_profiles,
        paper_bid_jsons,
        scores_by_reviewer,
        manual_conflicts_by_id)

    new_metadata_note = openreview.Note(**{
        'forum': blind_note.id,
        'invitation': metadata_inv.id,
        'readers': metadata_inv.reply['readers']['values'],
        'writers': metadata_inv.reply['writers']['values'],
        'signatures': metadata_inv.reply['signatures']['values'],
        'content': {
            'entries': entries
        }
    })

    return client.post_note(new_metadata_note)

if __name__ == '__main__':
    # Argument handling
    parser = argparse.ArgumentParser()
    parser.add_argument('notes', nargs='*', help="any of the following: " + ", ".join(group_templates.keys()))
    parser.add_argument('--overwrite', action='store_true', help="if present, overwrites the members of the groups")
    parser.add_argument('--baseurl', help="base url")
    parser.add_argument('--username')
    parser.add_argument('--password')
    args = parser.parse_args()

    client = openreview.Client(baseurl=args.baseurl, username=args.username, password=args.password)

