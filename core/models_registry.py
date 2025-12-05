from core.database import Base
import core.personality.models
import core.memory.models
import core.planner.models
import core.profiling.models
import core.chat.models
import core.context.models
import core.longterm.models
import core.shortterm.models
import core.office.models
import core.audio.models

def create_all():
    Base.metadata.create_all()
