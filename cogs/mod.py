from discord.ext import commands
from discord.ext.commands import MemberConverter, RoleConverter


def setup(bot):
    bot.add_cog(Mod(bot))


class Mod(commands.Cog):
    """Commands for server moderation."""
    def __init__(self, bot):
        self.bot = bot

    def setup(self):
        pass

    @commands.command()
    async def ban(self, ctx, args):
        """Adds the next banned role to a user."""
        if any([aghbo.permissions.manage_roles for aghbo in ctx.author.roles]):
            converter = MemberConverter()
            converter2 = RoleConverter()
            banroleids = [738456842707140700, 742128809129803806, 742128992286670910, 742129191277035590]
            for cycl in range(0, len(args.split())):
                user = await converter.convert(ctx, args.split()[cycl])
                userbanroles = []
                for bancycle in banroleids:
                    for x in user.roles:
                        if x.id == bancycle:
                            userbanroles.append(x.id)
                    if bancycle not in userbanroles:
                        break
                if len(userbanroles) != 0:
                    x = userbanroles[-1]
                else:
                    x = 0
                print(userbanroles)
                print(x)
                if x == 0:
                    y = await converter2.convert(ctx, "738456842707140700")
                    await user.add_roles(y)
                    await ctx.send("Ban role " + str(y) + " successfully added to user " + args.split()[cycl])
                elif x != 742129191277035590:
                    y = await converter2.convert(ctx, str(banroleids[banroleids.index(x) + 1]))
                    await user.add_roles(y)
                    [await user.remove_roles(thisshouldntbeplural) for thisshouldntbeplural in
                     ([await converter2.convert(ctx, str(banroleids[z])) for z in range(0, banroleids.index(x) + 1)])]
                    await ctx.send("Ban role " + str(y) + " successfully added to user " + args.split()[cycl])
                else:
                    await ctx.send("User " + args.split()[cycl] + " hath been yeeted")
                    await user.ban()
        else:
            await ctx.send("You do not have permission to use this command")

    @commands.command()
    async def yeet(self, ctx, args):
        '''ACTUALLY bans a user.'''
        if (any([aghbo.permissions.ban_members for aghbo in ctx.author.roles])):
            converter = MemberConverter()
            user = await converter.convert(ctx, args)
            await user.ban()
        else:
            await ctx.send("You do not have permission to use this command.")