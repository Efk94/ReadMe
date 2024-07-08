import os
import sys

# Dodanie ścieżki do katalogu głównego projektu tylko raz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import discord
from dotenv import load_dotenv
from discord.ext import commands
from StringProgressBar import progressBar
from data.KvkStats import KvkStats
from utils.generate_and_send_image import generate_and_send_image
import json
import pandas as pd

# Załadowanie zmiennych środowiskowych z pliku .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_ID')

if not TOKEN:
    raise ValueError("Brak tokenu. Upewnij się, że plik .env zawiera poprawny token.")
if not GUILD:
    raise ValueError("Brak ID gildii. Upewnij się, że plik .env zawiera poprawny ID gildii.")

# Ustawienia intencji bota
intents = discord.Intents.default()
intents.message_content = True

# Inicjalizacja bota
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Ścieżka do pliku Excel - upewnij się, że ścieżka jest poprawna
file_path = 'C:\\Users\\profo\\OneDrive\\Pulpit\\statystyki — kopia\\2732 statystyki (4).xlsx'
excel_data = pd.read_excel(file_path, engine='openpyxl')

# Check column names
print(excel_data.columns)

kvk_stats = KvkStats(file_path)

# Ścieżka do pliku z przypisaniami
assignments_file = 'assignments.json'
links_file = 'links.json'

# Załaduj dowódców
def load_commanders():
    avatar_folder = r'C:\Users\profo\OneDrive\Pulpit\Nowy folder\Avatar'
    commanders = {}
    for filename in os.listdir(avatar_folder):
        name, _ = os.path.splitext(filename)
        commanders[name] = os.path.join(avatar_folder, filename)
    return commanders

commanders = load_commanders()
emojis = {
    "Alex": "Alex",
    "Amanitore": "Amanitore",
    "Artemisia": "Artemisia",
    "Atilla": "Atilla",
    "Belisariusz": "Belisariusz",
    "Boudica": "Boudica",
    "CaoCao": "CaoCao",
    "Chandragupta": "Chandragupta",
    "Cheok": "Cheok",
    "Constantine": "Constantine",
    "Cyrus": "Cyrus",
    "Czyngischan": "Czyngischan",
    "Dildo": "Dildo",
    "Edward": "Edward",
    "ElCid": "ElCid",
    "Eleanor": "Eleanor",
    "Flavius": "Flavius",
    "Gorgo": "Gorgo",
    "Harald": "Harald",
    "Hendry": "Hendry",
    "Heraclius": "Heraclius",
    "Hermann": "Hermann",
    "Huo": "Huo",
    "Jadwiga": "Jadwiga",
    "JanZizka": "JanZizka",
    "Joan": "Joan",
    "Leonidas": "Leonidas",
    "LiuChe": "LiuChe",
    "Martel": "Martel",
    "MehmedII": "MehmedII",
    "Minamoto": "Minamoto",
    "Nebuchadnezzar": "Nebuchadnezzar",
    "Nevsky": "Nevsky",
    "Pakal": "Pakal",
    "Ramesses": "Ramesses",
    "Richard": "Richard",
    "Saladin": "Saladin",
    "Sargon": "Sargon",
    "Scipio": "Scipio",
    "Takeda": "Takeda",
    "Tariq": "Tariq",
    "Tomyris": "Tomyris",
    "William": "William",
    "XiangYu": "XiangYu",
    "YiSunSin": "YiSunSin",
    "YiSeongGye": "YiSeongGye",
    "Zenobia": "Zenobia",
    "Zhuge": "Zhuge"
}

# Słownik przypisujący tekst emoji do dowódców
emoji_texts = {
    "Alex": ":Alex:",
    "Amanitore": ":Amanitore:",
    "Artemisia": ":Artemisia:",
    "Atilla": ":Atilla:",
    "Belisariusz": ":Belisariusz:",
    "Boudica": ":Boudica:",
    "CaoCao": ":CaoCao:",
    "Chandragupta": ":Chandragupta:",
    "Cheok": ":Cheok:",
    "Constantine": ":Constantine:",
    "Cyrus": ":Cyrus:",
    "Czyngischan": ":Czyngischan:",
    "Dildo": ":Dildo:",
    "Edward": ":Edward:",
    "ElCid": ":ElCid:",
    "Eleanor": ":Eleanor:",
    "Flavius": ":Flavius:",
    "Gorgo": ":Gorgo:",
    "Harald": ":Harald:",
    "Hendry": ":Hendry:",
    "Heraclius": ":Heraclius:",
    "Hermann": ":Hermann:",
    "Huo": ":Huo:",
    "Jadwiga": ":Jadwiga:",
    "JanZizka": ":JanZizka:",
    "Joan": ":Joan:",
    "Leonidas": ":Leonidas:",
    "LiuChe": ":LiuChe:",
    "Martel": ":Martel:",
    "MehmedII": ":MehmedII:",
    "Minamoto": ":Minamoto:",
    "Nebuchadnezzar": ":Nebuchadnezzar:",
    "Nevsky": ":Nevsky:",
    "Pakal": ":Pakal:",
    "Ramesses": ":Ramesses:",
    "Richard": ":Richard:",
    "Saladin": ":Saladin:",
    "Sargon": ":Sargon:",
    "Scipio": ":Scipio:",
    "Takeda": ":Takeda:",
    "Tariq": ":Tariq:",
    "Tomyris": ":Tomyris:",
    "William": ":William:",
    "XiangYu": ":XiangYu:",
    "YiSunSin": ":YiSunSin:",
    "YiSeongGye": ":YiSeongGye:",
    "Zenobia": ":Zenobia:",
    "Zhuge": ":Zhuge:"
}

def get_assigned_commanders(user_id):
    if not os.path.exists(assignments_file):
        return []

    with open(assignments_file, 'r') as f:
        assignments = json.load(f)

    return assignments.get(user_id, {}).get('dowodca', [])

def get_linked_gov_id(user_id):
    if not os.path.exists(links_file):
        return None

    with open(links_file, 'r') as f:
        links = json.load(f)

    return links.get(user_id)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='stats')
async def stats(ctx, gov_id: int = None):
    if gov_id is None:
        gov_id = get_linked_gov_id(str(ctx.author.id))
        if gov_id is None:
            await ctx.send("Nie masz przypisanego `gov_id`. Użyj komendy `!link <gov_id>`, aby przypisać swoje `gov_id`.")
            return

    player_stats = excel_data[excel_data['GOVERNOR ID'] == gov_id]
    if not player_stats.empty:
        player_stats = player_stats.iloc[0]

        embed = discord.Embed(color=0xf56754)
        embed.title = f"📊 Statystyki osobiste dla {player_stats['USERNAME']}"
        embed.set_author(name="2732bot", url="https://lookerstudio.google.com/u/0/reporting/a5831fbc-65a0-4b7a-9213-00beb671ca79/page/p_q674h2m68c",
                         icon_url="https://cdn.discordapp.com/attachments/1237356214099247145/1258308083369902140/tawy.png?ex=66879239&is=668640b9&hm=4e6d5a5f77157b35e08e97bc8d043bf8fd202f09cc4adad6993ad0b216199617&")
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        # Dodanie pól sekcji
        
        embed.add_field(name="💪 Siła", value=f"{player_stats['POWER']:,}", inline=False)
        embed.add_field(name="🔫 Łączna liczba zabójstw", value=f"{player_stats['TOTAL KILLS']:,}", inline=False)
        embed.add_field(name="💀 Zgony", value=f"{player_stats['DEADS']:,}", inline=False)
        
        # Dodanie przypisanych dowódców do embedu
        assigned_commanders = get_assigned_commanders(str(ctx.author.id))
        if assigned_commanders:
            commander_icons = ' '.join([str(discord.utils.get(ctx.guild.emojis, name=cmd)) for cmd in assigned_commanders])
            embed.add_field(name="🛡️Dowódcy", value=commander_icons, inline=False)

        embed.add_field(name="📌 Grupa", value=player_stats['GROUP'], inline=False)
        embed.add_field(name="🎯 Cel zabójstw KVK", value=f"{player_stats.get('KVK Kills Target', 'N/A'):,}", inline=False)
        embed.add_field(name="🏅 Cel DKP", value=f"{player_stats.get('DKP Traget', 'N/A'):,}", inline=False)
        embed.set_footer(text=f"Na wniosek @{ctx.author.name}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)
    else:
        await ctx.send("Nie znaleziono statystyk dla podanego ID.")

@bot.command(name='link')
async def link(ctx, gov_id: int):
    user_id = str(ctx.author.id)
    if not os.path.exists(links_file):
        with open(links_file, 'w') as f:
            json.dump({}, f)

    with open(links_file, 'r') as f:
        links = json.load(f)

    links[user_id] = gov_id

    with open(links_file, 'w') as f:
        json.dump(links, f, indent=4)

    await ctx.send(f"Przypisano `gov_id` {gov_id} do użytkownika {ctx.author.mention}")

@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(title="Commands list", description=" ")
    embed.add_field(name="`!stats <gov_id>`", value="Pokazuje statystyki KvK dla określonego ID gubernatora.")
    embed.add_field(name="`!link <gov_id>`", value="Przypisuje `gov_id` do twojego konta Discord.")
    embed.add_field(name="`!przypisz`", value="Przypisuje Dowodców do twojego konta Discord.")
    await ctx.send(embed=embed)

# Globalne zmienne do zarządzania stanem
start_index = 0
last_grid_message_id = None

@bot.command()
async def przypisz(ctx):
    global start_index, last_grid_message_id
    start_index = 0
    last_grid_message_id = None
    await generate_and_send_image(ctx, commanders, emoji_texts, start_index, last_grid_message_id)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return

    global start_index, last_grid_message_id

    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    # Przechowuj informacje o przypisaniach w pliku JSON
    if not os.path.exists(assignments_file):
        with open(assignments_file, 'w') as f:
            json.dump({}, f)

    with open(assignments_file, 'r') as f:
        assignments = json.load(f)

    user_id = str(payload.user_id)

    # Jeśli reakcja to "⬆️" lub "⬇️", wyświetl odpowiednich dowódców
    if str(payload.emoji) in ['⬆️', '⬇️']:
        if message.author.id == bot.user.id:
            ctx = await bot.get_context(message)
            if str(payload.emoji) == '⬆️':
                start_index -= 12
            elif str(payload.emoji) == '⬇️':
                start_index += 12
            await generate_and_send_image(ctx, commanders, emoji_texts, start_index, last_grid_message_id)
        return

    # Jeśli reakcja to emoji dowódcy, zapisz przypisanie
    emoji_name = payload.emoji.name
    if emoji_name in commanders:
        if user_id not in assignments:
            assignments[user_id] = {
                "dowodca": [],
                "avatar": str(payload.member.display_avatar.url)  # Zmiana z avatar_url na display_avatar.url
            }
        elif isinstance(assignments[user_id]['dowodca'], str):
            assignments[user_id]['dowodca'] = [assignments[user_id]['dowodca']]

        if emoji_name not in assignments[user_id]['dowodca']:
            assignments[user_id]['dowodca'].append(emoji_name)
        with open(assignments_file, 'w') as f:
            json.dump(assignments, f, indent=4)
        await channel.send(f"{payload.member.mention} przypisano do dowódcy: {emoji_name}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Nie ma takiej komendy.")
    else:
        await ctx.send(f"Wystąpił błąd: {str(error)}")

# Uruchom bota
bot.run(TOKEN)
