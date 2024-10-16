from datetime import datetime

class Practice:
    def __init__(self, date_time: datetime, ping_stand_ins: bool):
        self.datetime = date_time
        self.ping_stand_ins = ping_stand_ins
