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
bot = commands.Bot(command_prefix="+", intents=intents)

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


# Synchroniser les commandes après le démarrage du bot
@bot.event
async def on_ready():
    await bot.tree.sync()  # Synchronise les commandes slash
    print(f'Bot logged in as {bot.user}')

keep_alive()
bot.run(token)
