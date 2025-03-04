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
intents.messages = True 
intents.members = True
bot = commands.Bot(command_prefix="+", intents=intents)
bot = commands.Bot(command_prefix='/', intents=intents)

OWNER_ID = 792755123587645461
STAFF_ROLE_ID = 1244339296706760726

# Lorsque le bot est prêt
@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt ! ✅")
    await bot.tree.sync()

# Lorsque le bot reçoit un message
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Vérifier si le message mentionne l'Owner
    if f"<@{OWNER_ID}>" in message.content:
        response = (f"📢 <@{message.author.id}>, évite de ping le Owner pour des choses futiles. 🔕\n"
                    "Si c'est important, contacte un administrateur en priorité. Merci ! 😊")
        await message.channel.send(response)

    # Afficher le message dans la console
    print(f"Message reçu : {message.content}")

    # Permet aux commandes de fonctionner
    await bot.process_commands(message)

# Vérifier si l'utilisateur a un rôle de gestion
def has_management_role(ctx):
    """Vérifie si l'utilisateur a un rôle de gestion."""
    return any(role.id == STAFF_ROLE_ID for role in ctx.author.roles)

# Fonction pour la commande clear
@bot.command()
async def clear(ctx, amount: int = None):
    if amount is None:
        await ctx.send("Merci de préciser un chiffre entre 2 et 100.")
        return
    if amount < 2 or amount > 100:
        await ctx.send("Veuillez spécifier un nombre entre 2 et 100.")
        return

    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f'{len(deleted)} messages supprimés.', delete_after=5)

@bot.command()
async def addrole(ctx, user: discord.Member = None, role: discord.Role = None):
    """Ajoute un rôle à un utilisateur."""
    # Vérifier si l'utilisateur a le rôle [𝑺ץ] Co-Owner
    if not any(role.id == 1244339296706760726 for role in ctx.author.roles):
        await ctx.send("Erreur : vous devez avoir le rôle [𝑺ץ] Co-Owner pour utiliser cette commande.")
        return

    # Vérifier si les arguments sont bien fournis
    if user is None or role is None:
        await ctx.send("Erreur : veuillez suivre ce format : +addrole @user @rôle")
        return

    try:
        # Ajouter le rôle à l'utilisateur
        await user.add_roles(role)
        await ctx.send(f"{user.mention} a maintenant le rôle {role.name} !")
    except discord.Forbidden:
        await ctx.send("Je n'ai pas les permissions nécessaires pour attribuer ce rôle.")
    except discord.HTTPException as e:
        await ctx.send(f"Une erreur est survenue : {e}")

@bot.command()
async def delrole(ctx, user: discord.Member = None, role: discord.Role = None):
    """Retire un rôle à un utilisateur."""
    # Vérifier si l'utilisateur a le rôle [𝑺ץ] Co-Owner
    if not any(role.id == 1244339296706760726 for role in ctx.author.roles):
        await ctx.send("Erreur : vous devez avoir le rôle [𝑺ץ] Co-Owner pour utiliser cette commande.")
        return

    # Vérifier si les arguments sont bien fournis
    if user is None or role is None:
        await ctx.send("Erreur : veuillez suivre ce format : +delrole @user @rôle")
        return

    try:
        # Retirer le rôle à l'utilisateur
        await user.remove_roles(role)
        await ctx.send(f"{user.mention} n'a plus le rôle {role.name} !")
    except discord.Forbidden:
        await ctx.send("Je n'ai pas les permissions nécessaires pour retirer ce rôle.")
    except discord.HTTPException as e:
        await ctx.send(f"Une erreur est survenue : {e}")

# Configuration des emojis personnalisables
EMOJIS = {
    "members": "👥",
    "crown": "👑",  # Emoji couronne
    "voice": "🎤",
    "boosts": "🚀"
}

@bot.command()
async def vc(ctx):
    guild = ctx.guild
    total_members = guild.member_count
    online_members = guild.approximate_presence_count if guild.approximate_presence_count else "N/A"
    voice_members = sum(len(voice_channel.members) for voice_channel in guild.voice_channels)
    boosts = guild.premium_subscription_count

    # Mentionner le propriétaire (to: 792755123587645461)
    owner_member = guild.owner
    server_invite = "https://discord.gg/X4dZAt3BME"  # Lien du serveur

    embed = discord.Embed(title=f"📊 Statistiques de {guild.name}", color=discord.Color.purple())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name=f"{EMOJIS['members']} Membres", value=f"**{total_members}**", inline=True)
    embed.add_field(name=f"{EMOJIS['crown']} Propriétaire", value=f"<@792755123587645461>", inline=True)  # Mention fixe pour le Owner
    embed.add_field(name=f"{EMOJIS['voice']} En vocal", value=f"**{voice_members}**", inline=True)
    embed.add_field(name=f"{EMOJIS['boosts']} Boosts", value=f"**{boosts}**", inline=True)
    embed.add_field(name="🔗 Lien du serveur", value=f"[{guild.name}]({server_invite})", inline=False)
    embed.set_footer(text="📈 Statistiques mises à jour en temps réel")
    
    await ctx.send(embed=embed)

# ID du salon de bienvenue
WELCOME_CHANNEL_ID = 1344194595092697108

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="<a:fete:1172810362261880873> Bienvenue sur le serveur ! <a:fete:1172810362261880873>",
            description=(
                "*<a:fire:1343873843730579478> Ici, l’économie règne en maître, les alliances se forment, les trahisons éclatent... et ta richesse ne tient qu’à un fil ! <a:fire:1343873843730579478>*\n\n"
                "<:better_scroll:1342376863909285930> **Avant de commencer, prends le temps de lire :**\n\n"
                "- <a:fleche3:1290077283100397672> **<#1245380752137388104>** pour éviter les problèmes dès le départ.\n"
                "- <a:fleche3:1290077283100397672> **<#1340402373708746802>** pour comprendre les bases de l’économie.\n"
                "- <a:fleche3:1290077283100397672> **<#1340403279019901014>** pour savoir ce que tu peux obtenir.\n\n"
                "💡 *Un doute ? Une question ? Ouvre un ticket et le staff t’aidera !*\n\n"
                "**Prépare-toi à bâtir ton empire... ou à tout perdre. Bonne chance ! 🍀**"
            ),
            color=discord.Color.gold()
        )
        embed.set_image(url="https://raw.githubusercontent.com/Cass64/EtheryaBot/main/images_etherya/etheryaBot_banniere.png")
        await channel.send(f"{member.mention}", embed=embed)


# Création du bot
intents = discord.Intents.default()
intents.members = True  # Nécessaire pour écouter les événements de join
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Liste des salons à pinguer
salon_ids = [
    1342179344889675827,
    1342179655263977492,
    1342179655263977492  # Le même salon répété
]

@bot.event
async def on_member_join(member: discord.Member):
    # Récupérer les salons depuis les IDs
    guild = member.guild
    channels = []
    for salon_id in salon_ids:
        salon = discord.utils.get(guild.text_channels, id=salon_id)
        if salon:
            channels.append(salon)
        else:
            print(f"Le salon avec l'ID {salon_id} n'existe pas ou n'est pas accessible.")
            return

    # Envoi du ghost ping dans chaque salon et suppression du message du bot
    for salon in channels:
        try:
            # Envoyer le message et mentionner uniquement le membre qui a rejoint
            message = await salon.send(f"{member.mention}")  # Mentionne uniquement le membre
            await message.delete()  # Supprime immédiatement le message
        except discord.Forbidden:
            print(f"Le bot n'a pas la permission d'envoyer un message dans {salon.name}.")
        except discord.HTTPException:
            print("Une erreur est survenue lors de l'envoi du message.")

client = commands.Bot(command_prefix="+", intents=intents)

# Dictionnaire pour stocker les messages supprimés par salon
deleted_messages = {}

@client.event
async def on_message_delete(message):
    # On garde une trace du dernier message supprimé pour chaque salon
    if message.guild.id not in deleted_messages:
        deleted_messages[message.guild.id] = {}
    
    deleted_messages[message.guild.id][message.channel.id] = message

    # Envoi du message supprimé dans le salon spécifique (ID 1346444947750129717)
    log_channel = message.guild.get_channel(1346444947750129717)  # Salon avec l'ID fourni
    if log_channel:
        embed = discord.Embed(
            title="Message supprimé",
            description=message.content,
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Supprimé par {message.author}")
        await log_channel.send(embed=embed)

@client.command()
async def snipe(ctx):
    # Récupérer le salon actuel
    channel = ctx.channel

    # Vérifier si un message a été supprimé dans ce salon
    if channel.id in deleted_messages.get(ctx.guild.id, {}):
        last_deleted_message = deleted_messages[ctx.guild.id][channel.id]
        embed = discord.Embed(
            title="Dernier message supprimé",
            description=last_deleted_message.content,
            color=discord.Color.yellow()
        )
        embed.set_footer(text=f"Supprimé par {last_deleted_message.author}")
        await channel.send(embed=embed)
    else:
        await channel.send("Aucun message supprimé récemment dans ce salon.")

keep_alive()
bot.run(token)
