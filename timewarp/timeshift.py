from datetime import datetime, timedelta, date
from typing import List, Union


def timeshift_json(
        data: Union[dict, list],
        num_days: int,
        exclusion_list: List[str]) -> Union[dict, list]:
    """
    Recursively updates date and datetime elements in a JSON-like object by adding 24 hours,
    while skipping keys in the exclusion list.

    :param data: The JSON-like object (dict or list) to process.
    :param num_days: The number of days to move all date / datetime elements forward
    :param exclusion_list: A list of keys to exclude from modification.
    :return: The updated JSON-like object.
    """
    def update_value(key, value):
        # Check if the key is in the exclusion list
        if key in exclusion_list:
            return value

        # Try to parse the value as a date or datetime and add requested days
        if isinstance(value, str):
            try:
                d = date.fromisoformat(value)
                return (d + timedelta(days=num_days)).isoformat()
            except ValueError:
                try:
                    dt = datetime.fromisoformat(value)
                    result = (dt + timedelta(days=num_days)).isoformat()
                    # prefer Z if offset is GMT
                    return result.replace("+00:00", "Z")
                except ValueError:
                    return value  # Return unchanged if not a valid datetime or date
        return value

    if isinstance(data, dict):
        return {key: timeshift_json(value, num_days, exclusion_list)
                if isinstance(value, (dict, list)) else update_value(key, value)
                for key, value in data.items()}
    elif isinstance(data, list):
        return [timeshift_json(item, num_days, exclusion_list) for item in data]
    else:
        return data  # Base case: return data unchanged

