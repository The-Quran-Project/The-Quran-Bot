from .commands import exportedHandlers as expCmds
from .others import exportedHandlers as expOthers
from .adminCommand import exportedHandlers as expAdmin
from .updateSettings import exportedHandlers as expSettings
from .scheduleVerseSend import exportedHandlers as expSchedule


# NOTE: The order of the handlers is important
handlers = [*expSchedule, *expAdmin, *expCmds, *expOthers, *expSettings]
