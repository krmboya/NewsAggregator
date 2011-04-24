def calculate_score(points, hour_age, gravity=1.8):
    return (points-1.0)/(hour_age+2.0)**gravity


while True:
        news_items = db().select(db.submission.points, db.submission.post_time, db.submission.score, db.submission.id)
        for item in news_items:
            new_score = calculate_score(item.points, seconds_since(item.post_time, now)/3600)
            item.update_record(score = new_score)
            db.commit()
    
        comments = db().select(db.comment.points, db.comment.post_time, db.comment.score, db.comment.id)
        for item in comments:
            new_score = calculate_score(item.points, seconds_since(item.post_time, now)/3600)
            item.update_record(score = new_score)
            db.commit()
        time.sleep(10)
        


