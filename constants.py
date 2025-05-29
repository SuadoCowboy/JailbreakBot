from dotenv import load_dotenv
import discord

load_dotenv()

client: discord.Client = None # type: ignore

GUILD_ID = 1376602598769168555
CLIENT_ID = 1376983057516466186
OWNER_ID = 309806482084462592
SAY_WHITELIST_IDS = [453745871755018241]

def isOwner(interaction: discord.Interaction):
	return interaction.user.id == OWNER_ID
