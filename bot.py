import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
from keep_alive import keep_alive

token = os.environ['ETHERYA']
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="+", intents=intents

# Commande slash pour le giveaway
@slash.slash(name="giveaway", description="Lance un giveaway personnalisé")
async def giveaway(ctx, channel: discord.TextChannel, prize: str, duration_hours: int, image_url: str = None):
    # Vérifier que l'utilisateur a les permissions appropriées
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("Vous n'avez pas les permissions nécessaires pour lancer un giveaway.", hidden=True)
        return

    # Convertir la durée en heures en secondes
    duration_seconds = duration_hours * 3600  # 1 heure = 3600 secondes

    # Créer l'embed pour annoncer le giveaway
    giveaway_embed = Embed(
        title="🎉 Giveaway en cours 🎉",
        description=f"**Prix :** {prize}\n**Durée :** {duration_hours} heures\n\nReact pour participer !",
        color=discord.Color.blue()
    )

    # Ajouter une image si elle est fournie
    if image_url:
        giveaway_embed.set_image(url=image_url)

    giveaway_embed.set_footer(text=f"Organisé par {ctx.author.name}", icon_url=ctx.author.avatar_url)
    
    # Envoyer l'embed dans le salon spécifié
    message = await channel.send(embed=giveaway_embed)
    
    # Ajouter une réaction pour participer
    await message.add_reaction("🎉")

    # Attendre la fin du giveaway
    await asyncio.sleep(duration_seconds)

    # Récupérer les utilisateurs ayant réagi
    reaction = discord.utils.get(message.reactions, emoji="🎉")
    users = await reaction.users().flatten()
    
    # Supprimer l'auteur du message des participants (si l'auteur a réagi, ne pas l'inclure)
    users = [user for user in users if user != bot.user]

    # Créer un embed pour annoncer le gagnant
    if users:
        winner = random.choice(users)
        winner_embed = Embed(
            title="🎉 Félicitations 🎉",
            description=f"Le gagnant du giveaway **{prize}** est : {winner.mention} !",
            color=discord.Color.green()
        )
        winner_embed.set_footer(text="Merci à tous pour votre participation!")
        await channel.send(embed=winner_embed)
    else:
        no_winner_embed = Embed(
            title="🎉 Giveaway annulé 🎉",
            description="Aucun participant n'a été trouvé, le giveaway est annulé.",
            color=discord.Color.red()
        )
        await channel.send(embed=no_winner_embed)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot connecté en tant que {bot.user}')

keep_alive()
bot.run(token)
