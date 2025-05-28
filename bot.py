import discord
from constants import *

import json
import random
import os
import asyncio

#from keep_alive import keep_alive

sounds = os.listdir('sounds')

def save_guilds_file(guildId, content):
	guilds[guildId] = content
	with open('guilds.json','w') as f:
		return json.dump(guilds, f, indent=4)

def get_guilds():
	guilds = {}

	with open('guilds.json','r') as f:
		guilds = json.load(f)

		for guild in guilds.copy():
			guilds[int(guild)] = guilds[guild]
			guilds.pop(guild)

	return guilds

guilds = get_guilds()

def create_guild(guildId):
	guilds[guildId] = {}
	guilds[guildId]['binds'] = {}
	save_guilds_file(guildId, guilds[guildId])

with open('fire_arguments.txt', 'r', encoding='utf-8') as f:
	fireArgs = f.readlines()

binds = json.load(open('binds.json', 'r', encoding='utf-8'))

class JailbreakBot(discord.Client):
	async def on_ready(self):
		await tree.sync(guild=discord.Object(GUILD_ID))
		print(f'Logged in as {self.user}!')

	async def on_join(self, guild: discord.Guild):
		create_guild(guild.id)

	async def on_message(self, message: discord.Message):
		if message.author.id == CLIENT_ID:
			return

		content = message.content.lower().strip() # say bind content if bind is typed

		if content in binds:
			await message.channel.send(binds[content])
			return

		if message.guild != None and content in guilds[message.guild.id]['binds']:
			await message.channel.send(guilds[message.guild.id]['binds'][content])

intents = discord.Intents.default()
intents.message_content = True
#intents.dm_messages = True

client = JailbreakBot(intents=intents)
tree = discord.app_commands.CommandTree(client)

@tree.command(
	name="sound",
	description="Plays a sound in the voice channel",
	guild=discord.Object(GUILD_ID)
)
@discord.app_commands.choices(sound=[discord.app_commands.Choice(name=sound, value=sound) for sound in sounds])
async def sound_command(interaction: discord.Interaction, sound: str):
	await interaction.response.defer(ephemeral=True, thinking=True)

	if interaction.user.voice:
		vc = await interaction.user.voice.channel.connect(self_deaf=True)

		vc.play(discord.FFmpegPCMAudio(source=os.path.join('sounds', sound)))
		while vc.is_playing():
			await asyncio.sleep(0.1)

		await vc.disconnect()
	else:
		await interaction.followup.send("Você não está em um canal de voz", ephemeral=True)

@tree.command(name='binds', guild=discord.Object(GUILD_ID))
async def binds_command(interaction: discord.Interaction):
	await interaction.response.defer(ephemeral=True, thinking=True)

	content = ''
	for i in binds:
		content += i + ' | '
	content = content[:-3]  # Remove the last ' | '

	while len(content) > 2000:
		out = content[:2000]
		content = content[2000:]
		await interaction.channel.send(out)

	await interaction.channel.send(content)

@tree.command(name='fire', guild=discord.Object(GUILD_ID))
async def fire_command(interaction: discord.Interaction):
	await interaction.response.defer(ephemeral=True, thinking=False)
	await interaction.channel.send(f'{interaction.user.display_name} deseja despejar o diretor (-1 restante)')
	await interaction.channel.send(random.choice(fireArgs))

@tree.command(name='add_bind', guild=discord.Object(GUILD_ID))
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def add_bind_command(interaction: discord.Interaction, bind_name: str, bind_output: str):
	bind_name = bind_name.replace('_',' ')

	if bind_name not in binds or bind_name in guilds[interaction.guild.id]['binds']:
		guilds[interaction.guild.id]['binds'][bind_name] = bind_output
		save_guilds_file(interaction.guild.id, guilds[interaction.guild.id])
		await interaction.response.send_message(f'bind \"{bind_name}\" criada')

	else:
		await interaction.response.send_message(f'bind \"{bind_name}\" já existe.')

@tree.command(name='remove_bind', guild=discord.Object(GUILD_ID))
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def remove_bind_command(interaction: discord.Interaction, bind_name: str):
	bind_name = bind_name.replace('_',' ')
	if bind_name in guilds[interaction.guild.id]['binds']:
		guilds[interaction.guild.id]['binds'].pop(bind_name)
		save_guilds_file(interaction.guild.id, guilds[interaction.guild.id])
		await interaction.response.send_message(f'A bind \"{bind_name}\" foi removida.')
	else:
		await interaction.response.send_message('Esse servidor nao tem essa bind')

@tree.command(name='color', guild=discord.Object(GUILD_ID))
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def color_command(interaction: discord.Interaction, hex_color: str):
	await interaction.response.defer(ephemeral=True, thinking=True)

	if hex_color.startswith('#'):
		hex_color = hex_color[1:]
	elif hex_color.startswith('0x'):
		hex_color = hex_color[2:]

	try:
		hex_color = int(hex_color, 16)
	except:
		await interaction.followup.send("Cor hexadecimal inválida")

	for role in interaction.user.roles:
		if role.name == interaction.user.display_name:
			role = await role.edit(color=hex_color)
			await interaction.user.add_roles(role)
			return

	role = await interaction.guild.create_role(name=interaction.user.display_name, color=hex_color)
	await interaction.user.add_roles(role)

def isOwnerOrFahel(interaction: discord.Interaction):
	return interaction.user.id == OWNER_ID or interaction.user.id == FAHEL_ID

@tree.command(name='fahel', guild=discord.Object(GUILD_ID))
@discord.app_commands.choices(arguments=[
	discord.app_commands.Choice(name='fire', value='fire'),
	discord.app_commands.Choice(name='fahel.', value='fahel.'),
	discord.app_commands.Choice(name='<@453745871755018241>', value='<@453745871755018241>')
])
@discord.app_commands.check(isOwnerOrFahel)
async def fahel_command(interaction: discord.Interaction, arguments: str):
	await interaction.response.defer(ephemeral=True, thinking=True)

	if arguments == 'fire':
		await interaction.channel.send('Fahel quer despejar o diretor.')
	elif arguments == 'fahel.':
		await interaction.channel.send('Fahel.')
	elif arguments == '<@453745871755018241>':
		await interaction.channel.send('Fahel gameplays original 2077 100% original.')
	elif arguments == 'STF É UMA FACÇÃO CRIMINOSA DA MAÇONARIA SATÂNICA ALERTA DAVINCCI SÓCIO DA CAMARGO CORRÊA JUDEUS SIONISTAS COMANDA A MAIOR ORGANIZAÇÃO CRIMINOSA DO MUNDO A MAÇONARIA . JUDICIÁRIO É UMA FACÇÃO CRIMINOSA DA MAÇONARIA SATÂNICA FORÇAS ARMADAS É UMA FACÇÃO CRIMINOSA DA MAÇONARIA SATÂNICA ALERTA DAVINCCI . FAZ O NARCOTRÁFICO PARA INDÚSTRIA FARMACÊUTICA CHINA COM ISRAEL. O NARCOTRÁFICO DAS INDÚSTRIAS FARMACÊUTICA DA MAÇONARIA PARA 150 PAÍSES':
		await interaction.channel.send('PUTA QUE ME PARIU')
	else:
		await interaction.channel.send('Seu argumento é fraco.')

	await interaction.response.defer(ephemeral=True)

#keep_alive()
client.run(os.getenv('DISCORD_BOT_TOKEN')) # type: ignore