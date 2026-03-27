from app.modules.content.schemas.post import PostCreate, PostUpdate, PostRead
from app.modules.content.schemas.material import MaterialUpdate, MaterialRead
from app.modules.content.schemas.goal import GoalCreate, GoalUpdate, GoalRead
from app.modules.content.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.modules.content.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingRead

__all__ = [
    "PostCreate", "PostUpdate", "PostRead",
    "MaterialUpdate", "MaterialRead",
    "GoalCreate", "GoalUpdate", "GoalRead",
    "TaskCreate", "TaskUpdate", "TaskRead",
    "MeetingCreate", "MeetingUpdate", "MeetingRead",
]
