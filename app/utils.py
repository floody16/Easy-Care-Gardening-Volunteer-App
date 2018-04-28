from app.models import UserType, TimePreference


def get_suitable_jobs(jobs, time_prefs, day_prefs):
    """
    Where the magic happens -- take a list of jobs and return only those that satisfy provided availability (see params).
    TODO: Can this be replaced by a clever query?

    :param jobs: All jobs on the database.
    :param time_prefs: 2-character string denoting time preference. Empty if no preference.
    :param day_prefs: 6-character binary string where each bit represents availability for that day (Sunday excluded).
    :return: Jobs where job.date and job.time satisfy user's availability (time_prefs, day_prefs).
    """
    suitable_jobs = []
    available_days = get_day_prefs(day_prefs)

    for job in jobs:
        if job.date.weekday() in available_days:
            if job.time in time_prefs or time_prefs == 'AP':
                suitable_jobs.append(job)

    return suitable_jobs


def get_day_prefs(day_prefs):
    """
    Converts a 6-character string denoting day preferences into a list of integers.
    Each integer corresponds to an available day of the week's index position:
        Monday = 0
        Tuesday = 1
        ...
        Saturday = 5

    '101010' (Monday, Wednesday, Friday) => [0, 2, 4]

    :param day_prefs: 6-character binary string where each bit represents availability for that day (Sunday excluded).
    :return: A list of integers where each element is an available day's index position.
    """
    days = []

    for i in range(0, 6):
        if day_prefs[i] == '1':
            days.append(i)

    return days


def day_pref_to_binary(day_prefs):
    """
    Does the inverse of get_day_prefs().

    :param day_prefs: A list of integers where each element is an available day's index position.
    :return: 6-character binary string where each bit represents availability for that day (Sunday excluded).
    """
    binary = ['0', '0', '0', '0', '0', '0']

    for day_pref in day_prefs:
        binary[int(day_pref)] = '1'

    return ''.join(binary)


def user_type_pretty(user_type):
    """
    Converts an integer denoting user type (0 = Volunteer, 1 = Team Leader, 2 = Coordinator, 3 = Administrator) into prettier string form.
    See models.py for __str__ function.

    :param user_type: Type of a particular user in integer form.
    :return: Type of a particular user in string form.
    """
    return str(UserType(user_type))


def time_pref_pretty(time_pref):
    """
    Converts a 2-character string denoting time preference ('AM' = Half-day (Morning), 'PM' = Half-day (Afternoon), 'AP' = Full day/no preference)
    into verbose string form. See models.py for __str__ function.

    :param time_pref: Time preference for a particular user in 2-character string form.
    :return: Verbose time preference for a particular user.
    """
    return str(TimePreference(time_pref))


def day_prefs_pretty(day_prefs):
    """
    Converts a 6-character string denoting day preferences into a list of days (Monday, Tuesday, ... , Saturday).

    :param day_prefs: 6-character binary string where each bit represents availability for that day (Sunday excluded).
    :return: A list of days that match day_prefs.
    """
    if not day_prefs or day_prefs == '000000':
        return ''

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    pretty = []

    for i in range(0, 6):
        if day_prefs[i] == '1':
            pretty.append(days[i])

    return pretty


def timestamp_pretty(timestamp, show_time=True):
    """
    Converts a timestamp to a pretty format with optional time. Only the date is shown otherwise.

    :param timestamp: The timestamp to be converted.
    :param show_time: Whether to include or exclude time from timestamp if applicable. True by default.
    :return: Pretty timestamp.
    """
    if not show_time:
        return timestamp.strftime('%d %B %Y (%A)')

    return timestamp.strftime('%d %B %Y at %H:%M')
