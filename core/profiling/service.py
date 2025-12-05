def update_profile(db, profile: UserProfile, new_data: dict):
    for key, value in new_data.items():
        old = profile.stats.get(key)
        profile.stats[key] = value if old is None else value

    db.commit()
    return profile


def create_profile(db, identity):
    obj = UserProfile(
        identity=identity,
        behavior={},
        preferences={},
        stats={"messages": 0}
    )
    db.add(obj)
    db.commit()
    return obj
