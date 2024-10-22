from datetime import datetime, timedelta, timezone
import util
import asyncio

class Practice:
    def __init__(self, date_time: datetime, ping_stand_ins: bool, team):
        self.datetime = date_time
        self.ping_stand_ins = ping_stand_ins
        self.team = team
        self._schedule_hour_reminder()
        self._schedule_now_reminder()
    
    def _schedule_hour_reminder(self):
        date_to_schedule = self.datetime - timedelta(hours=1)
        if datetime.now(timezone.utc) > date_to_schedule:
            return
        self.hour_schedule = util.ScheduleByFunction(date_to_schedule, self.post_hour_reminder)
        self.hour_task = asyncio.create_task(self.hour_schedule.start_checking())
        
    
    def _schedule_now_reminder(self):
        self.now_schedule = util.ScheduleByFunction(self.datetime, self.post_now_reminder)
        self.now_task = asyncio.create_task(self.now_schedule.start_checking())
        

    async def post_hour_reminder(self):
        timestamp = int(self.datetime.timestamp())
        await self.team.info_channel.send(f"{self.team.get_mention(self.ping_stand_ins)} Remember about the scheduled practice <t:{timestamp}:R>! (at <t:{timestamp}:t>)")

    async def post_now_reminder(self):
        await self.team.info_channel.send(f"{self.team.get_mention(self.ping_stand_ins)} Join the voice channel! It is time for team practice!")
        try:
            self.team.practices.remove(self)
        finally:
            del self

    async def cancel_practice(self):
        timestamp = int(self.datetime.timestamp())
        await self.team.info_channel.send(f"Team practice on <t:{timestamp}:F> has been cancelled.")
        try:
            self.team.practices.remove(self)
        finally:
            del self