from typing import Callable

create_default_update_message: Callable[[int, str], str] = (
    lambda number, last_id: (
        "{} documents until {} have been updated successfully".format(
            number, last_id
        )
    )
)
