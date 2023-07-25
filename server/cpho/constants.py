HSO_SUBMISSION_TYPE = "hso"
PROGRAM_SUBMISSION_TYPE = "program"
SUBMISSION_TYPES = [
    HSO_SUBMISSION_TYPE,
    PROGRAM_SUBMISSION_TYPE,
]


class SUBMISSION_STATUSES:
    NO_DATA = "no_data"
    NOT_YET_SUBMITTED = "not_yet_submitted"
    PROGRAM_SUBMITTED = "program_submitted"
    SUBMITTED = "submission_up_to_date"
    MODIFIED_SINCE_LAST_SUBMISSION = "modified_since_last_submission"
