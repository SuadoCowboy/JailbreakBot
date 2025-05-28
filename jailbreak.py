from discord.ext import commands
from discord.utils import get
import json
import emojis
from replit_hugo import hugo as hugao
from threading import Thread
import time

owner_id = 309806482084462592
max_x = 41 # in my 1900x600 screen on google.

def get_servers():
    with open('servers.json','r') as f:
        return json.load(f)

guilds = get_servers()

class Player:
    def __init__(self, id, emoji, lives=2, x=5, y=5):
        self.id = id
        self.lives = lives
        self.emoji = emoji
        self.x = x
        self.y = y
    
    def hit(self):
        self.lives -= 1
        if self.lives <= 0:
            return 'dead'

class Jailbreak:
    def __init__(self, channel, min_players: int, max_players: int, width, height, player_lives, background=':black_large_square:'):
        self.channel = channel
        self.min_players = min_players
        self.max_players = max_players
        self.width = width
        self.height = height
        self.player_lives = player_lives
        self.background = background
        self.last_command_time = 0
        self.timeout = 1200.0 # 20 minutos

        self.players = {}

        self.started = False
        
        self.warden = None
        self.guards = []
        self.prisioners = []

        self.blocks = []

    def join_game(self, playerid, emoji):
        self.last_command_time = 0

        if len(self.players) == self.max_players:
            return False
        self.players[playerid] = Player(playerid, emoji, self.player_lives)

    def leave_game(self, playerid):
        self.last_command_time = 0

        if playerid in self.players:
            del(self.players[playerid])

    def start_game(self):
        self.last_command_time = 0

        if len(self.players) < self.min_players:
            return False
        self.started = True

        return self.draw()

    def draw(self):
        self.last_command_time = 0

        map = ['']
        yy = 0
        for y in range(self.height):
            for x in range(self.width):
                for player in self.players:
                    player = self.players[player]
                    if y == player.y and x == player.x:
                        map[-1] += player.emoji
                    else:
                        map[-1] += emojis.encode(self.background)
            map[-1] += '\n'
            if yy == 3:
                map.append('')
                yy = -1
            yy += 1

        return map

    def restart_game(self):
        self.last_command_time = 0

        for player in self.players:
            del(self.players[player])
        self.players = {}
        self.map = ''
        self.guards = []
        self.warden = None
        self.prisioners = []
        self.started = False

    def kick_player(self, playerid):
        if playerid in self.players:
            del(self.players[playerid])

class BaseMinigame: # criar uma classe base pra minigames
    def __init__(self, min_players=2, max_players=-1):
        self.min_players = min_players
        self.max_players = max_players
        self.players = {}
    
    def start(self):
        pass
    
    def join(self, playerid, player):
        self.players[playerid] = player

jailbreaks = {}

def get_prefix(_client, message):
    if str(message.guild.id) in guilds:
        return guilds[str(message.guild.id)]['prefix']
    else:
        return '.'

client = commands.Bot(command_prefix=get_prefix, help_command=None)
with open('token.txt','r') as f:
    token = f.read()

def jb_check_timeout():
    while running:
        time.sleep(1)
        for jb in jailbreaks.copy():
            jailbreaks[jb].last_command_time += 1
            if jailbreaks[jb].last_command_time >= jailbreaks[jb].timeout:
                del(jailbreaks[jb])

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    t = Thread(target=jb_check_timeout)
    t.start()

@client.command(name='join_game')
async def jb_join_game(ctx, *emoji):
    if len(emoji) == 0 or emojis.count(emoji[0]) == 0:
        await ctx.send(emojis.encode('emoji faltando :robot:'))
        return
    if len(emoji) > 1:
        await ctx.send('É só pra usar um emoji seu buro da dYsgraça')
        return
    emoji = emoji[0]

    if jailbreaks[str(ctx.guild.id)].started:
        await ctx.send('O jogo ja foi iniciado... sore ;(')
        return

    if ctx.author.id in jailbreaks[str(ctx.guild.id)].players:
        await ctx.send('Burro pra caralho mano, voce ja ta no jogo seu genio')
        return

    if jailbreaks[str(ctx.guild.id)].join_game(ctx.author.id, emoji) == False:
        await ctx.send('Limite de players alcançado haha perdedor funi')
        return
    await ctx.send(f'{ctx.author.name} entrou no jogo como {emoji} ({len(jailbreaks[str(ctx.guild.id)].players)}/{jailbreaks[str(ctx.guild.id)].max_players})')

@client.command(name='leave_game')
async def jb_leave_game(ctx):
    if jailbreaks[str(ctx.guild.id)].leave_game(ctx.author.id) == False:
        await ctx.send('Você n ta no jogo bobão >:(')
        return
    await ctx.send(f'{ctx.author.name} saiu do jogo ({len(jailbreaks[str(ctx.guild.id)].players)}/{jailbreaks[str(ctx.guild.id)].max_players})')

@client.command(name='start_game')
@commands.has_permissions(manage_guild=True)
async def jb_start_game(ctx):
    if jailbreaks[str(ctx.guild.id)].started:
        await ctx.send('Ja foi iniciado brú') # DEPOIS FAZER NEGOCIO PRA CHECAR SE NGM MAIS TA JOGANDO OU SE O JOGO TA PARADO POR MT TEMPO
        return

    if jailbreaks[str(ctx.guild.id)].min_players <= len(jailbreaks[str(ctx.guild.id)].players):
        maps = jailbreaks[str(ctx.guild.id)].start_game()
        for map in maps:
            if len(map) != 0:
                await ctx.send(map)
        await ctx.send('Iniciado com sucesso')
    else:
        await ctx.send(f'Ainda falta jogadores. ({len(jailbreaks[str(ctx.guild.id)].players)}/{jailbreaks[str(ctx.guild.id)].max_players})')
        return

@client.command(name='draw')
@commands.has_permissions(manage_guild=True)
async def jb_draw(ctx):
    if not str(ctx.guild.id) in jailbreaks or not jailbreaks[str(ctx.guild.id)].started:
        await ctx.send('O jogo ainda não iniciou')
        return

    map = jailbreaks[str(ctx.guild.id)].draw()
    for i in map:
        if len(i) != 0:
            await ctx.send(i)

@client.command(name='init_jailbreak')
@commands.has_permissions(manage_guild=True)
async def init_jailbreak(ctx, channel_name='jailbrek', min_players=2, max_players=12, width=25, height=10, player_lives=2, background=':black_large_square:'):
    if str(ctx.guild.id) in jailbreaks:
        await ctx.send('Jailbreak ja foi inicializado nesse servidor seu genio')
        return
    
    jailbreaks[str(ctx.guild.id)] = Jailbreak(get(ctx.guild.channels, name=channel_name), int(min_players), int(max_players), int(width), int(height), int(player_lives), background)
    await ctx.send(emojis.encode('Jailbreak inicializado nesse servidor e amogusus :pray:'))

@client.command(name='move')
async def jb_move_player(ctx, way, times=1):
    if int(times) >= 3:
        times = 3
    if ctx.author.id in jailbreaks[str(ctx.guild.id)].players:
        player = jailbreaks[str(ctx.guild.id)].players[ctx.author.id]
    else:
        return
    for _ in range(int(times)):
        old_x = player.x
        old_y = player.y
        
        if way == 'w' or way == 'up':
            player.y -= 1
        elif way == 's' or way == 'down':
            player.y += 1
        elif way == 'a' or way == 'left':
            player.x -= 1
        elif way == 'd' or way == 'right':
            player.x += 1
        else:
            await ctx.send('Caminho pode ser apenas wasd ou up, down, left, ou right.')
            return
        
        for block in jailbreaks[str(ctx.guild.id)].blocks:
            if block.type == 'collide' and block.x == player.x and block.y == player.y:
                await ctx.send('Tem um bloco no caminho.')
                return
        for p in jailbreaks[str(ctx.guild.id)].players:
            p = jailbreaks[str(ctx.guild.id)].players[p]
            if p.id != player.id and p.x == player.x and p.y == player.y:
                await ctx.send('Tem um outro player nesse lugar.')
                return
    maps = jailbreaks[str(ctx.guild.id)].draw()
    for map in maps:
        if len(map) != 0:
            await ctx.send(map)

@client.command(name='teleport')
@commands.has_permissions(manage_guild=True)
async def jb_teleport_player(ctx, x, y):
    x = int(x)
    y = int(y)
    if ctx.author.id in jailbreaks[str(ctx.guild.id)].players:
        player = jailbreaks[str(ctx.guild.id)].players[ctx.author.id]

    for block in jailbreaks[str(ctx.guild.id)].blocks:
        if block.type == 'collide' and block.x == x and block.y == y:
            await ctx.send('Tem um bloco na posição especificada.')
            return
    for p in jailbreaks[str(ctx.guild.id)].players:
        p = jailbreaks[str(ctx.guild.id)].players[p]
        if p.id != ctx.guild.id and p.x == x and p.y == y:
            await ctx.send('Tem um outro player nesse lugar.')
            return
    player.x = x
    player.y = y
    maps = jailbreaks[str(ctx.guild.id)].draw()
    for map in maps:
        await ctx.send(map)

@client.command(name='hugo')
async def hugo(ctx, *args):
    await hugao(ctx, *args)

running = True
client.run(token)
running = False