from app.models import UserType, TimePreference, Job


def get_suitable_jobs(jobs, time_prefs, day_prefs):
    suitable_jobs = []
    available_days = get_day_prefs(day_prefs)

    for job in jobs:
        if job.date.weekday() in available_days:
            if job.time in time_prefs or time_prefs == 'AP':
                suitable_jobs.append(job)

    return suitable_jobs


def get_day_prefs(day_prefs):
    days = []

    for i in range(0, 6):
        if day_prefs[i] == '1':
            days.append(i)

    return days


def day_pref_to_binary(day_prefs):
    binary = ['0', '0', '0', '0', '0', '0']

    for day_pref in day_prefs:
        binary[int(day_pref)] = '1'

    return ''.join(binary)


def user_type_pretty(user_type):
    return str(UserType(user_type))


def time_pref_pretty(time_pref):
    return str(TimePreference(time_pref))


def day_prefs_pretty(day_prefs):
    if not day_prefs or day_prefs == '000000':
        return ''

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    pretty = []

    for i in range(0, 6):
        if day_prefs[i] == '1':
            pretty.append(days[i])

    return pretty


def timestamp_pretty(timestamp, show_time=True):
    if not show_time:
        return timestamp.strftime('%d %B %Y (%A)')

    return timestamp.strftime('%d %B %Y at %H:%M')


def past_jobs_pretty():
    past_jobs = []

    for job in Job.get_past_jobs():
        past_jobs.append((str(job.id), '{} on {}, {}'.format(job.address, timestamp_pretty(job.date, show_time=False), job.time)))

    return past_jobs
