def store_temp(db, session_id, data):
    obj = ShortTermMemory(session_id=session_id, data=data)
    db.add(obj)
    db.commit()
    return obj
