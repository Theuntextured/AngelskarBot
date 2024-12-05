from datetime import datetime, timedelta, timezone
import util
import asyncio
from sql_link import link as sql_link


class Practice:
    def __init__(self, date_time: datetime, ping_stand_ins: bool, team, loaded_in = False):
        self.cancelled = False
        self.datetime = date_time
        self.ping_stand_ins = ping_stand_ins
        self.team = team
        self._schedule_hour_reminder()
        self._schedule_now_reminder()

        if not loaded_in:
            sql_link.cursor.execute(f"INSERT INTO practices VALUES ('{team.name}', {int(date_time.timestamp())}, {int(ping_stand_ins)})")
            sql_link.database.commit()
    
    def _schedule_hour_reminder(self):
        date_to_schedule = self.datetime - timedelta(hours=1)
        if datetime.now(timezone.utc) > date_to_schedule:
            return
        self.hour_schedule = util.ScheduleByFunction(date_to_schedule, self.post_hour_reminder)
        self.hour_task = asyncio.create_task(self.hour_schedule.start_checking())
        
    
    def _schedule_now_reminder(self):
        self.now_schedule = util.ScheduleByFunction(self.datetime, self.post_now_reminder)
        self.now_task = asyncio.create_task(self.now_schedule.start_checking())
        
    def safe_delete(self):
        try:
            self.team.practices.remove(self)
            self.cancelled = True
            sql_link.cursor.execute(f"DELETE FROM practices WHERE (team = '{self.team.name}' and datetime = {int(self.datetime.timestamp())})")
            sql_link.database.commit()

        finally:
            del self

    async def post_hour_reminder(self):
        if self.cancelled:
            return
        timestamp = int(self.datetime.timestamp())
        await self.team.schedule_channel.send(f"{self.team.get_mention(self.ping_stand_ins)} Remember about the scheduled practice <t:{timestamp}:R>! (at <t:{timestamp}:t>)")

    async def post_now_reminder(self):
        if self.cancelled:
            return
        await self.team.schedule_channel.send(f"{self.team.get_mention(self.ping_stand_ins)} Join the voice channel! It is time for team practice!")
        self.safe_delete()

    async def cancel_practice(self):
        self.cancelled = True
        timestamp = int(self.datetime.timestamp())
        await self.team.schedule_channel.send(f"Team practice on <t:{timestamp}:F> has been cancelled.")