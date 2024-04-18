from .commands import exportedHandlers as expCmds
from .others import exportedHandlers as expOthers
from .adminCommand import exportedHandlers as expAdmin
from .updateSettings import exportedHandlers as expSettings

handlers = [
    *expAdmin,
    *expCmds,
    *expOthers,
    *expSettings
]