import inspect
import discord
from discord.ext.commands.formatter import HelpFormatter, Paginator
from discord.ext.commands.core import Command
from discord import Embed
from datetime import datetime
from cogs.utils.colors import BOT
from cogs.utils.chat_formatting import inline_list

class Formatter(HelpFormatter):
    def __init__(self):
        super().__init__()

    """Override for the default format method.
    """
    def format(self):
        self._paginator = Paginator()

        description = self.command.description if not self.is_cog() else None

        if description:
            # <description> portion
            self._paginator.add_line(description, empty=True)

        if isinstance(self.command, Command):
            # <signature portion>
            signature = self.get_command_signature()
            self._paginator.add_line(signature, empty=True)

            # end it here if it's just a regular command
            if not self.has_subcommands():
                self._paginator.close_page()
                return self._paginator.pages

        max_width = self.max_name_size

        self._paginator.add_line('Commands:')
        self._add_subcommands_to_page(max_width, self.filter_command_list())

        self._paginator.add_line()
        return self._paginator.pages


class RichEmbed(Embed):
    def __init__(self, ctx, **kwargs):
        author = ctx.message.author
        bot = ctx.bot

        if kwargs['color'] is 'bot':
            kwargs['color'] = BOT
        elif kwargs['color'] is 'author':
            if isinstance(author, discord.Member):
                kwargs['color'] = author.colour
            else:
                kwargs['color'] = BOT

        super().__init__(**kwargs, timestamp=datetime.utcnow(), type='rich')

        self.set_footer(text="Requested by: {}".format(author.name),
                        icon_url=author.avatar_url)
        self.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)


    # You can ignore this.
    def __len__(self):
        def clean(arr):
            return [v for v in arr if not not v]

        values = ([f.name for f in self.fields] + 
                  [f.value for f in self.fields] + 
                  [self.title, self.description, self.author.name, self.footer.text])
        
        return sum(clean([len(v) for v in values]))


class HelpEmbed(RichEmbed):
    """Basic embed for the help command, 
    returned when [p]help is called (without any arguments)
    """
    def __init__(self, ctx):
        bot = ctx.bot
        server = ctx.message.server
        g_prefixes = ",  ".join(inline_list(bot.settings.prefixes))
        s_prefixes = '--/--'
        if server:
            s_prefixes = ",  ".join(inline_list(bot.settings.get_server_prefixes(server)))
            s_prefixes = s_prefixes if s_prefixes else "--/--"

        cogs = [type(c).__name__ for c in bot.cogs.values()]

        wiki = "[bot's wiki](https://github.com/Quantomistro3178/PieBot/wiki)"
        support = "[support server](https://discord.gg/rEM9gFN)"
 
        super().__init__(ctx, title="Help",
                          description=("To get help with specific cogs, use `{p}help <cog>`\n"
                                      "To get help with specific commands, use `{p}help <command>`\n"
                                      "For more information about the bot, use `{p}help bot`\n\n"
                                      "You can also visit the {wiki} to get further "
                                      "help, or join the {support} if you have any questions!"
													            ).format(p=ctx.prefix, wiki=wiki, support=support),
                          color='bot')

        self.set_thumbnail(url=bot.user.avatar_url)
        self.add_field(name="Global Prefixes", value=g_prefixes)
        self.add_field(name="Server Prefixes", value=s_prefixes)
        self.add_field(name="Cogs", value="```{}```".format(",  ".join(cogs)), inline=False)


class CmdHelpEmbed(RichEmbed):
    """Help embed for bot commands"""
    def __init__(self, ctx, command):
        formatter = Formatter()

        longdoc = command.help
        base = command.full_parent_name.split(' ')[0]
        base_cmd = "{0}{1}".format(ctx.prefix, base) if base else '--/--'
        cog = command.cog_name if command.cog_name else '--/--'

        codeblock = "\n".join(formatter.format_help_for(ctx, command))

        super().__init__(ctx, title="Help",
                              description=longdoc,
                              color='bot')

        self.add_field(name="Cog", value=cog)
        self.add_field(name="Base Command", value=base_cmd)
        self.add_field(name="Command Usage:", value=codeblock, inline=False)
        
class CmdUsageEmbed(RichEmbed):
    """Command Usage embed"""
    def __init__(self, ctx, command):
        formatter = Formatter()

        codeblock = "\n".join(formatter.format_help_for(ctx, command))

        super().__init__(ctx, title="Command Usage",
                              description=codeblock,
                              color='bot')

class CogHelpEmbed(RichEmbed):
    """Help embed for cogs"""
    def __init__(self, ctx, cog):
        formatter = Formatter()

        descrip = inspect.getdoc(cog)

        codeblock = "\n".join(formatter.format_help_for(ctx, cog))

        super().__init__(ctx, title="Help [{.__class__.__name__}]".format(cog),
                              description="{0}\n{1}".format(descrip, codeblock),
                              color='bot')


class BotHelpEmbed(RichEmbed):
    """Help embed for the bot itself"""
    def __init__(self, ctx):
        discordpy = "[discord.py](https://github.com/Rapptz/discord.py)"
        red = "[Red V2](https://github.com/Cog-Creators/Red-DiscordBot)"
        piebot = "[PieBot](https://github.com/Quantomistro3178/PieBot)"
        support = "[support server](https://discord.gg/rEM9gFN)"
        
        descrip = ("This bot is an instance of {piebot}, an open-source, "
								  "self-hosted role playing / trading card game bot. "
                  "PieBot uses the {discordpy} library for interacting"
									"with the Discord API, and was originally forked from {red}.\n\n"
                  "For further questions, feel free to visit the {support}!"
				          ).format(piebot=piebot, discordpy=discordpy, red=red, support=support)

        super().__init__(ctx, title="Bot Info",
                              description=descrip,
                              color='bot')
				
        self.add_field(name="PieBot Version", value=ctx.bot.version)
        self.add_field(name="License", value="[GPL-3.0 License](https://github.com/Quantomistro3178/PieBot/blob/master/LICENSE)")
        self.add_field(name="Wiki", value="[Link](https://github.com/Quantomistro3178/PieBot/wiki)")
