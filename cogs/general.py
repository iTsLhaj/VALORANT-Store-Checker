
import discord
import random
import asyncio

from discord.commands import slash_command, Option
from discord.ext.commands.errors import MissingPermissions
from discord.ext import commands, tasks

servers = [949138372130119740]

class general(commands.Cog):
	"""docstring for general"""
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'-{self.__class__.__name__}')

	@slash_command(guild_ids=servers, name="clear", description="clean this sh*t")
	async def clear(self, ctx, messages: Option(int, description="Count? 0 for all", required=True)):
		if messages == 0:
			await ctx.channel.purge()
		else:
			await ctx.channel.purge(limit=messages)

		await ctx.respond("Done")
		await asyncio.sleep(2)
		await ctx.delete()
      


def setup(bot):
	bot.add_cog(general(bot))