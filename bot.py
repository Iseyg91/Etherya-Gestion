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

# Liste des salons à pinguer
salon_ids = [
    1342179344889675827,
    1342179655263977492,
    1245380752137388104
]

@bot.event
async def on_member_join(member):
    guild = member.guild
    
    # Envoi du message de bienvenue
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
    
    # Envoi du ghost ping dans plusieurs salons
    channels = [bot.get_channel(salon_id) for salon_id in salon_ids]
    
    for salon in channels:
        if salon:
            try:
                message = await salon.send(f"{member.mention}")
                await message.delete()
            except discord.Forbidden:
                print(f"Le bot n'a pas la permission d'envoyer un message dans {salon.name}.")
            except discord.HTTPException:
                print("Une erreur est survenue lors de l'envoi du message.")

@bot.command()
async def nuke(ctx):
    # Vérifie si l'utilisateur a les permissions nécessaires (admin ou le rôle spécifique)
    if ctx.author.guild_permissions.administrator or 1171489794698784859 in [role.id for role in ctx.author.roles]:
        # Vérifie que la commande a été lancée dans un salon texte
        if isinstance(ctx.channel, discord.TextChannel):
            # Récupère le salon actuel
            channel = ctx.channel

            # Sauvegarde les informations du salon
            overwrites = channel.overwrites
            channel_name = channel.name
            category = channel.category
            position = channel.position

            # Récupère l'ID du salon pour le recréer
            guild = channel.guild

            try:
                # Crée un nouveau salon avec les mêmes permissions et la même position
                await channel.delete()  # Supprime le salon actuel

                # Crée un nouveau salon avec les mêmes permissions, catégorie et position
                new_channel = await guild.create_text_channel(
                    name=channel_name,
                    overwrites=overwrites,
                    category=category
                )  # Crée le nouveau salon

                # Réajuste la position du salon
                await new_channel.edit(position=position)

                # Envoie un message dans le salon d'origine pour prévenir de la suppression avant de le recréer
                await ctx.send(f"{ctx.author.mention} a nuke le salon {channel_name}. Le salon a été recréé avec succès.")

                # Envoie un message dans le nouveau salon pour confirmer la recréation
                await new_channel.send(
                    f"Le salon {channel_name} a été supprimé et recréé, {ctx.author.mention}."
                )
            except Exception as e:
                await ctx.send(f"Une erreur est survenue lors de la recréation du salon : {e}")
        else:
            await ctx.send("Cette commande doit être utilisée dans un salon texte.")
    else:
        await ctx.send("Tu n'as pas les permissions nécessaires pour exécuter cette commande.")
@bot.command()
async def aide(ctx):
    # Vérifier si un message a déjà été envoyé
    if hasattr(ctx, 'sent_embed') and ctx.sent_embed:
        return  # Empêcher l'envoi en double si un embed a déjà été envoyé
    
    # Création de l'embed avec un titre et une description clairs
    embed = discord.Embed(
        title="📜 Commandes du Bot Etherya",
        description="Voici la liste complète des commandes disponibles pour interagir avec le bot.",
        color=discord.Color(0x1abc9c)  # Couleur plus douce et moderne
    )

    # Ajout de l'icône du bot à gauche de l'embed
    embed.set_thumbnail(url=bot.user.avatar.url)

    # Ajout des champs pour chaque commande avec des descriptions améliorées
    embed.add_field(
        name="🔨 **+clear (nombre entre 2 et 100)**", 
        value="Supprime un certain nombre de messages dans un salon. "
              "Entrez un nombre entre 2 et 100 pour que le bot nettoie les messages.",
        inline=False
    )
    embed.add_field(
        name="❌ **+delrole @user @rôle**", 
        value="Retire un rôle spécifique d'un utilisateur. "
              "Ciblez un utilisateur et le rôle à retirer.",
        inline=False
    )
    embed.add_field(
        name="✅ **+addrole @user @rôle**", 
        value="Attribue un rôle à un utilisateur spécifié. "
              "Ciblez un utilisateur et le rôle à attribuer.",
        inline=False
    )
    embed.add_field(
        name="📊 **+vc**", 
        value="Affiche les statistiques actuelles du serveur, y compris les membres en ligne.",
        inline=False
    )
    embed.add_field(
        name="💥 **+nuke**", 
        value="Efface tous les messages du salon actuel (nuke). "
              "Utilisé avec précaution pour éviter toute perte de données importante.",
        inline=False
    )
    
    # Image à inclure
    embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryaBot_banniere.png?raw=true")
    
    # Mention du créateur en bas
    embed.add_field(name="Bot développé par 👑 Iseyg", value="Merci à Iseyg pour ce bot incroyable !", inline=False)

    # Envoi de l'embed dans le salon
    await ctx.send(embed=embed)
    
    # Marquer comme envoyé pour éviter la duplication
    ctx.sent_embed = True
# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
