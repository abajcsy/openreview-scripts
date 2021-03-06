function() {
    var or3client = lib.or3client;
    var CONFERENCE_ID = 'ICLR.cc/2019/Conference';
    var PROGRAM_CHAIRS_ID = CONFERENCE_ID + '/Program_Chairs';
    var SHORT_PHRASE = 'ICLR 2019'

    var origNote = or3client.or3request(or3client.notesUrl+'?id='+note.forum, {}, 'GET', token);

    origNote.then(function(result){
      var forum = result.notes[0];

      var pc_mail = {
        "groups": [PROGRAM_CHAIRS_ID];
        "subject": "[" + SHORT_PHRASE + "] Meta-review by an area chair has been posted: " + "\"" + forum.content.title + "\".",
        "message": "A paper submission to " + SHORT_PHRASE + " has received a meta-review by an area chair.\n\nTitle: "+note.content.title+"\n\nMeta-review: "+note.content.metareview+"\n\nTo view the meta-review, click here: "+baseUrl+"/forum?id=" + note.forum + "&noteId=" + note.id
      };

      return or3client.or3request( or3client.mailUrl, pc_mail, 'POST', token );

    })
    .then(result => done())
    .catch(error => done(error));

    return true;
  };
