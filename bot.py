import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import random
import asyncio
import time
import datetime
import re
from keep_alive import keep_alive
from discord.ui import Button, View
from datetime import datetime
from discord.ui import View, Select
from discord.ext import tasks

token = os.environ['ETHERYA']
intents = discord.Intents.all()
start_time = time.time()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="+", intents=intents)

STAFF_ROLE_ID = 1244339296706760726

@bot.event
async def on_ready():
    print(f"✅ Le bot est connecté en tant que {bot.user} (ID: {bot.user.id})")

    # Afficher les commandes chargées
    print("📌 Commandes disponibles :")
    for command in bot.commands:
        print(f"- {command.name}")

    try:
        # Synchroniser les commandes avec Discord
        synced = await bot.tree.sync()  # Synchronisation des commandes slash
        print(f"✅ Commandes slash synchronisées : {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation des commandes slash : {e}")
    
    # Afficher les commandes disponibles après synchronisation
    print("📌 Commandes disponibles après synchronisation :")
    for command in bot.commands:
        print(f"- {command.name}")
    
    # Démarrer la boucle d'inactivité
    check_inactivity.start()
#------------------------------------------------------------------------- Commandes de Bienvenue : Message de Bienvenue + Ghost Ping Join
# ID du salon de bienvenue
WELCOME_CHANNEL_ID = 1344194595092697108

# Liste des salons à pinguer
salon_ids = [
1342179344889675827
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
#------------------------------------------------------------------------- Commandes d'Administration : Detections de Mots sensible:
# Liste des mots sensibles
sensitive_words = [
    "connard", "crétin", "idiot", "imbécile", "salopard", "enfoiré", "méchant",
    "pute", "salope", "con", "raciste", "sexiste", "homophobe", "antisémite", "xenophobe",
    "transphobe", "tuer", "assassin", "attaquer", "viol", "torturer", "menacer", "frapper",
    "guerre", "pervers", "abus", "sexe", "pornographie", "nu", "masturbation", "adultère",
    "drogue", "cocaïne", "héroïne", "crack", "alcool", "consommation abusive", "terrorisme",
    "jihad", "bombardement", "suicidaire", "hack", "pirater", "voler des données", "phishing",
    "ddos", "raid", "flood", "spam", "crasher", "ddos attack", "botnet", "infiltrer", "spammer",
    "griefing", "troll", "spam bot", "server crash", "exploiter"
]

ADMIN_ID = 792755123587645461

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore les messages du bot

    print(f"📩 Message reçu de {message.author}: {message.content}")

    # Vérification des mots sensibles avec regex
    for word in sensitive_words:
        if re.search(rf"\b{re.escape(word)}\b", message.content, re.IGNORECASE):
            print(f"🚨 Mot sensible détecté dans le message de {message.author}: {word}")
            
            # Exécuter l'envoi du message en arrière-plan pour ne pas bloquer les autres commandes
            asyncio.create_task(send_alert_to_admin(message, word))

            break  # Arrêter après la première détection

    # Permettre aux autres commandes de s'exécuter
    await bot.process_commands(message)

async def send_alert_to_admin(message, detected_word):
    try:
        admin = await bot.fetch_user(ADMIN_ID)
        print(f"✅ Admin trouvé : {admin}")

        # Création d'un embed stylisé
        embed = discord.Embed(
            title="🚨 Alerte : Mot sensible détecté !",
            description=f"Un message contenant un mot interdit a été détecté sur le serveur **{message.guild.name}**.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="📍 Salon", value=f"{message.channel.mention}", inline=True)
        embed.add_field(name="👤 Auteur", value=f"{message.author.mention} (`{message.author.id}`)", inline=True)
        embed.add_field(name="💬 Message", value=f"```{message.content}```", inline=False)
        embed.add_field(name="⚠️ Mot détecté", value=f"`{detected_word}`", inline=True)

        # Ajouter un lien vers le message si possible
        if message.guild:
            embed.add_field(name="🔗 Lien vers le message", value=f"[Clique ici]({message.jump_url})", inline=False)

        embed.set_footer(text="Système de détection automatique", icon_url=bot.user.avatar.url)

        await admin.send(embed=embed)
        print(f"✅ Alerte envoyée à l'admin {ADMIN_ID} en MP.")
    except discord.Forbidden:
        print(f"❌ Impossible d'envoyer un MP à l'admin {ADMIN_ID}. (MP bloqués)")
    except discord.HTTPException as e:
        print(f"⚠️ Erreur HTTP lors de l'envoi du MP : {e}")
    except Exception as e:
        print(f"⚠️ Erreur inconnue : {e}")

#------------------------------------------------------------------------- Commandes de Gestion : +clear, +nuke, +addrole, +delrole
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
    
#------------------------------------------------------------------------- Commandes d'aide : +aide
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
    embed.add_field(name="📚 **Informations**", value=f"• **Mon préfixe** : +\n• **Nombre de commandes** : 51", inline=False)

    # Création du menu déroulant
    select = discord.ui.Select(
        placeholder="Choisissez une catégorie 👇", 
        options=[
            discord.SelectOption(label="Gestion", description="📚 Commandes pour gérer le serveur", emoji="🔧"),
            discord.SelectOption(label="Économie", description="💸 Commandes économie", emoji="💰"),
            discord.SelectOption(label="Ludiques", description="🎉 Commandes amusantes pour détendre l'atmosphère et interagir avec les autres.", emoji="🎈"),
            discord.SelectOption(label="Test & Défis", description="🧠Commandes pour testez la personnalité et défiez vos amis avec des jeux et des évaluations.", emoji="🎲"),
            discord.SelectOption(label="Utilitaire", description="⚙️ Commandes utiles", emoji="🔔"),
            discord.SelectOption(label="Modération", description="⚖️ Commandes Modération", emoji="🔨"),
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
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Économie":
            new_embed.title = "⚖️ **Commandes Économie**"
            new_embed.description = "Gérez l’économie et la sécurité du serveur ici ! 💼"
            new_embed.add_field(name="🏰 +prison @user", value="Mets un utilisateur en prison pour taxes impayées.", inline=False)
            new_embed.add_field(name="🚔 +arrestation @user", value="Arrête un utilisateur après un braquage raté.", inline=False)
            new_embed.add_field(name="⚖️ +liberation @user", value="Libère un utilisateur après le paiement des taxes.", inline=False)
            new_embed.add_field(name="🔓 +evasion", value="Permet de s’évader après un braquage raté.", inline=False)
            new_embed.add_field(name="💰 +cautionpayer @user", value="Payez la caution d’un membre emprisonné.", inline=False)
            new_embed.add_field(name="🎫 +ticket_euro_million @user", value="Achetez un ticket Euromillion avec un combiné.", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Ludiques":
            new_embed.title = "🎉 **Commandes de Détente**"
            new_embed.description = "Bienvenue dans la section Détente ! 🎈\nCes commandes sont conçues pour vous amuser et interagir de manière légère et drôle. Profitez-en !"
            new_embed.add_field(name="🤗 +hug @user", value="Envoie un câlin à [membre] avec une image mignonne de câlin.", inline=False)
            new_embed.add_field(name="💥 +slap @user", value="Tu as giflé [membre] avec une image drôle de gifle.", inline=False)
            new_embed.add_field(name="💃 +dance @user", value="[membre] danse avec une animation rigolote.", inline=False)
            new_embed.add_field(name="💘 +flirt @user", value="Vous avez charmé [membre] avec un compliment !", inline=False)
            new_embed.add_field(name="💋 +kiss @user", value="Vous avez embrassé [membre] afin de lui démontrer votre amour !", inline=False)
            new_embed.add_field(name="🤫 +whisper @user [message]", value="[membre] a chuchoté à [ton nom] : [message].", inline=False)
            new_embed.add_field(name="🌟 +blague", value="Envoie une blague aléatoire, comme 'Pourquoi les plongeurs plongent toujours en arrière et jamais en avant ? Parce que sinon ils tombent toujours dans le bateau !'.", inline=False)
            new_embed.add_field(name="🪙 +coinflip", value="Lancez une pièce pour voir si vous gagnez ! \n*Tentez votre chance et découvrez si vous avez un coup de chance.*", inline=False)
            new_embed.add_field(name="🎲 +dice", value="Lancez un dé à 6 faces et voyez votre chance ! \n*Choisissez un numéro entre 1 et 6 et voyez si vous avez tiré le bon!*", inline=False)
            new_embed.add_field(name="🗣️ +say", value="Faites dire quelque chose au bot à la place de vous ! 🗨\n*Lancez votre message et il sera annoncé à tout le serveur !*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Test & Défis":
            new_embed.title = "🎯 **Commandes de Tests et Défis**"
            new_embed.description = "Bienvenue dans la section Tests et Défis ! 🎲\nIci, vous pouvez évaluer les autres, tester votre compatibilité et relever des défis fun !"
            new_embed.add_field(name="🌈 +gay @user", value="Détermine le taux de gayitude d'un utilisateur .\n*Testez votre ouverture d'esprit !*.", inline=False)
            new_embed.add_field(name="😤 +racist @user", value="Détermine le taux de racisme d'un utilisateur .\n*Un test amusant à faire avec vos amis.*", inline=False)
            new_embed.add_field(name="💘 +love @user", value="Affiche le niveau de compatibilité amoureuse .\n*Testez votre compatibilité avec quelqu'un !*.", inline=False)
            new_embed.add_field(name="🐀 +rat @user", value="Détermine le taux de ratitude d'un utilisateur .\n*Vérifiez qui est le plus ‘rat’ parmi vos amis.*", inline=False)
            new_embed.add_field(name="🍆 +zizi @user", value="Évalue le niveau de zizi de l'utilisateur .\n*Un test ludique pour voir qui a le plus grand ego !*.", inline=False)
            new_embed.add_field(name="🤡 +con @user", value="Détermine le taux de connerie d'un utilisateur .\n*Un test amusant à faire avec vos amis.*", inline=False)
            new_embed.add_field(name="🤪 +fou @user", value="Détermine le taux de folie d'un utilisateur .\n*Testez l'état mental de vos amis !*.", inline=False)
            new_embed.add_field(name="💪 +testo @user", value="Détermine le taux de testostérone d'un utilisateur .\n*Testez la virilité de vos amis !*.", inline=False)
            new_embed.add_field(name="🍑 +libido @user", value="Détermine le taux de libido d'un utilisateur .\n*Testez la chaleur de vos amis sous la couette !*.", inline=False)
            new_embed.add_field(name="🪴 +pfc @user", value="Jouez à Pierre-Feuille-Ciseaux avec un utilisateur ! \n*Choisissez votre coup et voyez si vous gagnez contre votre adversaire !*.", inline=False)
            new_embed.add_field(name="🔫 +gunfight @user", value="Affrontez un autre utilisateur dans un duel de Gunfight ! \n*Acceptez ou refusez le défi et découvrez qui sera le gagnant !*", inline=False)
            new_embed.add_field(name="💀 +kill @user", value="Tuez un autre utilisateur dans un duel de force ! \n*Acceptez ou refusez le défi et découvrez qui sortira vainqueur de cette confrontation!*", inline=False)
            new_embed.add_field(name="🔄 +reverse [texte]", value="Inverser un texte et le partager avec un autre utilisateur ! \n*Lancez un défi pour voir si votre inversion sera correcte !*", inline=False)
            new_embed.add_field(name="⭐ +note @user [note sur 10]", value="Notez un autre utilisateur sur 10 ! \n*Exprimez votre avis sur leur comportement ou performance dans le serveur.*", inline=False)
            new_embed.add_field(name="🎲 +roll", value="Lance un dé pour générer un nombre aléatoire entre 1 et 500 .\n*Essayez votre chance !*.", inline=False)
            new_embed.add_field(name="🥊 +fight @user", value="Lancez un duel avec un autre utilisateur ! \n*Acceptez ou refusez le combat et découvrez qui sera le champion du serveur.*", inline=False)
            new_embed.add_field(name="⚡ +superpouvoir @user", value="Déclenche un super-pouvoir épique pour un utilisateur !\n*Donne un pouvoir aléatoire allant du cool au complètement débile, comme la téléportation, la super vitesse, ou même la création de burgers.*", inline=False)
            new_embed.add_field(name="🌿 +totem @user", value="Découvrez votre animal totem spirituel !\n*Un animal magique et spirituel vous guidera, qu’il soit un loup protecteur ou un poisson rouge distrait. Un résultat épique et amusant !*", inline=False)
            new_embed.add_field(name="🔮 +futur @user", value="Prédit l'avenir d'un utilisateur de manière totalement farfelue !\n*L'avenir peut être aussi improbable qu'un trésor caché rempli de bonbons ou une rencontre avec un extraterrestre amateur de chats.*", inline=False)
            new_embed.add_field(
            name="👶 +enfant @user @user", value="Crée un enfant aléatoire entre deux utilisateurs !\n*Mélangez les pseudos et les photos de profil des deux utilisateurs pour créer un bébé unique. C'est fun et surprenant !*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Utilitaire":
            new_embed.title = "⚙️ **Commandes Utilitaires**"
            new_embed.description = "Bienvenue dans la section modération ! 🚨\nCes commandes sont conçues pour gérer et contrôler l'activité du serveur, en assurant une expérience sûre et agréable pour tous les membres."
            new_embed.add_field(name="📊 +vc", value="Affiche les statistiques du serveur en temps réel .\n*Suivez l'évolution du serveur en direct !*.", inline=False)
            new_embed.add_field(name="🚨 +alerte @user <reason>", value="Envoie une alerte au staff en cas de comportement inapproprié (insultes, spam, etc.) .\n*Note : Si cette commande est utilisée abusivement, des sanctions sévères seront appliquées !*.", inline=False)
            new_embed.add_field(name="📶 +ping", value="Affiche la latence du bot en millisecondes.", inline=False)
            new_embed.add_field(name="⏳ +uptime", value="Affiche depuis combien de temps le bot est en ligne.", inline=False)
            new_embed.add_field(name="ℹ️ +rôle info <nom_du_rôle>", value="Affiche les informations détaillées sur un rôle spécifique.", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Modération":
            new_embed.title = "🔑 **Commandes Modération**"
            new_embed.add_field(name="🚫 +ban @user", value="Exile un membre du serveur pour un comportement inacceptable .\nL'action de bannir un utilisateur est irréversible et est utilisée pour des infractions graves aux règles du serveur.*", inline=False)
            new_embed.add_field(name="🚔 +unban @user", value="Lève le bannissement d'un utilisateur, lui permettant de revenir sur le serveur .\nUnban un utilisateur qui a été banni, après examen du cas et décision du staff..*", inline=False)
            new_embed.add_field(name="⚖️ +mute @user", value="Rend un utilisateur silencieux en l'empêchant de parler pendant un certain temps .\nUtilisé pour punir les membres qui perturbent le serveur par des messages intempestifs ou offensants.", inline=False)
            new_embed.add_field(name="🔓 +unmute @user", value="Annule le silence imposé à un utilisateur et lui redonne la possibilité de communiquer 🔊.\nPermet à un membre de reprendre la parole après une période de mute.", inline=False)
            new_embed.add_field(name="⚠️ +warn @user", value="Avertit un utilisateur pour un comportement problématique ⚠.\nUn moyen de signaler qu'un membre a enfreint une règle mineure, avant de prendre des mesures plus sévères.", inline=False)
            new_embed.add_field(name="🚪 +kick @user", value="Expulse un utilisateur du serveur pour une infraction moins grave .\nUn kick expulse temporairement un membre sans le bannir, pour des violations légères des règles.", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Crédits":
            new_embed.title = "💖 **Crédits et Remerciements**"
            new_embed.description = """
            Un immense merci à **Iseyg** pour le développement de ce bot incroyable ! 🙏  
            Sans lui, ce bot ne serait rien de plus qu'un concept. Grâce à sa passion, son travail acharné et ses compétences exceptionnelles, ce projet a pris vie et continue de grandir chaque jour. 🚀

            Nous tenons également à exprimer notre gratitude envers **toute la communauté**. 💙  
            Votre soutien constant, vos retours et vos idées font de ce bot ce qu'il est aujourd'hui. Chacun de vous, que ce soit par vos suggestions, vos contributions ou même simplement en utilisant le bot, fait une différence. 

            Merci à **tous les développeurs, contributeurs et membres** qui ont aidé à faire évoluer ce projet et l’ont enrichi avec leurs talents et leurs efforts. 🙌

            Et bien sûr, un grand merci à vous, **utilisateurs**, pour votre enthousiasme et votre confiance. Vous êtes la raison pour laquelle ce bot continue d’évoluer. 🌟

            Restons unis et continuons à faire grandir cette aventure ensemble ! 🌍
            """
            new_embed.set_footer(text="♥️ by Iseyg")

        await interaction.response.edit_message(embed=new_embed)

    select.callback = on_select  # Attacher la fonction de callback à l'élément select

    # Afficher le message avec le menu déroulant
    view = discord.ui.View()
    view.add_item(select)
    
    await ctx.send(embed=embed, view=view)

#------------------------------------------------------------------------- Commandes Fun : Flemme de tout lister
@bot.command()
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} ♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    embed.set_thumbnail(url="https://img.freepik.com/photos-gratuite/silhouette-mains-coeur-contre-lumieres-ville-nuit_23-2150984259.jpg?ga=GA1.1.719997987.1741155829&semt=ais_hybrid")

    await ctx.send(embed=embed)

@bot.command()
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def libido(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title="Analyse de libido 🔥",
        description=f"{member.mention} a une libido à **{percentage}%** !\n\n*Le pourcentage varie en fonction de l'humeur et du climat.*",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    # Envoyer l'embed
    await ctx.send(embed=embed)

@bot.command()
async def fou(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title=f"Analyse de folie 🤪", 
        description=f"{member.mention} est fou à **{percentage}%** !\n\n*Le pourcentage varie en fonction de l'état mental du membre.*", 
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def testo(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title=f"Analyse de testostérone 💪", 
        description=f"{member.mention} a un taux de testostérone de **{percentage}%** !\n\n*Le pourcentage varie en fonction des niveaux de virilité du membre.*", 
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

class PFCView(View):
    def __init__(self, player1, player2):
        super().__init__(timeout=60)
        self.choices = {}
        self.player1 = player1
        self.player2 = player2
        
        for choice in ['Pierre', 'Feuille', 'Ciseau']:
            self.add_item(PFCButton(choice, self))

    async def check_winner(self):
        if len(self.choices) == 2:
            p1_choice = self.choices[self.player1]
            p2_choice = self.choices[self.player2]
            result = determine_winner(p1_choice, p2_choice)
            
            winner_text = {
                'win': f"{self.player1.mention} a gagné !",
                'lose': f"{self.player2.mention} a gagné !",
                'draw': "Match nul !"
            }
            
            embed = discord.Embed(title="Résultat du Pierre-Feuille-Ciseaux !", description=f"{self.player1.mention} a choisi **{p1_choice}**\n{self.player2.mention} a choisi **{p2_choice}**\n\n{winner_text[result]}", color=0x00FF00)
            await self.player1.send(embed=embed)
            await self.player2.send(embed=embed)
            await self.message.edit(embed=embed, view=None)

class PFCButton(Button):
    def __init__(self, choice, view):
        super().__init__(label=choice, style=discord.ButtonStyle.primary)
        self.choice = choice
        self.pfc_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user in [self.pfc_view.player1, self.pfc_view.player2]:
            if interaction.user not in self.pfc_view.choices:
                self.pfc_view.choices[interaction.user] = self.choice
                await interaction.response.send_message(f"{interaction.user.mention} a choisi **{self.choice}**", ephemeral=True)
                if len(self.pfc_view.choices) == 2:
                    await self.pfc_view.check_winner()
            else:
                await interaction.response.send_message("Tu as déjà choisi !", ephemeral=True)
        else:
            await interaction.response.send_message("Tu ne participes pas à cette partie !", ephemeral=True)

def determine_winner(choice1, choice2):
    beats = {"Pierre": "Ciseau", "Ciseau": "Feuille", "Feuille": "Pierre"}
    if choice1 == choice2:
        return "draw"
    elif beats[choice1] == choice2:
        return "win"
    else:
        return "lose"

class AcceptView(View):
    def __init__(self, ctx, player1, player2):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.player1 = player1
        self.player2 = player2

        self.add_item(AcceptButton("✅ Accepter", discord.ButtonStyle.success, True, self))
        self.add_item(AcceptButton("❌ Refuser", discord.ButtonStyle.danger, False, self))

class AcceptButton(Button):
    def __init__(self, label, style, accept, view):
        super().__init__(label=label, style=style)
        self.accept = accept
        self.accept_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.accept_view.player2:
            return await interaction.response.send_message("Ce n'est pas à toi d'accepter ou refuser !", ephemeral=True)
        
        if self.accept:
            embed = discord.Embed(title="Pierre-Feuille-Ciseaux", description=f"{self.accept_view.player1.mention} VS {self.accept_view.player2.mention}\n\nCliquez sur votre choix !", color=0x00FF00)
            await interaction.message.edit(embed=embed, view=PFCView(self.accept_view.player1, self.accept_view.player2))
        else:
            await interaction.message.edit(content=f"Le +pfc a été refusé par {self.accept_view.player2.mention}", embed=None, view=None)

@bot.command()
async def pfc(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("Vous devez mentionner un adversaire pour jouer !")
    if member == ctx.author:
        return await ctx.send("Vous ne pouvez pas jouer contre vous-même !")
    
    embed = discord.Embed(title="Défi Pierre-Feuille-Ciseaux", description=f"{member.mention}, acceptes-tu le défi de {ctx.author.mention} ?", color=0xFFA500)
    await ctx.send(embed=embed, view=AcceptView(ctx, ctx.author, member))

@bot.command()
async def gunfight(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send('Erreur : vous devez cibler un membre !')
        return

    if member == ctx.author:
        await ctx.send('Vous ne pouvez pas vous défier vous-même !')
        return

    # Création des boutons
    accept_button = Button(label="Oui", style=discord.ButtonStyle.green)
    decline_button = Button(label="Non", style=discord.ButtonStyle.red)

    # Définir les actions des boutons
    async def accept(interaction):
        if interaction.user != member:
            await interaction.response.send_message('Ce n\'est pas votre duel !', ephemeral=True)
            return
        result = random.choice([ctx.author, member])
        winner = result.name
        await interaction.message.edit(content=f"{member.mention} a accepté le duel ! Le gagnant est {winner} !", view=None)
    
    async def decline(interaction):
        if interaction.user != member:
            await interaction.response.send_message('Ce n\'est pas votre duel !', ephemeral=True)
            return
        await interaction.message.edit(content=f"{member.mention} a refusé le duel.", view=None)

    accept_button.callback = accept
    decline_button.callback = decline

    # Création de la vue avec les boutons
    view = View()
    view.add_item(accept_button)
    view.add_item(decline_button)

    # Envoyer l'embed pour le défi
    embed = discord.Embed(
        title="Défi de Gunfight",
        description=f"{ctx.author.mention} vous défie à un duel, {member.mention}. Acceptez-vous ?",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=view)
    
@bot.command()
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
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
    embed.set_footer(text=f"Un message secret entre vous deux... {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def kill(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Tu as tué {member.name} !",  # Utilisation de member.name
        description="C'est la fin pour lui... 💀",  
        color=discord.Color.red()
    )
    embed.set_image(url="https://media1.tenor.com/m/4hO2HfS9fcMAAAAd/toaru-index.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
async def reverse(ctx, *, text: str = None):
    if text is None:
        await ctx.send("Tu n'as pas fourni de texte à inverser !")
        return

    reversed_text = text[::-1]  # Inverser le texte
    await ctx.send(f"Texte inversé : {reversed_text}")

@bot.command()
async def note(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Tu n'as pas précisé l'utilisateur !")
        return

    # Générer une note aléatoire entre 1 et 10
    note = random.randint(1, 10)

    # Créer l'embed
    embed = discord.Embed(
        title=f"{member.name} a reçu une note !",
        description=f"Note : {note}/10",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


AUTHORIZED_ROLES = ["1244339296706760726"]

@bot.command()
async def say(ctx, *, text: str = None):
    # Vérifie si l'utilisateur a le rôle avec l'ID spécifié
    if str(ctx.author.id) not in AUTHORIZED_ROLES:
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")
        return
    
    if text is None:
        await ctx.send("Tu n'as pas écrit de texte à dire !")
        return

    # Supprime le message originel
    await ctx.message.delete()
    # Envoie le texte spécifié
    await ctx.send(text)


    # Envoie le texte demandé
    await ctx.send(text)

    # Supprime le message originel
    await ctx.message.delete()

    # Envoie le texte demandé
    await ctx.send(text)


@bot.command()
async def coinflip(ctx):
    import random
    result = random.choice(["Pile", "Face"])
    await ctx.send(f"Résultat du coinflip : {result}")


@bot.command()
async def dice(ctx):
    import random
    result = random.randint(1, 6)
    await ctx.send(f"Résultat du dé : {result}")


@bot.command()
async def fight(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Tu n'as ciblé personne pour te battre !")
        return

    # Simuler un combat
    import random
    result = random.choice([f"{ctx.author.name} a gagné !", f"{member.name} a gagné !", "C'est une égalité !"])

    # Créer l'embed
    embed = discord.Embed(
        title=f"Combat entre {ctx.author.name} et {member.name}",
        description=result,
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def enfant(ctx, parent1: discord.Member = None, parent2: discord.Member = None):
    if not parent1 or not parent2:
        await ctx.send("Tu dois mentionner deux membres ! Utilise `/enfant @membre1 @membre2`.")
        return
    
    # Génération du prénom en combinant les pseudos
    prenom = parent1.name[:len(parent1.name)//2] + parent2.name[len(parent2.name)//2:]
    
    # Création de l'embed
    embed = discord.Embed(
        title="👶 Voici votre enfant !",
        description=f"{parent1.mention} + {parent2.mention} = **{prenom}** 🍼",
        color=discord.Color.purple()
    )
    embed.set_footer(text=f"Prenez soin de votre bébé ! {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    # Ajout des photos de profil
    embed.set_thumbnail(url=parent1.avatar.url if parent1.avatar else parent2.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def superpouvoir(ctx, user: discord.Member = None):
    if not user:
        user = ctx.author  # Si pas d’utilisateur mentionné, prendre l’auteur

    pouvoirs = [
        "Téléportation instantanée 🌀 - Peut se déplacer n'importe où en un clin d'œil.",
        "Contrôle du feu 🔥 - Rien ne lui résiste… sauf l'eau.",
        "Super vitesse ⚡ - Peut courir plus vite qu'un TGV, mais oublie souvent où il va.",
        "Lecture des pensées 🧠 - Peut lire dans les esprits… sauf ceux qui ne pensent à rien.",
        "Invisibilité 🫥 - Peut disparaître… mais oublie que ses vêtements restent visibles.",
        "parler aux animaux 🦜 - Mais ils n'ont pas grand-chose d'intéressant à dire.",
        "Super force 💪 - Peut soulever une voiture, mais galère à ouvrir un pot de cornichons.",
        "Métamorphose 🦎 - Peut se transformer en n'importe quoi… mais pas revenir en humain.",
        "Chance infinie 🍀 - Gagne à tous les jeux… sauf au Uno.",
        "Création de portails 🌌 - Peut ouvrir des portails… mais ne sait jamais où ils mènent.",
        "Régénération 🩸 - Guérit instantanément… mais reste chatouilleux à vie.",
        "Capacité de voler 🕊️ - Mais uniquement à 10 cm du sol.",
        "Super charisme 😎 - Convainc tout le monde… sauf sa mère.",
        "Vision laser 🔥 - Brûle tout sur son passage… y compris ses propres chaussures.",
        "Invocation de clones 🧑‍🤝‍🧑 - Mais ils n’obéissent jamais.",
        "Télékinésie ✨ - Peut déplacer des objets… mais uniquement des plumes.",
        "Création de burgers 🍔 - Magique, mais toujours trop cuits ou trop crus.",
        "Respiration sous l'eau 🐠 - Mais panique dès qu'il voit une méduse.",
        "Contrôle de la gravité 🌍 - Peut voler, mais oublie souvent de redescendre.",
        "Capacité d’arrêter le temps ⏳ - Mais uniquement quand il dort."
    ]

    pouvoir = random.choice(pouvoirs)

    embed = discord.Embed(
        title="⚡ Super-Pouvoir Débloqué !",
        description=f"{user.mention} possède le pouvoir de**{pouvoir}** !",
        color=discord.Color.purple()
    )
    embed.set_footer(text=f"Utilise-le avec sagesse... ou pas. {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def totem(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author  # Si pas de membre mentionné, prendre l'auteur  

    animaux_totem = {
        "Loup 🐺": "Fidèle et protecteur, il veille sur sa meute.",
        "Renard 🦊": "Rusé et malin, il trouve toujours un moyen de s'en sortir.",
        "Hibou 🦉": "Sage et observateur, il comprend tout avant les autres.",
        "Dragon 🐉": "Puissant et imposant, il ne laisse personne indifférent.",
        "Dauphin 🐬": "Joueur et intelligent, il adore embêter les autres.",
        "Chat 🐱": "Mystérieux et indépendant, il fait ce qu’il veut, quand il veut.",
        "Serpent 🐍": "Discret et patient, il attend le bon moment pour frapper.",
        "Corbeau 🦅": "Intelligent et un peu sinistre, il voit ce que les autres ignorent.",
        "Panda 🐼": "Calme et adorable… jusqu’à ce qu’on lui prenne son bambou.",
        "Tortue 🐢": "Lente mais sage, elle gagne toujours à la fin.",
        "Aigle 🦅": "Libre et fier, il vole au-dessus de tous les problèmes.",
        "Chauve-souris 🦇": "Préférant l'obscurité, elle voit clair quand tout le monde est perdu.",
        "Tigre 🐯": "Puissant et rapide, personne ne l’arrête.",
        "Lapin 🐰": "Rapide et malin, mais fuit dès qu’il y a un problème.",
        "Singe 🐵": "Curieux et joueur, il adore faire des bêtises.",
        "Escargot 🐌": "Lent… mais au moins il arrive toujours à destination.",
        "Pigeon 🕊️": "Increvable et partout à la fois, impossible de s'en débarrasser.",
        "Licorne 🦄": "Rare et magique, il apporte de la lumière partout où il passe.",
        "Poisson rouge 🐠": "Mémoire de 3 secondes, mais au moins il ne s’inquiète jamais.",
        "Canard 🦆": "Semble idiot, mais cache une intelligence surprenante.",
        "Raton laveur 🦝": "Petit voleur mignon qui adore piquer des trucs."
    }

    totem, description = random.choice(list(animaux_totem.items()))

    embed = discord.Embed(
        title=f"🌿 Totem de {member.name} 🌿",
        description=f"**{totem}** : {description}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)
    
@bot.command()
async def futur(ctx, user: discord.Member = None):
    if not user:
        user = ctx.author  # Si pas d’utilisateur mentionné, prendre l’auteur

    predicions = [
        "Dans 5 minutes, tu découvriras un trésor caché… mais il sera rempli de bonbons.",
        "L'année prochaine, tu feras une rencontre étonnante avec un extraterrestre qui adore les chats.",
        "Demain, tu auras une conversation intense avec un pigeon, et il te donnera un conseil de vie précieux.",
        "Un chat va te confier un secret qui changera le cours de ton existence… mais tu ne te souviendras pas de ce secret.",
        "Dans quelques jours, tu seras élu meilleur joueur de cache-cache, mais tu te cacheras dans une pièce vide.",
        "Lundi, tu rencontreras quelqu'un qui aime les licornes autant que toi. Vous deviendrez amis pour la vie.",
        "Dans un futur proche, tu réussiras à inventer un gâteau qui ne se mange pas, mais il sera étonnamment populaire.",
        "Bientôt, un mystérieux inconnu t'offrira un paquet cadeau. Il contiendra un élastique et une noix de coco.",
        "Dans un mois, tu vivras une aventure épique où tu devras résoudre un mystère impliquant des chaussettes perdues.",
        "Prochainement, tu seras récompensé pour avoir trouvé une solution révolutionnaire au problème de la pizza froide.",
        "Dans un futur lointain, tu seras le leader d'une civilisation intergalactique. Tes sujets seront principalement des pandas."
    ]

    prediction = random.choice(predicions)

    embed = discord.Embed(
        title=f"🔮 Prédiction pour {user.name} 🔮",
        description=f"**Prédiction :**\n\n{prediction}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Le futur est incertain… mais amusant ! {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# Liste de blagues
blagues = [
    "Pourquoi les plongeurs plongent toujours en arrière et jamais en avant ? ||Parce que sinon ils tombent toujours dans le bateau.||",
    "Pourquoi les canards sont toujours à l'heure ? ||Parce qu'ils sont dans les starting-quack !||",
    "Quel est le comble pour un électricien ? ||De ne pas être au courant.||",
    "Pourquoi les maths sont tristes ? ||Parce qu'elles ont trop de problèmes.||",
    "Que dit une imprimante à une autre imprimante ? *||'T'as du papier ?'||",
    "Pourquoi les poissons détestent l'ordinateur ? ||Parce qu'ils ont peur du net !||",
    "Comment appelle-t-on un chat qui a perdu son GPS ? ||Un chat égaré.||",
    "Pourquoi les squelettes ne se battent-ils jamais entre eux ? ||Parce qu'ils n'ont pas de cœur !||",
    "Quel est le comble pour un plombier ? ||D'avoir un tuyau percé.||",
    "Comment appelle-t-on un chien magique ? ||Un labra-cadabra !||"
]

# Commande !blague
@bot.command()
async def blague(ctx):
    # Choisir une blague au hasard
    blague_choisie = random.choice(blagues)
    # Envoyer la blague dans le salon
    await ctx.send(blague_choisie)
#------------------------------------------------------------------------- Commandes d'économie : +prison, +evasion, +arrestation, +liberation, +cautionpayer, +ticket_euro_million
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
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
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
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
        
@bot.command()
@commands.has_role(1347165421958205470)
async def cautionpayer(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("Vous n'avez ciblé personne.")
        return

    embed = discord.Embed(
        title="Caution payée avec succès !",
        description="Vous êtes maintenant libre de retourner dans l'économie.",
        color=0x00ff00
    )
    embed.set_image(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/1dnyLPXGJgsrcmMo8Bgi4.jpg?raw=true")
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

    # Gestion des rôles
    role_remove = discord.utils.get(ctx.guild.roles, id=1344453363261116468)
    role_remove = discord.utils.get(ctx.guild.roles, id=1347165421958205470)
    if role_remove:
        await member.remove_roles(role_remove)

AUTHORIZED_ROLES = ["1341458600559644672"]

@bot.command()
async def ticket_euro_million(ctx, user: discord.Member):
    # Générer 5 chiffres entre 0 et 5
    numeros = [str(random.randint(0, 5)) for _ in range(5)]
    combinaison = " - ".join(numeros)
    
    # Créer l'embed pour le salon où la commande a été exécutée
    embed_user = discord.Embed(
        title="🎟️ Ticket Euro Million",
        description=f"Voici votre combinaison, **{user.mention}** : **{combinaison}**\n\n"
                    f"Bonne chance ! 🍀",
        color=discord.Color.gold()
    )
    embed_user.set_footer(text="Ticket généré par " + ctx.author.name)
    embed.set_footer(text=f"♥️by Iseyg", icon_url=ctx.author.avatar.url)

    # Envoie de l'embed dans le salon où la commande a été effectuée
    await ctx.send(embed=embed_user)
    
    # Créer un deuxième embed pour le salon spécifique
    embed_announce = discord.Embed(
        title="🎟️ Euro Million - Résultat",
        description=f"**{user.mention}** a tiré le combiné suivant : **{combinaison}**\n\n"
                    f"Commande exécutée par : **{ctx.author.mention}**",
        color=discord.Color.green()
    )
    embed_announce.set_footer(text="Ticket généré avec succès !")
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    # Envoie de l'embed dans le salon spécifique (ID du salon : 1343358346287120514)
    salon_announce = bot.get_channel(1343358346287120514)
    if salon_announce:
        await salon_announce.send(embed=embed_announce)
    else:
        await ctx.send("Erreur : Le salon d'annonce est introuvable.")
#------------------------------------------------------------------------- Commandes de Moderation : +ban, +unban, +mute, +unmute, +kick, +warn
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
    except discord.Forbidden:
        print(f"Impossible d'envoyer un DM à {member.display_name}.")

async def check_permissions(ctx):
    if ctx.guild is None:  # Empêche l'utilisation en DM
        await ctx.send("Cette commande ne peut être utilisée que sur un serveur.")
        return False

    mod_role = discord.utils.get(ctx.guild.roles, id=MOD_ROLE_ID)
    if mod_role and mod_role in ctx.author.roles:
        return True
    else:
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")
        return False

async def is_immune(member):
    immune_role = discord.utils.get(member.guild.roles, id=IMMUNE_ROLE_ID)
    return immune_role and immune_role in member.roles

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
async def mute(ctx, member: discord.Member, duration_with_unit: str, *, reason="Aucune raison spécifiée"):
    # Vérification si l'utilisateur a le rôle autorisé
    if not any(role.id == 1168109892851204166 for role in ctx.author.roles):
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")
        return
    
    # Extraction de la durée et de l'unité
    try:
        duration = int(duration_with_unit[:-1])  # Tout sauf le dernier caractère
        unit = duration_with_unit[-1]  # Dernier caractère (unité)
    except ValueError:
        await ctx.send("Format invalide ! Utilisez un nombre suivi de m (minutes), h (heures) ou j (jours). Exemple : 10m, 2h, 1j.")
        return

    if await check_permissions(ctx) and not await is_immune(member):
        muted_role = discord.utils.get(ctx.guild.roles, id=MUTED_ROLE_ID)
        await member.add_roles(muted_role)
        
        if unit.lower() in ["m", "minute", "minutes"]:
            seconds = duration * 60
            duration_str = f"{duration} minute(s)"
        elif unit.lower() in ["h", "heure", "heures"]:
            seconds = duration * 3600
            duration_str = f"{duration} heure(s)"
        elif unit.lower() in ["j", "jour", "jours"]:
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

# ID des rôles et du salon
access_role_id = 1166113718602575892  # Rôle qui peut utiliser la commande
ping_role_id = 1168109892851204166  # Rôle à mentionner avant l'embed
channel_id = 1345369756148170805  # Salon où l'alerte doit être envoyée

#------------------------------------------------------------------------- Commandes Utilitaires : +vc, +alerte, +uptime, +ping, +roleinfo
@bot.command()
async def alerte(ctx, member: discord.Member, *, reason: str):
    # Vérification si l'utilisateur a le rôle nécessaire pour exécuter la commande
    if access_role_id not in [role.id for role in ctx.author.roles]:
        await ctx.send("Vous n'avez pas les permissions nécessaires pour utiliser cette commande.")
        return

    # Obtention du salon où envoyer le message
    channel = bot.get_channel(channel_id)

    # Mentionner le rôle et l'utilisateur qui a exécuté la commande dans le message
    await channel.send(f"<@&{ping_role_id}>\n📢 Alerte émise par {ctx.author.mention}: {member.mention} - Raison : {reason}")

    # Création de l'embed
    embed = discord.Embed(
        title="Alerte Émise",
        description=f"**Utilisateur:** {member.mention}\n**Raison:** {reason}",
        color=0xff0000  # Couleur rouge
    )
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    # Envoi de l'embed dans le même salon
    await channel.send(embed=embed)

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
    embed.set_footer(text="📈 Statistiques mises à jour en temps réel | ♥️ by Iseyg")
    
    await ctx.send(embed=embed)
    # IMPORTANT : Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)
    
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)  # Latence en ms
    embed = discord.Embed(title="Pong!", description=f"Latence: {latency}ms", color=discord.Color.green())

    await ctx.send(embed=embed)

@bot.command()
async def roleinfo(ctx, *, role_name: str):
    # Cherche le rôle par son nom
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role is None:
        embed = discord.Embed(title="Erreur", description="Rôle introuvable.", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    else:
        embed = discord.Embed(title=f"Informations sur le rôle: {role.name}", color=role.color)
        embed.add_field(name="ID", value=role.id)
        embed.add_field(name="Couleur", value=str(role.color))
        embed.add_field(name="Nombre de membres", value=len(role.members))
        embed.add_field(name="Position", value=role.position)
        embed.set_footer(text=f"♥️by Iseyg", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

@bot.command()
async def uptime(ctx):
    uptime_seconds = round(time.time() - start_time)
    days = uptime_seconds // (24 * 3600)
    hours = (uptime_seconds % (24 * 3600)) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    embed = discord.Embed(
        title="Uptime du bot",
        description=f"Le bot est en ligne depuis : {days} jours, {hours} heures, {minutes} minutes, {seconds} secondes",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"♥️by Iseyg", icon_url=ctx.author.avatar.url)
#------------------------------------------------------------------------- Inactivité : Detection d'inactvité

CHANNEL_ID = 1166081599230709830  # Remplace par l'ID du salon à surveiller
CHECK_INTERVAL = 600  # Vérification toutes les 10 minutes (600 sec)
INACTIVITY_THRESHOLD = 3 * 3600  # 3 heures en secondes
WARNING_IMAGE_URL = "https://cdn.gamma.app/m6u5udkwwfl3cxy/generated-images/efL0tB_pALZ6fv0DVFXml.jpg"  # Mets une URL d'image ici

@tasks.loop(seconds=CHECK_INTERVAL)
async def check_inactivity():
    # Récupérer le salon par son ID
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        # Vérifier l'historique des messages
        async for message in channel.history(limit=1):
            # Calculer la différence de temps
            time_diff = (discord.utils.utcnow() - message.created_at).total_seconds()
            print(f"Time difference: {time_diff} secondes")  # Afficher la différence pour déboguer
            if time_diff > INACTIVITY_THRESHOLD:
                embed = discord.Embed(
                    title="💤 Le chat est endormi !",
                    description="Il n'y a eu aucun message depuis 3 Heures ! Réveillez le chat 🗣️",
                    color=discord.Color.red()
                )
                embed.set_image(url=WARNING_IMAGE_URL)
                await channel.send(content="<@&1166334752186433567> **Réveillez le chat !**", embed=embed)
    else:
        print("Le salon spécifié n'a pas été trouvé ou le bot n'a pas accès au salon.")

#------------------------------------------------------------------------- Commandes Braquages : Flemme de Lister
    await ctx.send(embed=embed)
class DynamiteGame(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.winning_spots = random.sample(range(9), 3)
            self.grid = [
                "<:coffrefort1:1344730431144329341>", "<:coffrefort2:1344434909602910301>", "<:coffrefort1:1344435008798195753>",
                "<:coffrefort1:1344435054704590969>", "<:coffrefort1:1344435190352576542>", "<:coffrefort6:1344435248443953354>",
                "<:coffrefort7:1344435296074334379>", "<:coffrefort8:1344435352047190147>", "<:coffrefort9:1344435400348799017>"
            ]
            self.game_over = False

        def update_grid(self):
            return "  ".join(self.grid[:3]) + "\n" + "  ".join(self.grid[3:6]) + "\n" + "  ".join(self.grid[6:])

        @discord.ui.button(label="", style=discord.ButtonStyle.red, emoji="<:1_:1344757365643153622>")
        async def button_1(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.handle_click(interaction, 0, button)

        @discord.ui.button(label="", style=discord.ButtonStyle.red, emoji="<:2_:1344757389739560970>")
        async def button_2(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.handle_click(interaction, 1, button)

        @discord.ui.button(label="", style=discord.ButtonStyle.red, emoji="<:3_:1344757414360252630>")
        async def button_3(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.handle_click(interaction, 2, button)

        @discord.ui.button(label="", style=discord.ButtonStyle.red, emoji="<:4_:1344757434874335414>")
        async def button_4(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.handle_click(interaction, 3, button)

        @discord.ui.button(label="", style=discord.ButtonStyle.red, emoji="<:5_:1344757454789148723>")
        async def button_5(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.handle_click(interaction, 4, button)

        @discord.ui.button(label="", style=discord.ButtonStyle.red, emoji="<:6_:1344757502142582918>")
        async def button_6(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.handle_click(interaction, 5, button)

        @discord.ui.button(label="", style=discord.ButtonStyle.red, emoji="<:7_:1344757527866507365>")
        async def button_7(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.handle_click(interaction, 6, button)

        @discord.ui.button(label="", style=discord.ButtonStyle.red, emoji="<:8_:1344757546518446142>")
        async def button_8(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.handle_click(interaction, 7, button)

        @discord.ui.button(label="", style=discord.ButtonStyle.red, emoji="<:9_:1344757668555788299>")
        async def button_9(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.handle_click(interaction, 8, button)

        async def handle_click(self, interaction: discord.Interaction, index: int, button: discord.ui.Button):
            if self.game_over:
                return await interaction.response.send_message("La partie est déjà terminée ! Merci d'avoir joué.", ephemeral=True)

            if index in self.winning_spots:
                button.style = discord.ButtonStyle.success
                button.emoji = "<:Dynamite:1344744174796410981>"
                self.game_over = True
                embed = discord.Embed(
                    title="💣 Braquage réussi ! 💸",
                    description=f"{interaction.user.mention} 🎉 Vous avez réussi à braquer la banque ! 💣💸 Félicitations, vous remportez des <:EzrinCoin:1344742958804635700> !",
                    color=discord.Color.green()
                )
                # Ajout du GIF comme image dans l'embed
                embed.set_image(url="https://media1.tenor.com/m/Z8GdGNlTC5oAAAAd/ready-to-rob-pops-mask.gif")

                for child in self.children:
                    if isinstance(child, discord.ui.Button):
                        child.disabled = True
            else:
                button.style = discord.ButtonStyle.danger
                button.emoji = "<a:Alerte:1344758825273528340>"
                self.game_over = True
                embed = discord.Embed(
                    title="🚨 Braquage échoué ! 🛑",
                    description=f"{interaction.user.mention} 🚨 Oh non ! Les policiers arrivent ! 🚔 Votre tentative de braquage a échoué. 🛑",
                    color=discord.Color.red()
                )
                # Ajout du GIF comme image dans l'embed
                embed.set_image(url="https://media1.tenor.com/m/tj3ltZKxO94AAAAd/cops-police.gif")

                for child in self.children:
                    if isinstance(child, discord.ui.Button):
                        child.disabled = True

            await interaction.response.edit_message(content=self.update_grid(), view=self)
            await interaction.channel.send(embed=embed)


@bot.command()
async def start(ctx):
        await ctx.message.delete()

        embed = discord.Embed(
            title="<:EzrinCoin:1344742958804635700> Braquage de Banque : L'Heist ! 💣",
            description=(
                "🔫 *Bienvenue dans l'ultime braquage de banque !* 💥\n\n"
                "Tentez de trouver les caches de dynamite parmi les 9 coffres, choisissez judicieusement...\n"
                "Chaque coffre peut soit cacher de l'argent, soit... une explosion qui finira votre tentative !\n\n"
                "Vous avez 3 chances sur 9 de réussir à braquer la banque ! \n"
                "Bonne chance... et ne vous laissez pas surprendre par les policiers 🚔 !"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Les récompenses sont en <:EzrinCoin:1344742958804635700>.")

        game = DynamiteGame()
        await ctx.send(embed=embed)
        await ctx.send(game.update_grid(), view=game)


class LuckGame(discord.ui.View):
    def __init__(self, health_message):
        super().__init__()
        self.health = 100  # Vie initiale
        self.wins = 0
        self.correct_button = None
        self.choose_random_button()
        self.health_message = health_message  # Message affichant la barre de vie

    def choose_random_button(self):
        """Choisit aléatoirement quel bouton sera gagnant (1 chance sur 4)."""
        self.correct_button = random.choice([1, 2, 3, 4])

    def gif(self):
        """Lien du GIF."""
        return "[GIF](https://tenor.com/view/resident-evil-4-lasers-laser-grid-laser-hallway-laser-gif-5511927577551637319)"

    def update_health_bar(self):
        """Met à jour la barre de vie visuellement."""
        health_bar = "💖" * (self.health // 10) + "🖤" * (10 - (self.health // 10))
        return f"**Vie : {health_bar} ({self.health}%)**"

    async def update_health_message(self):
        """Met à jour le message affichant la barre de vie."""
        await self.health_message.edit(content=self.update_health_bar())

    async def handle_button_click(self, interaction: discord.Interaction, button_number: int):
        """Gère l'interaction des boutons et applique les conséquences."""
        if self.correct_button == button_number:
            self.wins += 1
            if self.wins >= 3:
                await interaction.response.send_message(f"{interaction.user.mention} 🎉 Vous avez esquivé tous les [lasers](https://tenor.com/view/lasers-happy-dance-break-in-deadbeat-gif-15408559) !", ephemeral=False)
                self.stop()
            else:
                await interaction.response.send_message(f"{interaction.user.mention} ✅ Vous avez esquivé un laser !", ephemeral=True)
        else:
            damage = random.randint(5, 25)  # Dégâts aléatoires
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                await interaction.response.send_message(f"{interaction.user.mention} ⚰️ Vous êtes [mort](https://tenor.com/view/coffin-dance-gif-21318528) !", ephemeral=False)
                self.stop()
            else:
                await interaction.response.send_message(f"{interaction.user.mention} ❌ Vous avez perdu **{damage}** points de vie !", ephemeral=True)

        await self.update_health_message()  # Met à jour la barre de vie affichée
        self.choose_random_button()

    @discord.ui.button(label="", style=discord.ButtonStyle.blurple, emoji="<:Symbol_Left_Arrow:1345159488109285477>")
    async def button_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, 1)

    @discord.ui.button(label="", style=discord.ButtonStyle.blurple, emoji="<:Symbol_Up_Arrow:1345422014672011265>")
    async def button_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, 2)

    @discord.ui.button(label="", style=discord.ButtonStyle.blurple, emoji="<:Symbol_Down_Arrow1:1345421982459756665>")
    async def button_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, 3)

    @discord.ui.button(label="", style=discord.ButtonStyle.blurple, emoji="<:Symbol_Right_Arrow:1345159464407535726>")
    async def button_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_button_click(interaction, 4)

@bot.command()
async def start2(ctx):
    """Démarre le jeu et affiche la barre de vie au-dessus de l'embed."""
    await ctx.message.delete()

    # Envoi initial de la barre de vie
    health_message = await ctx.send("Chargement de la barre de vie...")

    embed = discord.Embed(
        title="🔴 Esquive les lasers !",
        description="Choisis par où passer. ⚠️ Un mauvais choix peut être fatal (Objectif esquiver 3 fois.",
        color=discord.Color.red()
    )

    message = await ctx.send(embed=embed)

    game = LuckGame(health_message)  # Associer le message de vie au jeu
    await game.update_health_message()  # Met à jour la barre de vie dès le début

    # Envoi de l'animation et des boutons de jeu
    await message.channel.send(content=game.gif(), view=game)

class CorruptionGame(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.questions = [
            {
                "question": "Quel est le nom du directeur du casino ?",
                "choices": ["Jean Dupont", "Luc Besson", "Marc Bernier", "Pierre Dufresne"],
                "correct": 0  # "Jean Dupont" est la bonne réponse (index 0)
            },
            {
                "question": "Quel est le mot de passe de la salle des coffres ?",
                "choices": ["1234", "casino42", "open sesame", "password123"],
                "correct": 1  # "casino42" est la bonne réponse (index 1)
            },
            {
                "question": "Quel est le nom du responsable de la sécurité ?",
                "choices": ["Franck Morgan", "Emma Roy", "Sarah Dupuis", "Thomas Leclerc"],
                "correct": 2  # "Sarah Dupuis" est la bonne réponse (index 2)
            },
            {
                "question": "Quelle est la couleur de la porte secrète dans le casino ?",
                "choices": ["Rouge", "Bleu", "Vert", "Jaune"],
                "correct": 0  # "Rouge" est la bonne réponse (index 0)
            },
            {
                "question": "Qui est le meilleur ami du directeur du casino ?",
                "choices": ["Alfred", "Louis", "Bernard", "Paul"],
                "correct": 3  # "Paul" est la bonne réponse (index 3)
            }
        ]
        self.current_question = 0
        self.user_score = 0

    async def ask_question(self, interaction: discord.Interaction):
        question_data = self.questions[self.current_question]
        question = question_data["question"]
        choices = question_data["choices"]

        # URL de l'image à ajouter pour la question
        image_url = "https://example.com/your_question_image.png"

        embed = discord.Embed(
            title="💼 Corruption de l'Employé du Casino 🕴️",
            description=f"Question {self.current_question + 1} :\n\n{question}\n\n" + "\n".join([f"{i+1}. {choice}" for i, choice in enumerate(choices)]),
            color=discord.Color.blue()
        )
        embed.set_image(url=image_url)  # Ajouter l'image
        embed.set_footer(text="Choisissez la bonne réponse !")

        # Envoie le message dans le même canal où l'interaction a eu lieu
        await interaction.channel.send(embed=embed, view=self)

    @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
    async def button_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 0)

    @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
    async def button_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 1)

    @discord.ui.button(label="3", style=discord.ButtonStyle.primary)
    async def button_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 2)

    @discord.ui.button(label="4", style=discord.ButtonStyle.primary)
    async def button_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 3)

    async def check_answer(self, interaction: discord.Interaction, selected_option: int):
        question_data = self.questions[self.current_question]

        # Vérification de la réponse
        if selected_option == question_data["correct"]:
            self.user_score += 1
            message = "✅ Bonne réponse ! Vous gagnez un point et vous gagnez peu à peu la confiance de l'employé."
            embed_color = discord.Color.green()
            image_url = "https://example.com/success_image.png"  # Image pour la bonne réponse
        else:
            message = "❌ Mauvaise réponse... Pas grave, passons à la suite !"
            embed_color = discord.Color.red()
            image_url = "https://example.com/fail_image.png"  # Image pour la mauvaise réponse

        self.current_question += 1

        # Envoie un message avec l'état de la réponse
        embed = discord.Embed(
            title="Résultat de la question",
            description=message,
            color=embed_color
        )
        embed.set_image(url=image_url)  # Ajouter l'image
        embed.set_footer(text="L'épreuve continue !")

        await interaction.channel.send(embed=embed)

        # Si l'utilisateur a répondu à toutes les questions
        if self.current_question >= len(self.questions):
            if self.user_score == len(self.questions):
                message = "🎉 Félicitations ! Vous avez réussi à corrompre l'employé du casino ! 🎉"
                embed_color = discord.Color.green()
                image_url = "https://example.com/victory_image.png"  # Image de victoire
            else:
                message = "😞 Désolé, vous n'avez pas réussi à corrompre l'employé du casino. L'occasion est perdue."
                embed_color = discord.Color.red()
                image_url = "https://example.com/defeat_image.png"  # Image de défaite

            # Envoie l'embed final pour tous les membres
            embed = discord.Embed(
                title="Résultat du Braquage : Corruption Échouée ou Réussie",
                description=message,
                color=embed_color
            )
            embed.set_image(url=image_url)  # Ajouter l'image
            embed.set_footer(text="Merci d'avoir participé à l'épreuve.")
            await interaction.channel.send(embed=embed)

            self.stop()  # Arrêter l'épreuve
            return

        # Envoyer la prochaine question sans afficher "échec"
        await self.ask_question(interaction)

@bot.command()
async def start3(ctx):
    await ctx.message.delete()

    # URL de l'image à ajouter pour le début du jeu
    image_url = "https://example.com/start_image.png"

    embed = discord.Embed(
        title="💼 Corruption de l'Employé du Casino 🕴️",
        description="Bienvenue dans l'épreuve de corruption ! Vous devez répondre correctement à des questions pour corrompre un employé du casino et obtenir des informations cruciales pour le braquage.",
        color=discord.Color.blue()
    )
    embed.set_image(url=image_url)  # Ajouter l'image
    embed.set_footer(text="Répondez vite, le temps presse !")

    game = CorruptionGame()
    await ctx.send(embed=embed)  # Utiliser ctx.send pour démarrer l'épreuve
    await game.ask_question(ctx)  # Utiliser ctx pour envoyer la première question


class TruckTheftGame(discord.ui.View):
    def __init__(self, challenge=1):
        super().__init__(timeout=180)  
        self.challenge = challenge  
        self.police_called = False
        self.game_over = False
        self.update_buttons()

    def update_buttons(self):
        """ Met à jour les boutons selon l'épreuve actuelle """
        self.clear_items()  
        if self.challenge == 1:  # Briser la vitre
            self.add_item(ToolButton("Marteau", "marteau"))  # Correct
            self.add_item(ToolButton("Tournevis", "tournevis"))
            self.add_item(ToolButton("Caillou", "caillou"))
        elif self.challenge == 2:  # Connecter les fils
            self.add_item(ToolButton("Tournevis", "tournevis"))  # Correct
            self.add_item(ToolButton("Pince", "pince"))
            self.add_item(ToolButton("Ciseaux", "ciseaux"))
        elif self.challenge == 3:  # Démarrer et fuir
            self.add_item(ToolButton("Clé de contact", "cle_contact"))  # Correct
            self.add_item(ToolButton("Carte magnétique", "carte_magnetique"))
            self.add_item(ToolButton("Câble USB", "cable_usb"))

class ToolButton(discord.ui.Button):
    def __init__(self, label, tool):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.tool = tool

    async def callback(self, interaction: discord.Interaction):
        view = self.view  

        if view.game_over:
            return await interaction.response.send_message("Le jeu est terminé !", ephemeral=True)

        if view.police_called:
            return await interaction.response.send_message("La police est déjà sur place ! Vous avez échoué.", ephemeral=True)

        # Épreuve 1 : Briser la vitre
        if view.challenge == 1:
            if self.tool in ["tournevis", "caillou"]:
                view.police_called = True
                view.game_over = True
                embed = discord.Embed(
                    title="🚨 Police appelées ! 🛑",
                    description=f"{interaction.user.mention} a utilisé un {self.tool}, mais un témoin a appelé la police. 🚔",
                    color=discord.Color.red(),
                )
                embed.set_image(url="https://cdn.motor1.com/images/mgl/3WAl7R/s3/unplugged-performance-upfit-tesla-model-y-police-vehicle-exterior-front-three-quarter-view.jpg")  # Image de la police
                await interaction.response.send_message(embed=embed)
            else:  
                success_embed = discord.Embed(
                    title="✅ Épreuve réussie !",
                    description=f"{interaction.user.mention} a cassé la vitre et peut entrer dans le camion.",
                    color=discord.Color.green(),
                )
                success_embed.set_image(url="https://cdn.prod.website-files.com/6413856d54d41b5f298d5953/67a48bdc0e89f1802ccff330_645a4a8c6e2c9ef89dbc922e_vitre-voiture-explosee.jpeg")  # Image de la vitre cassée
                next_embed = discord.Embed(
                    title="🛠️ Épreuve suivante : Bidouiller les fils",
                    description="Utilisez le bon outil pour connecter les fils et activer le moteur.",
                    color=discord.Color.blue(),
                )
                next_embed.set_image(url="https://cdn.gamma.app/m6u5udkwwfl3cxy/generated-images/xSwg2kTjrOkw_-TeAl_XW.jpg")  # Image des fils à connecter
                view.challenge = 2
                view.update_buttons()
                await interaction.response.send_message(embed=success_embed)
                await interaction.followup.send(embed=next_embed, view=view)

        # Épreuve 2 : Connecter les fils
        elif view.challenge == 2:
            if self.tool == "tournevis":
                success_embed = discord.Embed(
                    title="✅ Épreuve réussie !",
                    description=f"{interaction.user.mention} a connecté les fils, le moteur est prêt !",
                    color=discord.Color.green(),
                )
                success_embed.set_image(url="https://cdn.gamma.app/m6u5udkwwfl3cxy/generated-images/Kmeu9uf3ybXqVeU88rDSR.jpg")  # Image des fils connectés
                next_embed = discord.Embed(
                    title="🚚 Épreuve finale : Démarrer et fuir",
                    description="Trouvez le bon outil pour démarrer le camion et fuyez avant l’arrivée de la police !",
                    color=discord.Color.blue(),
                )
                next_embed.set_image(url="https://cdn.gamma.app/m6u5udkwwfl3cxy/generated-images/mlsYQ3-sCMCxrKMs46c5O.jpg")  # Image du camion
                view.challenge = 3
                view.update_buttons()
                await interaction.response.send_message(embed=success_embed)
                await interaction.followup.send(embed=next_embed, view=view)
            else:
                view.police_called = True
                view.game_over = True
                embed = discord.Embed(
                    title="🚨 Mauvais outil !",
                    description=f"{interaction.user.mention} a utilisé {self.tool}, mais cela a déclenché une alarme ! 🚔",
                    color=discord.Color.red(),
                )
                embed.set_image(url="https://example.com/image_alarme.jpg")  # Image de l'alarme
                await interaction.response.send_message(embed=embed)

        # Épreuve 3 : Démarrer et fuir
        elif view.challenge == 3:
            if self.tool == "cle_contact":
                success = random.choice([True, False])
                if success:
                    embed = discord.Embed(
                        title="🏆 Victoire !",
                        description=f"{interaction.user.mention} a démarré le camion et s’échappe !",
                        color=discord.Color.green(),
                    )
                    embed.set_image(url="https://cdn.gamma.app/m6u5udkwwfl3cxy/generated-images/6rnr8DEFvcLz7GYQi_WeL.jpg")  # Image de victoire
                else:
                    embed = discord.Embed(
                        title="🚨 Démarrage échoué ! 🚨",
                        description=f"{interaction.user.mention} n'a pas réussi à démarrer à temps. La police arrive !",
                        color=discord.Color.red(),
                    )
                    embed.set_image(url="https://cdn.gamma.app/m6u5udkwwfl3cxy/generated-images/uePhica-bN8bEsNJfpAre.jpg")  # Image d'échec
                    view.game_over = True
                await interaction.response.send_message(embed=embed, view=None)
            else:
                view.police_called = True
                view.game_over = True
                embed = discord.Embed(
                    title="🚔 Mauvais outil !",
                    description=f"{interaction.user.mention} a tenté avec un(e) {self.tool}, mais cela ne fonctionne pas... 🚨",
                    color=discord.Color.red(),
                )
                embed.set_image(url="https://cdn.gamma.app/m6u5udkwwfl3cxy/generated-images/xiR6IoHh7KD9b24CAc0B_.jpg")  # Image du mauvais outil
                await interaction.response.send_message(embed=embed)
                
@bot.command()
async def start4(ctx):
    """Commande pour lancer l'épreuve du vol de camion"""
    embed = discord.Embed(
        title="🚚 Tentative de Vol de Camion 🏃‍♂️",
        description="Après le braquage, vous devez fuir en volant un camion. Trouvez le bon outil pour entrer et démarrez le moteur avant que la police n'arrive !",
        color=discord.Color.blue(),
    )
    embed.set_image(url="https://cdn.gamma.app/m6u5udkwwfl3cxy/generated-images/yEC-Ojkt0gIfFz-vucAWg.jpg")  # Image d'introduction
    await ctx.send(embed=embed, view=TruckTheftGame())

class MaterialRetrieval(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)  # Temps limite
        
        self.add_item(MaterialButton("🔦 Infiltrer l'entrepôt", "entrepot"))
        self.add_item(MaterialButton("💰 Acheter au marché noir", "acheter"))
        self.add_item(MaterialButton("🔪 Voler le vendeur", "voler"))

    async def on_timeout(self):
        """Désactive tous les boutons après que le temps soit écoulé"""
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

class MaterialButton(discord.ui.Button):
    def __init__(self, label, action):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        outcome = random.choice(["succès", "échec"])
        
        # Désactive tous les boutons après un clic
        for item in self.view.children:
            item.disabled = True
        
        if self.action == "entrepot":
            if outcome == "succès":
                embed = discord.Embed(
                    title="✅ Infiltration réussie !",
                    description=f"{interaction.user.mention} a réussi à pénétrer dans l'entrepôt et a volé du matériel sans se faire repérer !",
                    color=discord.Color.green()
                )
                embed.set_image(url="https://example.com/image_entrepot.jpg")
                await interaction.response.send_message(embed=embed, ephemeral=False, view=EscapeChallenge())
            else:
                embed = discord.Embed(
                    title="🚨 Alarme déclenchée !",
                    description=f"{interaction.user.mention} a été repéré ! Il doit fuir immédiatement !",
                    color=discord.Color.red()
                )
                embed.set_image(url="https://example.com/image_alarme.jpg")
                await interaction.response.send_message(embed=embed, ephemeral=False, view=EscapeChallenge())
        
        elif self.action == "acheter":
            embed = discord.Embed(
                title="💰 Achat réussi",
                description=f"{interaction.user.mention} a acheté du matériel en toute sécurité, mais cela lui a coûté quelques Ezryn Coins...",
                color=discord.Color.blue()
            )
            embed.set_image(url="https://example.com/image_marche_noir.jpg")
            await interaction.response.send_message(embed=embed, ephemeral=False)
        
        elif self.action == "voler":
            if outcome == "succès":
                embed = discord.Embed(
                    title="🔪 Vol réussi !",
                    description=f"{interaction.user.mention} a réussi à menacer le vendeur et s'est emparé du matériel !",
                    color=discord.Color.green()
                )
                embed.set_image(url="https://example.com/image_vol_reussi.jpg")
                await interaction.response.send_message(embed=embed, ephemeral=False, view=EscapeChallenge())
            else:
                embed = discord.Embed(
                    title="🚔 Échec !",
                    description=f"{interaction.user.mention} a tenté de voler le vendeur, mais ce dernier a riposté et alerté la police !",
                    color=discord.Color.red()
                )
                embed.set_image(url="https://example.com/image_police.jpg")
                await interaction.response.send_message(embed=embed, ephemeral=False, view=EscapeChallenge())

class EscapeChallenge(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)  # Temps limite
        self.add_item(EscapeButton("🏃 Fuir rapidement", "fuir"))
        self.add_item(EscapeButton("🛑 Se cacher", "cacher"))
        self.add_item(EscapeButton("🤜 Combattre", "combattre"))

class EscapeButton(discord.ui.Button):
    def __init__(self, label, action):
        super().__init__(label=label, style=discord.ButtonStyle.danger)
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        outcome = random.choice(["succès", "échec"])
        
        if outcome == "succès":
            embed = discord.Embed(
                title="✅ Évasion réussie !",
                description=f"{interaction.user.mention} a réussi à s'enfuir !",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="🚔 Capturé !",
                description=f"{interaction.user.mention} a échoué et s'est fait attraper !",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.command()
async def start5(ctx):
    """Commande pour lancer l'épreuve de récupération du matériel"""
    embed = discord.Embed(
        title="🔧 Récupération du Matériel",
        description="Vous avez besoin d'équipement pour finaliser le plan. Choisissez votre méthode : infiltration, achat ou vol !",
        color=discord.Color.orange()
    )
    embed.set_image(url="https://example.com/image_intro_materiel.jpg")
    
    # Vérification du message envoyé avec la vue
    message = await ctx.send(embed=embed, view=MaterialRetrieval())
    print(f"Message envoyé avec vue : {message.content}")  # Ceci va t'aider à vérifier que le message est envoyé correctement.

# 🎛️ Classe pour la première étape (choix du câble)
class CableView(View):
    def __init__(self, correct_cable):
        super().__init__()
        self.correct_cable = correct_cable

        cables = ['🔴 Rouge', '🔵 Bleu', '🟢 Vert', '🟡 Jaune', '🟠 Orange']
        random.shuffle(cables)

        for cable in cables:
            button = Button(label=cable, style=discord.ButtonStyle.green, custom_id=cable)
            button.callback = self.create_callback(cable)
            self.add_item(button)

    def create_callback(self, cable):
        async def callback(interaction: discord.Interaction):
            if cable == self.correct_cable:
                embed = discord.Embed(
                    title="✅ Câble coupé avec succès !",
                    description=f"🎉 **Bravo {interaction.user.mention} !**\n\n"
                                f"Tu as coupé le bon câble **{cable}** et la sécurité a été désactivée.",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url="https://example.com/success.png")  # Remplace avec une vraie URL
                await interaction.response.send_message(embed=embed)
                await step_2(interaction)
            else:
                embed = discord.Embed(
                    title="🚨 Mauvais câble !",
                    description=f"❌ **Oups {interaction.user.mention} !**\n\n"
                                f"Tu as coupé **{cable}**, mais cela a déclenché l'alarme ! 🚨",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url="https://example.com/fail.png")  # Remplace avec une vraie URL
                await interaction.response.send_message(embed=embed)
        return callback


# 🛠 Étape 1 : Sélectionner le bon câble
async def step_1(ctx):
    correct_cable = random.choice(['🔴 Rouge', '🔵 Bleu', '🟢 Vert', '🟡 Jaune', '🟠 Orange'])

    embed = discord.Embed(
        title="🔧 Étape 1: Sabotage de la Sécurité",
        description="🎯 **Mission :** Couper le bon câble pour désactiver la sécurité.\n\n"
                    "⚠️ Faites attention ! Si vous vous trompez, l'alarme se déclenchera !",
        color=discord.Color.red()
    )
    embed.set_image(url="https://example.com/cables_image.png")  # Remplace par une vraie URL

    view = CableView(correct_cable)
    await ctx.send(embed=embed, view=view)


# 🔑 Classe pour la deuxième étape (choix de l'action)
class ActionView(View):
    def __init__(self):
        super().__init__()

        actions = ['🔨 Forcer la porte', '🔢 Utiliser un code de sécurité', '📞 Contacter un allié']
        random.shuffle(actions)

        for action in actions:
            button = Button(label=action, style=discord.ButtonStyle.blurple, custom_id=action)
            button.callback = self.create_callback(action)
            self.add_item(button)

    def create_callback(self, action):
        async def callback(interaction: discord.Interaction):
            if action == '🔢 Utiliser un code de sécurité':
                embed = discord.Embed(
                    title="✅ Action réussie !",
                    description=f"🔐 **Bravo {interaction.user.mention} !**\n\n"
                                "Tu as utilisé le code de sécurité avec succès et la porte s'ouvre ! 🚪",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url="https://example.com/success.png")  # Remplace avec une vraie URL
                await interaction.response.send_message(embed=embed)
                await interaction.followup.send(embed=discord.Embed(
                    title="🎯 Mission réussie !",
                    description="✅ **Tu as terminé l'épreuve avec succès !** 🎉",
                    color=discord.Color.gold()
                ))
            else:
                embed = discord.Embed(
                    title="❌ Mauvaise action...",
                    description=f"⚠️ **{interaction.user.mention}, mauvaise décision !**\n\n"
                                "Tu as choisi **{action}**, mais cela t'a ralenti dans l'épreuve...",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url="https://example.com/fail.png")  # Remplace avec une vraie URL
                await interaction.response.send_message(embed=embed)
                await interaction.followup.send(embed=discord.Embed(
                    title="🔚 Fin de l'épreuve",
                    description="❌ **Tu as échoué. La mission est terminée.**",
                    color=discord.Color.dark_gray()
                ))
        return callback

# 🏆 Étape 2 : Sélectionner une action
async def step_2(interaction):
    embed = discord.Embed(
        title="🔑 Étape 2: Sélectionner une action",
        description="🤔 **Choisissez la meilleure action pour continuer l'épreuve.**",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url="https://example.com/action_choice.png")  # Remplace avec une vraie URL

    view = ActionView()
    await interaction.followup.send(embed=embed, view=view)


# 🚀 Commande pour démarrer l'épreuve
@bot.command()
async def start6(ctx):
    await step_1(ctx)

class DiversionGame(discord.ui.View):
    def __init__(self, scenario_choices):
        super().__init__(timeout=180)  # Le jeu dure 3 minutes
        self.scenario_choices = scenario_choices
        self.game_over = False
        self.update_buttons()

    def update_buttons(self):
        """Met à jour les boutons selon les scénarios disponibles"""
        self.clear_items()  # Supprime les boutons existants
        for scenario, success_chance in self.scenario_choices.items():
            self.add_item(DiversionButton(scenario, success_chance))

class DiversionButton(discord.ui.Button):
    def __init__(self, scenario, success_chance):
        super().__init__(label=scenario, style=discord.ButtonStyle.primary)
        self.scenario = scenario
        self.success_chance = success_chance

    async def callback(self, interaction: discord.Interaction):
        if self.view.game_over:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Jeu Terminé",
                    description="Le jeu est déjà terminé, veuillez attendre la prochaine manche.",
                    color=discord.Color.orange()
                ), ephemeral=True
            )
        
        roll = random.randint(1, 100)
        success = roll <= self.success_chance

        # Création de l'embed pour afficher le résultat
        result_embed = discord.Embed(
            title="Résultat de la Diversion",
            description="\n✅ La diversion a réussi !" if success else "\n❌ La diversion a échoué... Les autorités ont réagi trop vite.",
            color=discord.Color.green() if success else discord.Color.red()
        )
        result_embed.add_field(name="🎭 Scénario Choisi", value=self.scenario, inline=False)
        result_embed.add_field(name="🎲 Chance de Réussite", value=f"{self.success_chance}%", inline=True)
        result_embed.add_field(name="🎯 Résultat du Lancer", value=f"{roll}% - {'Succès' if success else 'Échec'}", inline=True)
        result_embed.set_footer(text="Une diversion bien menée peut tout changer...")

        self.view.game_over = True
        await interaction.response.edit_message(embed=result_embed, view=None)

@bot.command()
async def start7(ctx):
    """Commande pour lancer l'épreuve de diversion"""
    embed = discord.Embed(
        title="🎭 Choix de la Diversion",
        description="Sélectionnez une stratégie pour détourner l'attention et faciliter le braquage !\n\n**Les scénarios possibles :**",
        color=discord.Color.blurple()
    )
    embed.add_field(name="🚗 Accident de voiture sur l'autoroute", value="La circulation est complètement bloquée ! 🚧", inline=False)
    embed.add_field(name="🔫 Vol à main armée dans un autre quartier", value="Toutes les unités sont envoyées sur place ! 🚔", inline=False)
    embed.add_field(name="🔥 Incendie dans un entrepôt abandonné", value="Les pompiers et la police sont mobilisés ! 🚒", inline=False)
    embed.add_field(name="💣 Fausse alerte à la bombe", value="Le quartier est évacué et sécurisé ! 🚨", inline=False)
    embed.add_field(name="✊ Manifestation contre la police", value="Les forces de l'ordre sont débordées par la foule ! 📢", inline=False)
    embed.set_footer(text="Sélectionnez un scénario ci-dessous pour commencer.")
    
    diversion_scenarios = {
        "🚗 Accident de voiture sur l'autoroute": 70,
        "🔫 Vol à main armée dans un autre quartier": 60,
        "🔥 Incendie dans un entrepôt abandonné": 50,
        "💣 Fausse alerte à la bombe": 40,
        "✊ Manifestation contre la police": 30
    }

    view = DiversionGame(diversion_scenarios)
    await ctx.send(embed=embed, view=view)

class CasinoHeist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guard_hp = 20  # PV des gardes
        self.player_hp = {}  # PV des joueurs

    @commands.command()
    async def start8(self, ctx):
        """Lance l'épreuve de neutralisation de la sécurité."""
        player = ctx.author.id
        self.player_hp[player] = 20

        await ctx.send(f"🔫 **Épreuve : Neutraliser la sécurité** 🔫\nDes gardes vous repèrent ! Choisissez votre action :\n`attaquer` ⚔ | `esquiver` 🏃 | `assommer` 💤")

        def check(m):
            return m.author.id == player and m.content.lower() in ["attaquer", "esquiver", "assommer"]

        while self.guard_hp > 0 and self.player_hp[player] > 0:
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=20)
                action = msg.content.lower()
                result = self.resolve_action(action, player)
                await ctx.send(result)
            except Exception:
                await ctx.send("⏳ Vous avez mis trop de temps à répondre ! Les gardes vous maîtrisent ! ❌")
                self.player_hp[player] = 0
                break

        if self.guard_hp <= 0:
            await ctx.send("✅ **Les gardes sont neutralisés ! Vous pouvez avancer.**")
        elif self.player_hp[player] <= 0:
            await ctx.send("❌ **Vous avez été mis hors d'état de nuire... Mission échouée !**")

    def resolve_action(self, action, player):
        """Gère les actions du joueur et la réponse des gardes."""
        if action == "attaquer":
            damage = random.randint(5, 10)
            self.guard_hp -= damage
            return f"⚔ Vous attaquez et infligez {damage} dégâts aux gardes ! (Garde : {self.guard_hp} PV)"
        
        elif action == "esquiver":
            if random.random() < 0.6:
                return "🏃 Vous esquivez avec succès ! Aucun dégât subi."
            else:
                self.player_hp[player] -= 5
                return f"❌ Vous ratez votre esquive et prenez 5 dégâts ! (Vos PV : {self.player_hp[player]})"

        elif action == "assommer":
            if random.random() < 0.4:
                self.guard_hp = 0
                return "💤 Vous assommez un garde avec succès ! Ils sont hors d'état de nuire."
            else:
                self.player_hp[player] -= 7
                return f"❌ Vous tentez d'assommer un garde mais échouez ! Il vous frappe (-7 PV). (Vos PV : {self.player_hp[player]})"

# Ajout du Cog au bot
async def setup(bot):
    await bot.add_cog(CasinoHeist(bot))

# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
