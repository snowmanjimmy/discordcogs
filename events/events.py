import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help
import os.path
import time
import random
import json

try:
    from prettytable import PrettyTable
    ptAvailable = True
except:
    ptAvailable = False



class Events:
    """Cog for the Red Discord bot -- used to plan events."""

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/events/"

    # Function to add attendee to an existing event - will be called with the !event rsvp function -- may be removed and
    # integrated into the !event rsvp command itself
    def add_attendee(self, eventid, attendee):
        with open(self.file_path + eventid + ".json") as f:
            newdata = dataIO.load_json(f)

        newdata[eventid]["attending"].append(attendee)

        with open(self.file_path + eventid + ".json") as f:
            dataIO.save_json(f, newdata)

    # Creating a command group due to multiple commands with the parameter
    # 'event' existing.
    @commands.group(pass_context=True)
    async def events(self, ctx):
        """Here's what you can do with events. Please note that the commands are case-sensitive."""

        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    # Command to create events
    @events.command(name="create", pass_context=True)
    async def _events_create(self, ctx, eventname : str, eventdate : str, *, eventdesc : str):
        """Create an event.  Requires a single string as an event name, a date, and a description.\n
        Date must be in the YYYY/MM/DD format. \n
        Ex: !event create TestEvent 2009/02/09 This is a test event
        """


        user = ctx.message.author
        eventid = str(random.randint(10000, 99999))
        temp_filename = eventid + ".json"
        temp_path = os.path.join(self.file_path, temp_filename)
        print(temp_path)
        if not os.path.isfile(temp_path):
            f = temp_path
            if not dataIO.is_valid_json(f):
                print("Creating empty" + eventid + ".json...")
                dataIO.save_json(f, {})
        else:
            eventid = str(random.randint(10000, 99999))

        await self.bot.say("Event with ID **#" + eventid + "** created by " + user.mention)

        with open(temp_path) as f:
            newdata = json.load(f)

        data = {"eventName": eventname, "eventOrganizer": str(user), "eventDate": eventdate, "attending": []}

        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)

        #dataIO.save_json(self.file_path, data)



    # List all events -- maybe add ability to accept a 3rd parameter for number of days or 'all'
    @events.command(name="list", pass_context=False)
    async def _events_list(self):
        """List all events"""

        eventlist = self.all_events
        await self.bot.say(eventlist)

    # RSVP to an existing event
    @events.command(name="rsvp", pass_context=True)
    async def _events_rsvp(self, ctx, eventid):
        """RSVP to an existing event by Event ID"""

        user = ctx.message.author
        userstr = str(user)

        appendfilename = eventid + ".json"
        appendpath = os.path.join(self.file_path, appendfilename)
        if os.path.isfile(appendpath):
            with open(appendpath) as f:
                newdata = json.load(f)

            newdata["attending"].append(userstr)
            with open(appendpath, 'w') as f:
                json.dump(newdata, f, indent=4, sort_keys=True)
            await self.bot.say(user.mention + " successfully RSVP'd to Event with ID **" + eventid +"**.")
        else:
            await self.bot.say("No event with the ID #**" + eventid + "** was found.")



    # Delete an existing event by Event ID
    @events.command(name="delete", pass_context=True)
    async def _events_delete(self, ctx, eventid):
        """Delete an existing event by Event ID"""

        user = str(ctx.message.author)
        deletefilename = eventid + ".json"
        deletepath = os.path.join(self.file_path, deletefilename)
        if os.path.isfile(deletepath):
            os.remove(deletepath)
            await self.bot.say(user.mention + " deleted event with ID **#" + eventid + "**")
        else:
            await self.bot.say("No event with the ID #**" + eventid + "** was found.")


def check_folders():
    if not os.path.exists("data/events"):
        print("Creating data/events folder...")
        os.makedirs("data/events")

def check_files():
    f = "data/events/events.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty events.json...")
        dataIO.save_json(f, {})


def setup(bot):
    check_folders()
    check_files()
    if ptAvailable:
        bot.add_cog(Events(bot))
    else:
        raise RuntimeError("You need to run **pip3 install prettytable**")
