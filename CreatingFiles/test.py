import re
import datetime

iso_datetime_str = '2023-04-10T07:48:09.033+09:00'
iso_format_str = '%Y-%m-%dT%H:%M:%S.%f%z'
re_iso_datetime_str = re.sub('([0-9]{2}):([0-9]{2})$',r'\1\2',iso_datetime_str)
print(re_iso_datetime_str)
print(datetime.datetime.strptime(re_iso_datetime_str, iso_format_str))
