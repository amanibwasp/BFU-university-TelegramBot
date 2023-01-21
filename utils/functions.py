import datetime
import pytz


def get_tz():
    return pytz.timezone('Etc/GMT-2')


def datetime_kld():
    return datetime.datetime.now(tz=get_tz())


def can_i_book(auditorium, time_to_start, duration, booked):
    if time_to_start.replace(tzinfo=get_tz()) < datetime_kld():
        return False

    for b in booked[1:]:
        try:
            if b[-1] != 'Отказано' and b[1] == auditorium:
                start = datetime.datetime.fromisoformat(b[2])
                end = datetime.datetime.fromisoformat(b[3])
                if time_to_start <= start <= time_to_start + duration or \
                        time_to_start <= end <= time_to_start + duration or \
                        start <= time_to_start <= end or \
                        start <= time_to_start + duration <= end:
                    return False
        except Exception as ex:
            return False
    return True
