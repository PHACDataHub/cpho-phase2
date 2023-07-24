HSO_APPROVAL_TYPE = "hso"
PROGRAM_APPROVAL_TYPE = "program"
APPROVAL_TYPES = [
    HSO_APPROVAL_TYPE,
    PROGRAM_APPROVAL_TYPE,
]


class APPROVAL_STATUSES:
    NO_DATA = "no_data"
    NOT_YET_SUBMITTED = "not_yet_submitted"
    PROGRAM_SUBMITTED = "program_submitted"
    SUBMITTED = "submission_up_to_date"
    MODIFIED_SINCE_LAST_SUBMISSION = "modified_since_last_submission"
