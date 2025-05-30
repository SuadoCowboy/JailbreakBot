import discord
from constants import *

import json
import random
import os
import asyncio

#from keep_alive import keep_alive

sounds = os.listdir('sounds')

#def save_guilds_file(guildId, content):
#	guilds[guildId] = content
#	with open('guilds.json', 'w', encoding='utf-8') as f:
#		return json.dump(guilds, f, indent=4)

def save_binds_file():
	with open('binds.json', 'w', encoding='utf-8') as f:
		return json.dump(binds, f, indent=4)

#def get_guilds():
#	guilds = {}
#
#	with open('guilds.json','r') as f:
#		guilds = json.load(f)
#
#		for guild in guilds.copy():
#			guilds[int(guild)] = guilds[guild]
#			guilds.pop(guild)
#
#	return guilds

#guilds = get_guilds()

#def create_guild(guildId):
#	guilds[guildId] = {}
#	guilds[guildId]['binds'] = {}
#	save_guilds_file(guildId, guilds[guildId])

binds = json.load(open('binds.json', 'r', encoding='utf-8'))

class JailbreakBot(discord.Client):
	async def on_ready(self):
		await tree.sync()
		print(f'Logged in as {self.user}!')

#	async def on_join(self, guild: discord.Guild):
#		create_guild(guild.id)

	async def on_message(self, message: discord.Message):
		if message.author.id == CLIENT_ID:
			return

		content = message.content.lower().strip() # say bind content if bind is typed

		if content in binds:
			await message.channel.send(binds[content])
			return

#		if message.guild != None and content in guilds[message.guild.id]['binds']:
#			await message.channel.send(guilds[message.guild.id]['binds'][content])

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

client = JailbreakBot(intents=intents)
tree = discord.app_commands.CommandTree(client)

@tree.command(
	name='sound',
	description='Plays a sound in the voice channel',
#	guild=discord.Object(GUILD_ID)
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
		await interaction.delete_original_response()
	else:
		await interaction.followup.send("Você não está em um canal de voz", ephemeral=True)

@tree.command(
	name='binds',
#	guild=discord.Object(GUILD_ID)
)
async def binds_command(interaction: discord.Interaction, ephemeral: bool=True):
	await interaction.response.defer(ephemeral=ephemeral, thinking=True)

	content = ''
	for i in binds:
		content += i + ' | '
#	for i in guilds[interaction.guild.id]['binds']:
#		content += i + ' | '
	content = content[:-3]  # Remove the last ' | '

	while len(content) > 2000:
		out = content[:2000]
		content = content[2000:]
		await interaction.channel.send(out)

	await interaction.followup.send(content, ephemeral=ephemeral)

@tree.command(
	name='fire',
	#guild=discord.Object(GUILD_ID)
)
async def fire_command(interaction: discord.Interaction):
	await interaction.response.defer(ephemeral=True, thinking=False)
	await interaction.delete_original_response()

	await interaction.channel.send(f'{interaction.user.display_name} deseja despejar o diretor (-1 restante)')

@tree.command(
	name='addbind',
#	guild=discord.Object(GUILD_ID)
)
@discord.app_commands.check(isOwner)
async def addbind_command(interaction: discord.Interaction, bind_name: str, bind_output: str):
	bind_name = bind_name.replace('_',' ')

	if bind_name not in binds: #and bind_name not in guilds[interaction.guild.id]['binds']:
		#guilds[interaction.guild.id]['binds'][bind_name] = bind_output
		#save_guilds_file(interaction.guild.id, guilds[interaction.guild.id])
		binds[bind_name] = bind_output
		save_binds_file()
		await interaction.response.send_message(f'bind \"{bind_name}\" criada')

	else:
		await interaction.response.send_message(f'bind \"{bind_name}\" já existe.')

@tree.command(name='removebind', guild=discord.Object(GUILD_ID))
@discord.app_commands.check(isOwner)
async def removebind_command(interaction: discord.Interaction, bind_name: str):
	await interaction.response.defer(ephemeral=True, thinking=True)

	bind_name = bind_name.replace('_',' ')

	if bind_name in binds: #guilds[interaction.guild.id]['binds']:
	#	guilds[interaction.guild.id]['binds'].pop(bind_name)
		binds.pop(bind_name)
		#	save_guilds_file(interaction.guild.id, guilds[interaction.guild.id])
		save_binds_file()
		await interaction.edit_original_response(content=f'A bind \"{bind_name}\" foi removida.')
	else:
		await interaction.edit_original_response(content='Bind inexistente') #'Esse servidor nao tem essa bind')

@tree.command(name='color', guild=discord.Object(GUILD_ID))
async def color_command(interaction: discord.Interaction, hex_color: str):
	await interaction.response.defer(ephemeral=True, thinking=True)

	if hex_color.startswith('#'):
		hex_color = hex_color[1:]
	elif hex_color.startswith('0x'):
		hex_color = hex_color[2:]

	try:
		hex_color = int(hex_color, 16)
		if hex_color > 0xffffff:
			await interaction.followup.send('Cor hexadecimal não pode ser mais do que #ffffff')
			return
	except Exception as e:
		await interaction.followup.send("Cor hexadecimal inválida")
		return

	for role in interaction.user.roles:
		if role.name == interaction.user.display_name:
			role = await role.edit(color=hex_color)
			await interaction.user.add_roles(role)
			await interaction.delete_original_response()
			return

	role = await interaction.guild.create_role(name=interaction.user.display_name, color=hex_color)
	await interaction.user.add_roles(role)
	await interaction.delete_original_response()

async def say_command_text_autocomplete(interaction: discord.Interaction, _current: str):
	return [
		discord.app_commands.Choice(name='STF', value='STF')
	]

def say_command_whitelist(interaction: discord.Interaction):
	return interaction.user.id in SAY_WHITELIST_IDS + [OWNER_ID]

@tree.command(name='say', guild=discord.Object(GUILD_ID))
@discord.app_commands.autocomplete(text=say_command_text_autocomplete)
@discord.app_commands.check(say_command_whitelist)
async def say_command(interaction: discord.Interaction, text: str):
	await interaction.response.defer(ephemeral=True, thinking=True)

	print(f'{interaction.user.display_name}: {text}')

	if text == 'STF':
		await interaction.channel.send('STF É UMA FACÇÃO CRIMINOSA DA MAÇONARIA SATÂNICA ALERTA DAVINCCI SÓCIO DA CAMARGO CORRÊA JUDEUS SIONISTAS COMANDA A MAIOR ORGANIZAÇÃO CRIMINOSA DO MUNDO A MAÇONARIA . JUDICIÁRIO É UMA FACÇÃO CRIMINOSA DA MAÇONARIA SATÂNICA FORÇAS ARMADAS É UMA FACÇÃO CRIMINOSA DA MAÇONARIA SATÂNICA ALERTA DAVINCCI . FAZ O NARCOTRÁFICO PARA INDÚSTRIA FARMACÊUTICA CHINA COM ISRAEL. O NARCOTRÁFICO DAS INDÚSTRIAS FARMACÊUTICA DA MAÇONARIA PARA 150 PAÍSES')
	else:
		await interaction.channel.send(text)

	await interaction.delete_original_response()

async def bindsay_command_bind_autocomplete(interaction: discord.Interaction, current: str):
	current = current.lower().strip()

	bindOptions = []
	for bind in binds:
		if not current or bind.startswith(current):
			bindOptions.append(discord.app_commands.Choice(name=bind, value=bind))

	if interaction.guild and interaction.guild.id in guilds:
		for bind in guilds[interaction.guild.id]['binds']:
			if not current or bind.startswith(current):
				bindOptions.append(discord.app_commands.Choice(name=bind, value=bind))

	return bindOptions

@tree.command(name='bindsay')
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@discord.app_commands.autocomplete(bind=bindsay_command_bind_autocomplete)
async def bindsay_command(interaction: discord.Interaction, bind: str, ephemeral: bool=False):
	await interaction.response.defer(ephemeral=ephemeral, thinking=True)

	bind = bind.lower()
	if bind in binds:
		await interaction.edit_original_response(content=binds[bind])
	#elif interaction.guild and interaction.guild.id in guilds and bind in guilds[interaction.guild.id]['binds']:
	#	await interaction.edit_original_response(content=guilds[interaction.guild.id]['binds'])
	else:
		await interaction.edit_original_response(content='Bind inexistente')

#keep_alive()
client.run(os.getenv('DISCORD_BOT_TOKEN')) # type: ignore
