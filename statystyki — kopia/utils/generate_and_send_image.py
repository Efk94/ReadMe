import os
from PIL import Image, ImageDraw, ImageFont
import discord

async def generate_and_send_image(ctx, commanders, emoji_texts, start_index, last_grid_message_id):
    # Współczynnik skalowania avatara
    scale_factor = 5
    # Wymiary pojedynczego avatara
    avatar_size = (64 * scale_factor, 64 * scale_factor)
    # Ilość dowódców do wyświetlenia jednocześnie
    max_commanders = 12

    # Tworzymy listę dowódców do wyświetlenia
    selected_commanders = list(commanders.items())[start_index:start_index + max_commanders]
    if not selected_commanders:
        await ctx.send("Brak więcej dowódców do wyświetlenia.")
        return

    # Oblicz szerokość całego obrazu na podstawie liczby kolumn
    width = max_commanders * avatar_size[0]
    # Oblicz wysokość obrazu na podstawie wysokości avatara i wysokości tekstu
    font_size = 44
    height = avatar_size[1] + font_size + 10

    # Nowy obraz
    new_image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(new_image)
    # Font do tekstu (dobrany rozmiar)
    font = ImageFont.truetype("arial.ttf", font_size)

    # Wczytujemy i wklejamy avatary dowódców
    for index, (dowodca, avatar_path) in enumerate(selected_commanders):
        avatar = Image.open(avatar_path)
        avatar = avatar.resize(avatar_size)
        x = index * avatar_size[0]
        new_image.paste(avatar, (x, 0))

        dowodca_name = dowodca.split('.')[0]

        text_bbox = draw.textbbox((x, avatar_size[1], x + avatar_size[0], height - 10), dowodca_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x + (avatar_size[0] - text_width) // 2
        text_y = avatar_size[1] + 5

        outline_color = (50, 50, 255)
        outline_thickness = 2
        for i in range(1, outline_thickness + 1):
            draw.text((text_x - i, text_y), dowodca_name, font=font, fill=outline_color)
            draw.text((text_x + i, text_y), dowodca_name, font=font, fill=outline_color)
            draw.text((text_x, text_y - i), dowodca_name, font=font, fill=outline_color)
            draw.text((text_x, text_y + i), dowodca_name, font=font, fill=outline_color)

        draw.text((text_x, text_y), dowodca_name, font=font, fill=(255, 255, 255))

    filename = "commanders_grid.jpg"
    new_image.save(filename)
    file = discord.File(filename, filename=filename)

    # Usuwanie poprzedniej wiadomości z siatką
    if last_grid_message_id:
        try:
            previous_message = await ctx.fetch_message(last_grid_message_id)
            await previous_message.delete()
        except:
            pass

    message = await ctx.send(file=file)

    # Zapisz ID nowej wiadomości z siatką
    last_grid_message_id = message.id

    # Dodaj reakcje emoji do obrazka
    for dowodca, _ in selected_commanders:
        dowodca_name = dowodca.split('.')[0]
        emoji_text = emoji_texts.get(dowodca_name, '')  # Pobierz tekst emoji zamiast samej nazwy
        emoji = discord.utils.get(ctx.guild.emojis, name=emoji_text.strip(':'))  # Wyszukaj emotkę po nazwie
        if emoji:
            await message.add_reaction(emoji)
        else:
            print(f"No emoji found for {dowodca_name} with text {emoji_text}")
    await message.add_reaction('⬆️')
    await message.add_reaction('⬇️')
