from app.models import UserType, TimePreference


def get_suitable_jobs(jobs, timeprefs, dayprefs):
    """
    Where the magic happens -- take a list of jobs and return only those that satisfy provided availability (see params).
    TODO: Can this be replaced by a clever query?

    :param jobs: All jobs on the database.
    :param timeprefs: 2-character string denoting time preference. Empty if no preference.
    :param dayprefs: 6-character binary string where each bit represents availability for that day (Sunday excluded).
    :return: Jobs where job.date and job.time satisfy user's availability (timeprefs, dayprefs).
    """
    suitable_jobs = []

    available_days = get_dayprefs(dayprefs)

    for job in jobs:
        if job.date.weekday() in available_days:
            if job.time in timeprefs or not timeprefs:
                suitable_jobs.append(job)

    return suitable_jobs


def usertype_pretty(usertype):
    """
    Converts an integer denoting user type (0 = Volunteer, 1 = Team Leader, 2 = Coordinator, 3 = Administrator) into prettier string form.
    See models.py for __str__ function.

    :param usertype: Type of a particular user in integer form.
    :return: Type of a particular user in string form.
    """
    return str(UserType(usertype))


def timepref_pretty(timepref):
    """
    Converts a 2-character string denoting time preference ('AM' = Half-day (Morning), 'PM' = Half-day (Afternoon), '' = Full day/no preference)
    into verbose string form. See models.py for __str__ function.

    :param timepref: Time preference for a particular user in 2-character string form.
    :return: Verbose time preference for a particular user.
    """
    return str(TimePreference(timepref))


def get_dayprefs(dayprefs):
    """
    Converts a 6-character string denoting day preferences into a list of integers.
    Each integer corresponds to an available day of the week's index position:
        Monday = 0
        Tuesday = 1
        ...
        Saturday = 5

    '101010' (Monday, Wednesday, Friday) => [0, 2, 4]

    :param dayprefs: 6-character binary string where each bit represents availability for that day (Sunday excluded).
    :return: A list of integers where each element is an available day's index position.
    """
    days = []

    for i in range(0, 6):
        if dayprefs[i] == '1':
            days.append(i)

    return days
