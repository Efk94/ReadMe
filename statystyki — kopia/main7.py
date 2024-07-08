import os
import sys
import json
import discord
import pandas as pd
import logging
import matplotlib.pyplot as plt
from discord.ext import commands
from dotenv import load_dotenv
from StringProgressBar import progressBar
from data.KvkStats import KvkStats
from utils.generate_and_send_image import generate_and_send_image

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s', filename='bot.log', filemode='a')

# Dodanie ścieżki do katalogu głównego projektu tylko raz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

# Globalne zmienne do zarządzania stanem
start_index = 0
last_grid_message_id = None

translations = {
    'pl': {
        'stats_command': 'Statystyki',
        'link_command': 'Przypisz ID gubernatora',
        'no_gov_id': 'Nie masz przypisanego `gov_id`. Użyj komendy `!link <gov_id>`, aby przypisać swoje `gov_id`.',
        'stats_not_found': 'Nie znaleziono statystyk dla podanego ID.',
        'help_command': 'Lista komend',
    },
    'en': {
        'stats_command': 'Stats',
        'link_command': 'Link governor ID',
        'no_gov_id': 'You have not linked a `gov_id`. Use the command `!link <gov_id>` to link your `gov_id`.',
        'stats_not_found': 'No stats found for the provided ID.',
        'help_command': 'Commands list',
    }
}

user_languages = {}

def get_translation(locale: str, key: str) -> str:
    return translations.get(locale, {}).get(key, key)

@bot.command(name='set_language')
async def set_language(ctx, language: str):
    if language not in translations:
        await ctx.send("Nieobsługiwany język. Dostępne języki: " + ", ".join(translations.keys()))
        return

    user_id = str(ctx.author.id)
    user_languages[user_id] = language

    await ctx.send(f"Ustawiono język na {language}.")

# Załaduj dowódców
def load_commanders():
    avatar_folder = r'C:\Users\profo\OneDrive\Pulpit\Nowy folder\Avatar'
    commanders = {}
    for filename in os.listdir(avatar_folder):
        name, _ = os.path.splitext(filename)
        commanders[name] = os.path.join(avatar_folder, filename)
    return commanders

commanders = load_commanders()
emoji_texts = {
    "Alex": ":Alex:",
    "Amanitore": ":Amanitore:",
    # Dodaj pozostałych dowódców tutaj...
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
    logging.info(f'{bot.user} has connected to Discord!')

@bot.command(name='stats')
async def stats(ctx, gov_id: int = None):
    user_id = str(ctx.author.id)
    language = user_languages.get(user_id, 'pl')

    if gov_id is None:
        gov_id = get_linked_gov_id(user_id)
        if gov_id is None:
            await ctx.send(get_translation(language, 'no_gov_id'))
            return

    player_stats = get_player_stats(gov_id)
    if not player_stats:
        await ctx.send(get_translation(language, 'stats_not_found'))
        return

    # Tworzenie wykresu statystyk
    create_stats_plot(player_stats)

    embed = create_stats_embed(player_stats, ctx.author, language)
    file = discord.File("stats_plot.png", filename="stats_plot.png")
    embed.set_image(url="attachment://stats_plot.png")
    await ctx.send(embed=embed, file=file)

def get_player_stats(gov_id):
    player_stats_df = excel_data[excel_data['GOVERNOR ID'] == gov_id]
    if player_stats_df.empty:
        return None
    return player_stats_df.iloc[0]

def create_stats_plot(player_stats):
    labels = ['Siła', 'Łączna liczba zabójstw', 'Zgony', 'KP']
    values = [player_stats['POWER'], player_stats['TOTAL KILLS'], player_stats['DEADS'], player_stats['KVK Kills T4/5']]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color=['blue', 'green', 'red', 'purple'])
    plt.xlabel('Kategorie')
    plt.ylabel('Wartości')
    plt.title('Statystyki gracza')
    plt.savefig('stats_plot.png')
    plt.close()

def create_stats_embed(player_stats, author, language):
    embed = discord.Embed(color=0xf56754)
    embed.title = f"📊 {get_translation(language, 'stats_command')} dla {player_stats['USERNAME']}"
    embed.set_author(name="2732bot", url="https://lookerstudio.google.com/u/0/reporting/a5831fbc-65a0-4b7a-9213-00beb671ca79/page/p_q674h2m68c", icon_url="https://cdn.discordapp.com/attachments/1237356214099247145/1258308083369902140/tawy.png?ex=66879239&is=668640b9&hm=4e6d5a5f77157b35e08e97bc8d043bf8fd202f09cc4adad6993ad0b216199617&")
    embed.set_thumbnail(url=author.display_avatar.url)
    
    embed.add_field(name="📈 Statystyki bojowe", value="\u200b", inline=False)
    embed.add_field(name="💪 Siła", value=f"{player_stats['POWER']:,}", inline=True)
    embed.add_field(name="🔫 Łączna liczba zabójstw", value=f"{player_stats['TOTAL KILLS']:,}", inline=True)
    embed.add_field(name="💀 Zgony", value=f"{player_stats['DEADS']:,}", inline=True)
    embed.add_field(name="🏆 KP", value=f"{player_stats['KVK Kills T4/5']:,}", inline=True)
    embed.add_field(name="📌 Grupa", value=player_stats['GROUP'], inline=True)
    
    assigned_commanders = get_assigned_commanders(str(author.id))
    if assigned_commanders:
        commander_icons = ' '.join([str(discord.utils.get(ctx.guild.emojis, name=cmd)) for cmd in assigned_commanders])
        embed.add_field(name="Przypisani Dowódcy", value=commander_icons, inline=True)
    
    embed.add_field(name="📊 Statystyki DKP", value="\u200b", inline=False)
    embed.add_field(name="💥 DKP", value=f"{player_stats.get('KVK Kills T4/5', 'N/A'):,}", inline=True)
    embed.add_field(name="📍 Grupa DKP", value=player_stats.get('DKP group', 'N/A'), inline=True)
    embed.add_field(name="🎯 KVK Kills Target", value=f"{player_stats.get('KVK Kills Target', 'N/A'):,}", inline=True)
    embed.add_field(name="🏅 DKP Target", value=f"{player_stats.get('DKP Traget', 'N/A'):,}", inline=True)
    embed.set_footer(text=f"Requested by @{author.name}", icon_url=author.display_avatar.url)
    
    return embed

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
async def help(ctx, command_name: str = None):
    user_id = str(ctx.author.id)
    language = user_languages.get(user_id, 'pl')

    if command_name:
        command = bot.get_command(command_name)
        if command:
            embed = discord.Embed(title=f"Pomoc dla komendy {command_name}")
            embed.add_field(name="Opis", value=command.help)
            embed.add_field(name="Użycie", value=command.brief)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Nie znaleziono komendy {command_name}.")
    else:
        embed = discord.Embed(title=get_translation(language, 'help_command'), description=" ")
        for command in bot.commands:
            embed.add_field(name=f"`!{command.name}`", value=get_translation(language, f'{command.name}_command'))
        await ctx.send(embed=embed)

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
                "avatar": str(payload.member.display_avatar.url)
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
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Brak wymaganych argumentów.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Błędny argument.")
    else:
        await ctx.send(f"Wystąpił nieznany błąd: {str(error)}")

# Uruchom bota
bot.run(TOKEN)
