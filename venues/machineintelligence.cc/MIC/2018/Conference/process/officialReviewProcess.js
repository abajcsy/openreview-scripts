function(){
    var SHORT_PHRASE = 'MIC 2018 Conference';
    var CONFERENCE_ID = 'machineintelligence.cc/MIC/2018/Conference';
    var or3client = lib.or3client;

    // send email to author of paper submission
    var origNote = or3client.or3request(or3client.notesUrl+'?id='+note.forum, {}, 'GET', token);
    origNote.then(function(result) {
      var forum = result.notes[0];
      var note_number = forum.number;

      var author_mail = {
        groups: forum.content.authorids,
        subject: 'Review of your submission to ' + SHORT_PHRASE + ': "' + forum.content.title + '"',
        message: 'Your submission to ' + SHORT_PHRASE + ' has received an official review.\n\nTitle: ' + note.content.title + '\n\nReview: ' + note.content.review + '\n\nTo view the review, click here: ' + baseUrl+'/forum?id=' + note.forum
      };

      return or3client.or3request( or3client.mailUrl, author_mail, 'POST', token );
    })
    // do not allow reviewer to post another review for this paper
    .then(result => or3client.addInvitationNoninvitee(note.invitation, note.signatures[0], token))
    .then(result => done())
    .catch(error => done(error));
    return true;
  };




