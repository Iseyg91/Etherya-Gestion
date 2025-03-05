import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
from keep_alive import keep_alive
from discord.ui import Button, View
from discord.ui import View, Select

token = os.environ['ETHERYA']
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True 
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="+", intents=intents)

STAFF_ROLE_ID = 1244339296706760726

# Lorsque le bot est prêt
@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt ! ✅")
    await bot.tree.sync()

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    print(f"Commandes chargées: {list(bot.commands)}")  # Affiche les commandes disponibles

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
                "- <a:fleche3:1290077283100397672> **<#1340402531712368752>** pour savoir ce que tu peux obtenir.\n\n"
                "💡 *Un doute ? Une question ? Ouvre un ticket et le staff t’aidera !*\n\n"
                "**Prépare-toi à bâtir ton empire... ou à tout perdre. Bonne chance ! 🍀**"
            ),
            color=discord.Color.gold()
        )
        embed.set_image(url="https://raw.githubusercontent.com/Cass64/EtheryaBot/main/images_etherya/etheryaBot_banniere.png")
        await channel.send(f"{member.mention}", embed=embed)
    
    # Envoi du ghost ping une seule fois par salon
    for salon_id in salon_ids:
        salon = bot.get_channel(salon_id)
        if salon:
            try:
                message = await salon.send(f"{member.mention}")
                await message.delete()
            except discord.Forbidden:
                print(f"Le bot n'a pas la permission d'envoyer un message dans {salon.name}.")
            except discord.HTTPException:
                print("Une erreur est survenue lors de l'envoi du message.")

    # IMPORTANT : Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)
    
@bot.command()
async def clear(ctx, amount: int = None):
    # Vérifie si l'utilisateur a les permissions nécessaires (admin ou le rôle spécifique)
    if ctx.author.guild_permissions.administrator or 1171489794698784859 in [role.id for role in ctx.author.roles]:
        if amount is None:
            await ctx.send("Merci de préciser un chiffre entre 2 et 100.")
            return
        if amount < 2 or amount > 100:
            await ctx.send("Veuillez spécifier un nombre entre 2 et 100.")
            return

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f'{len(deleted)} messages supprimés.', delete_after=5)
    else:
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")

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
    # IMPORTANT : Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)

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
        
    # IMPORTANT : Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)
    
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
    # IMPORTANT : Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)
    
@bot.command()
async def aide(ctx):
    role_id = 1166113718602575892  # ID du rôle requis
    if not any(role.id == role_id for role in ctx.author.roles):
        await ctx.send("⚠️ Vous n'avez pas la permission d'utiliser cette commande.")
        return

    banner_url = "https://raw.githubusercontent.com/Cass64/EtheryaBot/refs/heads/main/images_etherya/etheryaBot_banniere.png"  # URL de la bannière
    embed = discord.Embed(
        title="🏡 **Accueil Etherya Gestion**",
        description=f"Hey, bienvenue {ctx.author.mention} sur la page d'accueil d'Etherya Gestion ! 🎉\n\n"
                    "Ici, vous trouverez toutes les informations nécessaires pour gérer et administrer votre serveur efficacement. 🌟",
        color=discord.Color(0x1abc9c)
    )
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.set_footer(text="Développé avec ❤️ par Iseyg. Merci pour votre soutien !")
    embed.set_image(url=banner_url)  # Ajout de la bannière en bas de l'embed

    # Informations générales
    embed.add_field(name="📚 **Informations**", value=f"• **Mon préfixe** : +\n• **Nombre de commandes** : X", inline=False)

    # Création du menu déroulant
    select = discord.ui.Select(
        placeholder="Choisissez une catégorie 👇", 
        options=[
            discord.SelectOption(label="Gestion", description="📚 Commandes pour gérer le serveur", emoji="🔧"),
            discord.SelectOption(label="Modération / Économie", description="⚖️ Commandes modération et économie", emoji="💰"),
            discord.SelectOption(label="Fun", description="🎉 Commandes fun et divertissantes", emoji="🎲"),
            discord.SelectOption(label="Utilitaire", description="⚙️ Commandes utiles", emoji="🔔"),
            discord.SelectOption(label="Crédits", description="💖 Remerciements et crédits", emoji="🙏")
        ], 
        custom_id="help_select"
    )

    # Définir la méthode pour gérer l'interaction du menu déroulant
    async def on_select(interaction: discord.Interaction):
        category = interaction.data['values'][0]
        new_embed = discord.Embed(color=discord.Color(0x1abc9c))
        new_embed.set_image(url=banner_url)  # Ajout de la bannière dans chaque catégorie

        if category == "Gestion":
            new_embed.title = "🔨 **Commandes de Gestion**"
            new_embed.description = "Bienvenue dans la section gestion ! 📊\nCes commandes sont essentielles pour administrer le serveur. Voici un aperçu :"
            new_embed.add_field(name="🔧 +clear (2-100)", value="Supprime des messages dans le salon 📬.\n*Utilisé pour nettoyer un salon ou supprimer un spam.*", inline=False)
            new_embed.add_field(name="💥 +nuke", value="Efface **tous** les messages du salon 🚨.\n*Pour une action plus drastique en cas de chaos ou d'urgence !*.", inline=False)
            new_embed.add_field(name="➕ +addrole @user @rôle", value="Ajoute un rôle à un utilisateur 👤.\n*Pour attribuer des rôles et des privilèges spéciaux aux membres.*", inline=False)
            new_embed.add_field(name="➖ +delrole @user @rôle", value="Retire un rôle à un utilisateur 🚫.\n*Retirer un rôle en cas de sanction ou de changement de statut.*", inline=False)
        elif category == "Modération / Économie":
            new_embed.title = "⚖️ **Commandes de Modération et Économie**"
            new_embed.description = "Bienvenue dans la section modération et économie ! 💼\nIci, vous pouvez gérer les aspects économiques et de sécurité du serveur."
            new_embed.add_field(name="🏰 +prison @user", value="Mets un utilisateur en prison pour non-paiement des taxes 🏰.\n*Assurez-vous que tout le monde respecte les règles économiques.*", inline=False)
            new_embed.add_field(name="🚔 +arrestation @user", value="Arrête un utilisateur après un braquage raté 🚔.\n*Appliquez les sanctions après un braquage raté ou une tentative échouée.*", inline=False)
            new_embed.add_field(name="⚖️ +liberation @user", value="Libère un utilisateur emprisonné pour taxes impayées ⚖️.\n*Libérer un membre après le paiement ou la levée des charges.*", inline=False)
            new_embed.add_field(name="🔓 +evasion", value="Permet de s'évader après un braquage raté 🔓.\n*Les audacieux peuvent tenter de s'échapper pour éviter les conséquences.*", inline=False)
        elif category == "Fun":
            new_embed.title = "🎉 **Commandes Fun**"
            new_embed.description = "Bienvenue dans la section Fun ! 🎲\nCes commandes sont là pour ajouter une touche d'humour et de détente au serveur. Amusez-vous !"
            new_embed.add_field(name="🌈 +gay @user", value="Détermine le taux de gayitude d'un utilisateur 🌈.\n*Testez votre ouverture d'esprit !*.", inline=False)
            new_embed.add_field(name="😤 +racist @user", value="Détermine le taux de racisme d'un utilisateur 😤.\n*Un test amusant à faire avec vos amis.*", inline=False)
            new_embed.add_field(name="💘 +love @user", value="Affiche le niveau de compatibilité amoureuse 💘.\n*Testez votre compatibilité avec quelqu'un !*.", inline=False)
            new_embed.add_field(name="🐀 +rat @user", value="Détermine le taux de ratitude d'un utilisateur 🐀.\n*Vérifiez qui est le plus ‘rat’ parmi vos amis.*", inline=False)
            new_embed.add_field(name="🎲 +roll", value="Lance un dé pour générer un nombre aléatoire entre 1 et 500 🎲.\n*Essayez votre chance !*.", inline=False)
            new_embed.add_field(name="🍆 +zizi @user", value="Évalue le niveau de zizi de l'utilisateur 🍆.\n*Un test ludique pour voir qui a le plus grand ego !*.", inline=False)
            new_embed.add_field(name="🤗 +hug @user", value="Envoie un câlin à [membre] avec une image mignonne de câlin.", inline=False)
            new_embed.add_field(name="💥 +slap @user", value="Tu as giflé [membre] avec une image drôle de gifle.", inline=False)
            new_embed.add_field(name="💃 +dance @user", value="[membre] danse avec une animation rigolote.", inline=False)
            new_embed.add_field(name="💘 +flirt @user", value="Vous avez charmé [membre] avec un compliment !", inline=False)
            new_embed.add_field(name="🤫 +whisper @user [message]", value="[membre] a chuchoté à [ton nom] : [message].", inline=False)
            new_embed.add_field(name="🌟 +compliment @user", value="Envoie un compliment aléatoire à [membre], comme 'Tu es plus génial que tout le chocolat du monde !'.", inline=False)
            new_embed.add_field(name="😜 +troll @user", value="Une blague aléatoire ou une phrase troll envers le membre, avec une image rigolote.", inline=False)
        elif category == "Utilitaire":
            new_embed.title = "⚙️ **Commandes Utilitaires**"
            new_embed.description = "Bienvenue dans la section utilitaire ! 🛠️\nCes commandes sont conçues pour offrir des statistiques en temps réel et envoyer des alertes."
            new_embed.add_field(name="📊 +vc", value="Affiche les statistiques du serveur en temps réel 📊.\n*Suivez l'évolution du serveur en direct !*.", inline=False)
            new_embed.add_field(name="🚨 +alerte", value="Envoie une alerte au staff en cas de comportement inapproprié (insultes, spam, etc.) 🚨.\n*Note : Si cette commande est utilisée abusivement, des sanctions sévères seront appliquées !*.", inline=False)
        elif category == "Crédits":
            new_embed.title = "💖 **Crédits**"
            new_embed.description = "Un immense merci à **Iseyg** pour le développement de ce bot incroyable ! 🙏\n\nGrâce à lui, ce bot est ce qu'il est aujourd'hui. Merci à toute la communauté pour son soutien continu ! 💙"

        await interaction.response.edit_message(embed=new_embed)

    select.callback = on_select  # Attacher la fonction de callback à l'élément select

    # Afficher le message avec le menu déroulant
    view = discord.ui.View()
    view.add_item(select)
    
    await ctx.send(embed=embed, view=view)

ROLE_ID = 1166113718602575892  # ID du rôle requis

def has_required_role():
    def predicate(ctx):
        role = discord.utils.get(ctx.author.roles, id=ROLE_ID)
        if role is None:
            return False
        return True
    return commands.check(predicate)

@bot.command()
@has_required_role()
async def gay(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title=f"Analyse de gayitude 🌈", 
        description=f"{member.mention} est gay à **{percentage}%** !\n\n*Le pourcentage varie en fonction des pulsions du membre.*", 
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
@has_required_role()
async def racist(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title=f"Analyse de racisme 🪄", 
        description=f"{member.mention} est raciste à **{percentage}%** !\n\n*Le pourcentage varie en fonction des pulsions du membre.*", 
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
@has_required_role()
async def love(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("Tu n'as pas mentionné de membre ! Utilise +love @membre.")
        return
    
    love_percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title="L'Amour Etheryen",
        description=f"L'amour entre {ctx.author.mention} et {member.mention} est de **{love_percentage}%** !",
        color=discord.Color.red() if love_percentage > 50 else discord.Color.blue()
    )
    embed.set_footer(text="Que l'amour vous guide !")
    embed.set_thumbnail(url="https://img.freepik.com/photos-gratuite/silhouette-mains-coeur-contre-lumieres-ville-nuit_23-2150984259.jpg?ga=GA1.1.719997987.1741155829&semt=ais_hybrid")
    
    await ctx.send(embed=embed)

@bot.command()
@has_required_role()
async def rat(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title=f"Analyse de radinerie 🐁", 
        description=f"{member.mention} est un rat à **{percentage}%** !\n\n*Le pourcentage varie en fonction des actes du membre.*", 
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

import random
import discord
from discord.ext import commands

@bot.command()
@has_required_role()
async def con(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title="Analyse de connerie 🤡",
        description=f"{member.mention} est con à **{percentage}%** !\n\n*Le pourcentage varie en fonction des neurones actifs du membre.*",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

# ID du rôle requis
role_id = 1166113718602575892

# Définir la commande +roll
@bot.command()
async def roll(ctx, x: str = None):
    # Vérifier si l'utilisateur a le rôle requis
    if role_id not in [role.id for role in ctx.author.roles]:
        embed = discord.Embed(
            title="Erreur",
            description="Vous n'avez pas le rôle requis pour utiliser cette commande.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Vérifier si x est bien précisé
    if x is None:
        embed = discord.Embed(
            title="Erreur",
            description="Vous n'avez pas précisé de chiffre entre 1 et 500.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    try:
        # Convertir x en entier
        x = int(x)
    except ValueError:
        embed = discord.Embed(
            title="Erreur",
            description="Le chiffre doit être un nombre entier.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Vérifier si x est dans les bonnes limites
    if x < 1 or x > 500:
        embed = discord.Embed(
            title="Erreur",
            description="Le chiffre doit être compris entre 1 et 500.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Générer un nombre aléatoire entre 1 et x
    result = random.randint(1, x)

    # Créer l'embed de la réponse
    embed = discord.Embed(
        title="Résultat du tirage",
        description=f"Le nombre tiré au hasard entre 1 et {x} est : **{result}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    
@bot.command()
@has_required_role()
async def zizi(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    # Générer une valeur aléatoire entre 0 et 28 cm
    value = random.randint(0, 50)

    # Créer l'embed
    embed = discord.Embed(
        title="Analyse de la taille du zizi 🔥", 
        description=f"{member.mention} a un zizi de **{value} cm** !\n\n*La taille varie selon l'humeur du membre.*", 
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)

    # Envoyer l'embed
    await ctx.send(embed=embed)

@bot.command()
@has_required_role()
async def hug(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Tu as donné un câlin à {member.name} ! 🤗",  # Utilisation de member.name pour afficher le nom simple
        description="Les câlins sont la meilleure chose au monde !",
        color=discord.Color.blue()
    )
    embed.set_image(url="https://media.tenor.com/P6FsFii7pnoAAAAM/hug-warm-hug.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)  # Utilisation de ctx.author.name
    await ctx.send(embed=embed)


@bot.command()
@has_required_role()
async def slap(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Tu as giflé {member.name} !",  # Utilisation de member.name
        description="Oups, ça a dû faire mal 😱",
        color=discord.Color.red()
    )
    embed.set_image(url="https://media.tenor.com/QRdCcNbk18MAAAAM/slap.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)  # Utilisation de ctx.author.name
    await ctx.send(embed=embed)


@bot.command()
@has_required_role()
async def dance(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"{member.name} danse comme un pro ! 💃🕺",  # Utilisation de member.name
        description="Admirez cette danse épique !",
        color=discord.Color.green()
    )
    embed.set_image(url="https://media.tenor.com/d7ibtS6MLQgAAAAM/dancing-kid.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)  # Utilisation de ctx.author.name
    await ctx.send(embed=embed)


@bot.command()
@has_required_role()
async def flirt(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Vous avez charmé {member.name} avec un sourire éclatant ! 😍",  # Utilisation de member.name
        description="Vous êtes irrésistible !",
        color=discord.Color.purple()
    )
    embed.set_image(url="https://media.tenor.com/HDdV-0Km1QAAAAAM/hello-sugar.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)  # Utilisation de ctx.author.name
    await ctx.send(embed=embed)


@bot.command()
@has_required_role()
async def whisper(ctx, member: discord.Member = None, *, message):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Chuchotement de {ctx.author.name} à {member.name}",  # Utilisation de member.name et ctx.author.name
        description=f"*{message}*",
        color=discord.Color.greyple()
    )
    embed.set_footer(text="Un message secret entre vous deux...")
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
@has_required_role()
async def troll(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Tu as trollé {member.name} ! 😆",  # Utilisation de member.name
        description=f"Oups, {member.name} s'est fait avoir !",
        color=discord.Color.orange()
    )
    embed.set_image(url="https://media.tenor.com/7Q8TRpW2ZXkAAAAM/yeet-lol.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)  # Utilisation de ctx.author.name
    await ctx.send(embed=embed)

@bot.command()
@has_required_role()
async def kiss(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Tu as embrassé {member.name} !",  # Utilisation de member.name
        description="Un doux baiser 💋",  
        color=discord.Color.pink()
    )
    embed.set_image(url="https://media.tenor.com/3DHc1_2PZ-oAAAAM/kiss.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=ctx.author.avatar.url)  # Utilisation de ctx.author.name
    await ctx.send(embed=embed)
    
# Commande +prison
@bot.command()
@commands.has_role(1165936153418006548)  # ID du rôle sans guillemets
async def prison(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("Vous n'avez ciblé personne.")
        return

    embed = discord.Embed(
        title="La Police Etheryenne vous arrête !",
        description="Te voilà privé d'accès de l'économie !",
        color=0xffcc00
    )
    embed.set_image(url="https://i.imgur.com/dX0DSGh.jpeg")
    await ctx.send(embed=embed)

    # Gestion des rôles
    role_remove = discord.utils.get(ctx.guild.roles, id=1344407004739014706)
    role_add = discord.utils.get(ctx.guild.roles, id=1344453363261116468)

    if role_remove:
        await member.remove_roles(role_remove)
    if role_add:
        await member.add_roles(role_add)

# Commande +arrestation
@bot.command()
@commands.has_role(1165936153418006548)
async def arrestation(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("Vous n'avez ciblé personne.")
        return

    embed = discord.Embed(
        title="Vous avez été arrêté lors d'une tentative de braquage",
        description="Braquer les fourgons c'est pas bien !",
        color=0xff0000
    )
    embed.set_image(url="https://i.imgur.com/uVNxDX2.jpeg")
    await ctx.send(embed=embed)

    # Gestion des rôles
    role_remove = discord.utils.get(ctx.guild.roles, id=1344407004739014706)
    role_add = discord.utils.get(ctx.guild.roles, id=1344453363261116468)

    if role_remove:
        await member.remove_roles(role_remove)
    if role_add:
        await member.add_roles(role_add)

# Commande +liberation
@bot.command()
@commands.has_role(1165936153418006548)
async def liberation(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("Vous n'avez ciblé personne.")
        return

    embed = discord.Embed(
        title="La Police Étheryenne a décidé de vous laisser sortir de prison !",
        description="En revanche, si vous refaites une erreur c'est au cachot direct !",
        color=0x00ff00
    )
    embed.set_image(url="https://i.imgur.com/Xh7vqh7.jpeg")
    await ctx.send(embed=embed)

    # Gestion des rôles
    role_add = discord.utils.get(ctx.guild.roles, id=1344407004739014706)
    role_remove = discord.utils.get(ctx.guild.roles, id=1344453363261116468)

    if role_add:
        await member.add_roles(role_add)
    if role_remove:
        await member.remove_roles(role_remove)

# Commande +evasion
@bot.command()
@commands.has_role(1344591867068809268)
async def evasion(ctx):
    member = ctx.author  # L'auteur de la commande s'évade

    embed = discord.Embed(
        title="Un joueur s'évade de prison !",
        description="Grâce à un ticket trouvé à la fête foraine !!",
        color=0x0000ff
    )
    embed.set_image(url="https://i.imgur.com/X8Uje39.jpeg")
    await ctx.send(embed=embed)

    # Gestion des rôles
    role_add = discord.utils.get(ctx.guild.roles, id=1344407004739014706)
    role_remove_1 = discord.utils.get(ctx.guild.roles, id=1344453363261116468)
    role_remove_2 = discord.utils.get(ctx.guild.roles, id=1344591867068809268)

    if role_add:
        await member.add_roles(role_add)
    if role_remove_1:
        await member.remove_roles(role_remove_1)
    if role_remove_2:
        await member.remove_roles(role_remove_2)

# Gestion des erreurs pour les commandes
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Il manque un argument à la commande.")
    else:
        await ctx.send(f"Une erreur est survenue : {error}")

MOD_ROLE_ID = 1168109892851204166
MUTED_ROLE_ID = 1170488926834798602
IMMUNE_ROLE_ID = 1170326040485318686
LOG_CHANNEL_ID = 1345349357532090399

async def send_log(ctx, member, action, reason, duration=None):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="Formulaire des sanctions", color=discord.Color.red())
        embed.add_field(name="Pseudo de la personne sanctionnée:", value=member.mention, inline=False)
        embed.add_field(name="Pseudo du modérateur:", value=ctx.author.mention, inline=False)
        embed.add_field(name="Sanction:", value=action, inline=False)
        embed.add_field(name="Raison:", value=reason, inline=False)
        if duration:
            embed.add_field(name="Durée:", value=duration, inline=False)
        await log_channel.send(embed=embed)

async def send_dm(member, action, reason, duration=None):
    try:
        embed = discord.Embed(title="Sanction reçue", color=discord.Color.red())
        embed.add_field(name="Sanction:", value=action, inline=False)
        embed.add_field(name="Raison:", value=reason, inline=False)
        if duration:
            embed.add_field(name="Durée:", value=duration, inline=False)
        await member.send(embed=embed)
    except:
        print(f"Impossible d'envoyer un MP à {member.display_name}")

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')

async def check_permissions(ctx):
    mod_role = discord.utils.get(ctx.guild.roles, id=MOD_ROLE_ID)
    if mod_role in ctx.author.roles:
        return True
    else:
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")
        return False

async def is_immune(member):
    immune_role = discord.utils.get(member.guild.roles, id=IMMUNE_ROLE_ID)
    return immune_role in member.roles

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    if await check_permissions(ctx) and not await is_immune(member):
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} a été banni.")
        await send_log(ctx, member, "Ban", reason)
        await send_dm(member, "Ban", reason)

@bot.command()
async def unban(ctx, user_id: int):
    if await check_permissions(ctx):
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"{user.mention} a été débanni.")
        await send_log(ctx, user, "Unban", "Réintégration")
        await send_dm(user, "Unban", "Réintégration")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    if await check_permissions(ctx) and not await is_immune(member):
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} a été expulsé.")
        await send_log(ctx, member, "Kick", reason)
        await send_dm(member, "Kick", reason)

@bot.command()
async def mute(ctx, member: discord.Member, duration: int, unit: str, *, reason="Aucune raison spécifiée"):
    if await check_permissions(ctx) and not await is_immune(member):
        muted_role = discord.utils.get(ctx.guild.roles, id=MUTED_ROLE_ID)
        await member.add_roles(muted_role)
        
        if unit.lower() in ["m", "minute", "minutes"]:
            seconds = duration * 60
            duration_str = f"{duration} minute(s)"
        elif unit.lower() in ["h", "heure", "heures"]:
            seconds = duration * 3600
            duration_str = f"{duration} heure(s)"
        elif unit.lower() in ["d", "jour", "jours"]:
            seconds = duration * 86400
            duration_str = f"{duration} jour(s)"
        else:
            await ctx.send("Unité de temps invalide ! Utilisez m (minutes), h (heures) ou d (jours).")
            return

        await ctx.send(f"{member.mention} a été muté pour {duration_str}.")
        await send_log(ctx, member, "Mute", reason, duration_str)
        await send_dm(member, "Mute", reason, duration_str)

        await asyncio.sleep(seconds)
        await member.remove_roles(muted_role)
        await ctx.send(f"{member.mention} a été démuté après {duration_str}.")
        await send_log(ctx, member, "Unmute automatique", "Fin de la durée de mute")
        await send_dm(member, "Unmute", "Fin de la durée de mute")

@bot.command()
async def unmute(ctx, member: discord.Member):
    if await check_permissions(ctx) and not await is_immune(member):
        muted_role = discord.utils.get(ctx.guild.roles, id=MUTED_ROLE_ID)
        await member.remove_roles(muted_role)
        await ctx.send(f"{member.mention} a été démuté.")
        await send_log(ctx, member, "Unmute", "Réhabilitation")
        await send_dm(member, "Unmute", "Réhabilitation")

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="Aucune raison spécifiée"):
    if await check_permissions(ctx) and not await is_immune(member):
        await ctx.send(f"{member.mention} a reçu un avertissement.")
        await send_log(ctx, member, "Warn", reason)
        await send_dm(member, "Warn", reason)

# ID des rôles
access_role_id = 1166113718602575892  # Rôle qui peut utiliser la commande
ping_role_id = 1168109892851204166  # Rôle à mentionner dans l'embed

@bot.command()
async def alerte(ctx, member: discord.Member, *, reason: str):
    # Vérification si l'utilisateur a le rôle nécessaire pour exécuter la commande
    if access_role_id not in [role.id for role in ctx.author.roles]:
        await ctx.send("Vous n'avez pas les permissions nécessaires pour utiliser cette commande.")
        return

    # Création de l'embed
    embed = Embed(
        title="Alerte Émise",
        description=f"**Utilisateur:** {member.mention}\n**Raison:** {reason}",
        color=0xff0000  # Couleur rouge
    )

    # Mentionner le rôle dans l'embed
    embed.add_field(name="Ping Rôle", value=f"<@&{ping_role_id}>", inline=False)

    # Envoi de l'embed
    await ctx.send(embed=embed)

# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
