def can_vote(target_id, target_type, target_author):
    #target_id = request.args(2)

    if (not session.authorized) or (session.authorized == target_author):
        return False

    #if target_type == 'submission':
    #    item = db(db.submission.id == target_id).select()[0]
    #else:
    #    item = db(db.comment.id == target_id).select()[0]
    
    


    
    item = db((db.vote.item_type == target_type) &
               (db.vote.author == session.authorized) &
               (db.vote.item_id == target_id)).select()

    if len(item):
        #return "jQuery('#upvote%s').css('visibility', 'hidden')" % target_id
        return False
    else:
        return True

