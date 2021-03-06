from discord.ext import commands, tasks
from discord.ext.commands import MemberConverter, RoleConverter, TextChannelConverter
import pickle
import discord
from itertools import count
import time


def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Mod(bot))


class Mod(commands.Cog):
    """Commands for server moderation."""
    def __init__(self, bot):
        self.bot = bot
        self.update_mutes.start()

    def setup(self):
        pass

    @tasks.loop(seconds=30)
    async def update_mutes(self):
        try:
            globalconfig = pickle.load(open("config", "rb"))
        except EOFError or KeyError:
            globalconfig = {}
        for x in self.bot.guilds:
            try:
                config = globalconfig[x.id]
            except KeyError:
                config = {}
            try:
                mutes = config["mutes"]
            except KeyError:
                mutes = {}
            print(config)
            print(globalconfig)
            logchannel = x.get_channel(config["logchannel"])
            removemutes = []
            for y in mutes.keys():
                y = x.get_member(y)
                mutefinished = mutes[y.id]
                if time.time() > mutefinished:
                    muterole = x.get_role(config["muterole"])
                    await y.remove_roles(muterole)
                    removemutes.append(y.id)
            for z in removemutes:
                mutes.pop(z)
                member = x.get_member(z)
                print("Mute removed from user " + str(member) + " in guild " + str(x.id) + ".")
                await logchannel.send("Mute removed from user " + str(member) + " by auto-unmute.")
            config.update({"mutes": mutes})
            globalconfig.update({x.id: config})
            pickle.dump(globalconfig, open("config", "wb"))

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def config(self, ctx, args):
        """Configures the local server settings of HAL.
        Requires administrator.
        ```//config logchannel
        //config systemchannel
        //config copypasta
        //config read```"""
        try:
            globalconfig = pickle.load(open("config", "rb"))
        except EOFError or KeyError:
            globalconfig = {}
        try:
            config = globalconfig[ctx.guild.id]
        except KeyError:
            config = {}
        if args == "systemchannel":
            q = await ctx.send("Please enter the channel you would like HAL to send server updates in.")
            responsefound = False
            while not responsefound:
                async for message in ctx.channel.history(limit=10):
                    if message.author == ctx.author and message.created_at > q.created_at:
                        response = message
                        responsefound = True
                        break
            systemchannel = await TextChannelConverter().convert(ctx, response.content)
            config.update({"systemchannel": systemchannel.id})
            globalconfig.update({ctx.guild.id: config})
            pickle.dump(globalconfig, open("config", "wb"))
            await ctx.send("System channel set to " + response.content)
        elif args == "logchannel":
            q = await ctx.send("Please enter the channel you would like HAL to send moderation logs and errors in.")
            responsefound = False
            while not responsefound:
                async for message in ctx.channel.history(limit=10):
                    if message.author == ctx.author and message.created_at > q.created_at:
                        response = message
                        responsefound = True
                        break
            logchannel = await TextChannelConverter().convert(ctx, response.content)
            config.update({"logchannel": logchannel.id})
            globalconfig.update({ctx.guild.id: config})
            pickle.dump(globalconfig, open("config", "wb"))
            await ctx.send("Log channel set to" + response.content)
        elif args == "copypasta":
            q = await ctx.send('Please enter "yes" or "no" to configure whether copypasta is enabled on this server.')
            responsefound = False
            while not responsefound:
                async for message in ctx.channel.history(limit=10):
                    if message.author == ctx.author and message.created_at > q.created_at:
                        response = message
                        responsefound = True
                        break
            if response.content == "yes":
                enabled = True
            elif response.content == "no":
                enabled = False
            else:
                await ctx.send ("That is not a valid response")
                return
            config.update({"copypastaenabled": enabled})
            globalconfig.update({ctx.guild.id: config})
            pickle.dump(globalconfig, open("config", "wb"))
            await ctx.send("Copypasta enabled set to " + str(enabled).lower() + ".")
        elif args == "read":
            message = ""
            for x in config.keys():
                try:
                    value = (await TextChannelConverter().convert(ctx, str(config[x]))).mention
                except Exception:
                    value = str(config[x])
                message = message + "\n" + str(x) + ": " + value
            await ctx.send(message)
        elif args == "muterole":
            q = await ctx.send("What would you like the new muted role to be?")
            responsefound = False
            while not responsefound:
                async for message in ctx.channel.history(limit=10):
                    if message.author == ctx.author and message.created_at > q.created_at:
                        response = message
                        responsefound = True
                        break
            answer = response.content
            try:
                muterole = await RoleConverter().convert(ctx, answer)
                config.update({"muterole": muterole.id})
                globalconfig.update({ctx.guild.id: config})
                pickle.dump(globalconfig, open("config", "wb"))
                await ctx.send("Set muted role to " + muterole.name + ".")
            except Exception:
                await ctx.send("Role not found.")
        elif args == "colorposition":
            q = await ctx.send("What position (from the top of the roles list) would you like new colors to be inserted at?")
            rolenumber = len(ctx.guild.roles)
            responsefound = False
            while not responsefound:
                async for message in ctx.channel.history(limit=10):
                    if message.author == ctx.author and message.created_at > q.created_at:
                        response = message
                        responsefound = True
                        break
            answer = int(response.content)
            answer = (len(ctx.guild.roles) - answer) + 1
            position = answer
            config.update({"colorposition": position})
            globalconfig.update({ctx.guild.id: config})
            pickle.dump(globalconfig, open("config", "wb"))
            await ctx.send("Done!")
        elif args == "wipe":
            q = await ctx.send("What config element would you like to wipe?")
            responsefound = False
            while not responsefound:
                async for message in ctx.channel.history(limit=10):
                    if message.author == ctx.author and message.created_at > q.created_at:
                        response = message
                        responsefound = True
                        break
            answer = response.content
            config.pop(answer)
            globalconfig.update({ctx.guild.id: config})
            pickle.dump(globalconfig, open("config", "wb"))

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, args):
        """Bans a user.
        Requires ban users.
        ```//ban <user>```"""
        user = await MemberConverter().convert(ctx, args)
        await user.ban()
        await ctx.send(user.mention + " has been banned.")

    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def mute(self, ctx, *args):
        """Mutes a user for a certain amount of time.
        Requires manage roles.
        ```//mute <user> <number> <units>"""
        try:
            globalconfig = pickle.load(open("config", "rb"))
        except EOFError or KeyError:
            globalconfig = {}
        try:
            config = globalconfig[ctx.guild.id]
        except KeyError:
            config = {}
        try:
            user = await MemberConverter().convert(ctx, args[0])
        except Exception:
            await ctx.send("User not found.")
            return
        try:
            length = int(args[1])
        except Exception:
            await ctx.send("That is not a valid time.")
            return
        try:
            muterole = await RoleConverter().convert(ctx, str(config["muterole"]))
        except KeyError:
            await ctx.send("No muted role found. Use //config muterole to set one.")
            return
        try:
            mutes = config["mutes"]
        except KeyError:
            mutes = {}
        if args[2] == "minutes" or args[2] == "minute":
            length = length * 60
        elif args[2] == "seconds" or args[2] == "second":
            pass
        elif args[2] == "hours" or args[2] == "hour":
            length = length * 3600
        elif args[2] == "days" or args[2] == "day":
            length = length * 86400
        else:
            await ctx.send("Invalid time unit. Using seconds.")
        await user.add_roles(muterole)
        mutes.update({user.id: time.time() + length})
        config.update({"mutes": mutes})
        globalconfig.update({ctx.guild.id: config})
        await ctx.send("User muted.")
        pickle.dump(globalconfig, open("config", "wb"))

    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def bulkdelete(self, ctx, args):
        """Deletes messages in bulk.
        Requires manage messages.
        ```//bulkdelete <# of messages>```"""
        deletionlist = []
        async for message in ctx.channel.history(limit=int(args) + 1):
            deletionlist.append(message)
        await ctx.channel.delete_messages(deletionlist)
        await ctx.send("Deleted " + args + " messages.")

    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def rgive(self, ctx, *args):
        """Gives a user / users a role.
        Requires Manage Roles.
        ```//rgive <user(s)> <role>
        //rgive everyone <role>```"""
        converter = MemberConverter()
        converter2 = RoleConverter()
        if args[0] == "everyone" or args[0] == "@everyone":
            users = ctx.guild.members
        else:
            users = []
            assignments = args.remove(args[-1])
            for user in assignments:
                user = await converter.convert(ctx, user)
                users.append(user)
        role = await converter2.convert(ctx, args[-1])
        await ctx.send("Giving roles...")
        for user in users:
            await user.add_roles(role, reason="Assigned by " + ctx.author.name + ".")
        await ctx.send("Done!")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def embedsend(self, ctx, *args):
        """Sends an embed message of choice in a channel of choice.
        Requires administrator.
        ```//embedsend <channel>```"""
        converter = TextChannelConverter()
        converter2 = RoleConverter()
        try:
            channel = await converter.convert(ctx, args[0])
        except Exception:
            await ctx.send("Please input a channel.")
            return
        embed = discord.Embed(color=0xff0008)
        for x in count(1):
            embed_var = discord.Embed(color=0xff0008)
            embed_var.add_field(name="Name #" + str(x), value="Respond with the name of field #" + str(
                x) + ". If you are done type \"done\". If you would like to include a field with who sent this embed, "
                     "type \"userstamp\". The message will then be sent.    ",
                                inline=False)
            q = await ctx.send(embed=embed_var)
            responsefound = False
            while not responsefound:
                async for message in ctx.channel.history(limit=10):
                    if message.author == ctx.author and message.created_at > q.created_at:
                        response = message
                        responsefound = True
                        break
            answer = response.content
            if answer == "done":
                break
            elif answer == "userstamp":
                embed.add_field(name="__Message Sent By__", value=ctx.author.mention, inline=False)
                break
            embed_var = discord.Embed(color=0xff0008)
            embed_var.add_field(name="Value #" + str(x), value="Respond with the name of field #" + str(x) + ".",
                                inline=False)
            q = await ctx.send(embed=embed_var)
            responsefound = False
            while not responsefound:
                async for message in ctx.channel.history(limit=10):
                    if message.author == ctx.author and message.created_at > q.created_at:
                        response = message
                        responsefound = True
                        break
            answer2 = response.content
            embed.add_field(name=answer, value=answer2 + "\n", inline=False)
        try:
            if args[1] == "everyone":
                await channel.send("@everyone\n", embed=embed)
            elif args[1] == "here":
                await channel.send("@here\n", embed=embed)
            else:
                rolemention = await converter2.convert(ctx, args[1])
                await channel.send(rolemention.mention + "\n", embed=embed)
        except Exception:
            await channel.send(embed=embed)
        await ctx.send("Message sent!")
