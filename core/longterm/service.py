def save_fact(db, key, value):
    obj = LongTermMemory(key=key, value=value)
    db.add(obj)
    db.commit()
    return obj
