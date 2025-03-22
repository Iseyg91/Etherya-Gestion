import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import random
import asyncio
import time
import datetime
import re
import subprocess
import sys
from keep_alive import keep_alive
from discord.ui import Button, View
from datetime import datetime
from discord.ui import View, Select
from discord.ext import tasks
from collections import defaultdict
from collections import deque
import pymongo
from pymongo import MongoClient
import psutil
import platform

token = os.environ['ETHERYA']
intents = discord.Intents.all()
start_time = time.time()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="+", intents=intents)

# Connexion MongoDB
mongo_uri = os.getenv("MONGO_DB")
print("Mongo URI :", mongo_uri)  # Cela affichera l'URI de connexion (assure-toi de ne pas laisser cela en prod)
client = MongoClient(mongo_uri)
db = client['SetupEtherya']
collection = db['setup']

def load_guild_settings(guild_id):
    setup_data = collection.find_one({"guild_id": guild_id}) or {}
    return setup_data

# Dictionnaire pour stocker les paramètres de chaque serveur
GUILD_SETTINGS = {}

@bot.event
async def on_ready():
    print(f"✅ Le bot est connecté en tant que {bot.user} (ID: {bot.user.id})")

    # Initialiser l'uptime du bot
    bot.uptime = time.time()

    # Liste des activités à alterner
    activity_types = [
        discord.Game("Etherya"),  # Playing
        discord.Activity(type=discord.ActivityType.watching, name=" Le Monde d'Etherya"),  # Watching
        discord.Activity(type=discord.ActivityType.listening, name=" Les Murmures du Passé"),  # Listening
        discord.Activity(type=discord.ActivityType.streaming, name=" Les Sombres Secrets")  # Streaming
    ]

    # Liste des statuts à alterner
    status_types = [
        discord.Status.online,  # En ligne
        discord.Status.idle,    # Inactif
        discord.Status.dnd      # Ne pas déranger
    ]
    
    print(f'{bot.user} est connecté !')

    # Afficher les commandes chargées
    print("📌 Commandes disponibles 😊")
    for command in bot.commands:
        print(f"- {command.name}")

    try:
        # Synchroniser les commandes avec Discord
        synced = await bot.tree.sync()  # Synchronisation des commandes slash
        print(f"✅ Commandes slash synchronisées : {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation des commandes slash : {e}")

    # Jongler entre différentes activités et statuts
    while True:
        for activity in activity_types:
            for status in status_types:
                await bot.change_presence(status=status, activity=activity)
                await asyncio.sleep(10)  # Attente de 10 secondes avant de changer l'activité et le statut
    for guild in bot.guilds:
        GUILD_SETTINGS[guild.id] = load_guild_settings(guild.id)


# Gestion des erreurs globales pour toutes les commandes
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Une erreur s'est produite : {event}")
    embed = discord.Embed(
        title="❗ Erreur inattendue",
        description="Une erreur s'est produite lors de l'exécution de la commande. Veuillez réessayer plus tard.",
        color=discord.Color.red()
    )
    await args[0].response.send_message(embed=embed)

#--------------------------------------------------------------------------- Owner Verif

BOT_OWNER_ID = 792755123587645461

# Vérification si l'utilisateur est l'owner du bot
def is_owner(ctx):
    return ctx.author.id == BOT_OWNER_ID

@bot.command()
async def shutdown(ctx):
    if is_owner(ctx):
        embed = discord.Embed(
            title="Arrêt du Bot",
            description="Le bot va maintenant se fermer. Tous les services seront arrêtés.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Cette action est irréversible.")
        await ctx.send(embed=embed)
        await bot.close()
    else:
        await ctx.send("Seul l'owner peut arrêter le bot.")

@bot.command()
async def restart(ctx):
    if is_owner(ctx):
        embed = discord.Embed(
            title="Redémarrage du Bot",
            description="Le bot va redémarrer maintenant...",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        os.execv(sys.executable, ['python'] + sys.argv)  # Redémarre le bot
    else:
        await ctx.send("Seul l'owner peut redémarrer le bot.")

@bot.command()
async def setstatus(ctx, status: str):
    if is_owner(ctx):
        await bot.change_presence(activity=discord.Game(name=status))
        embed = discord.Embed(
            title="Changement de Statut",
            description=f"Le statut du bot a été changé en : {status}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("Seul l'owner peut changer le statut du bot.")

@bot.command()
async def getbotinfo(ctx):
    # Calcul de l'uptime du bot
    uptime_seconds = time.time() - bot.uptime
    uptime_days = int(uptime_seconds // 86400)
    uptime_hours = int((uptime_seconds % 86400) // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    uptime_seconds = int(uptime_seconds % 60)

    # Récupération des statistiques du bot
    total_servers = len(bot.guilds)
    total_users = sum(g.member_count for g in bot.guilds)
    total_text_channels = sum(len(g.text_channels) for g in bot.guilds)
    total_voice_channels = sum(len(g.voice_channels) for g in bot.guilds)
    latency = round(bot.latency * 1000, 2)  # Latence en ms
    total_commands = len(bot.commands)

    # Création de l'embed
    embed = discord.Embed(
        title="🤖 Informations du Bot",
        description=f"✨ **Nom :** `{bot.user.name}`\n"
                    f"🔹 **ID :** `{bot.user.id}`\n"
                    f"📅 **Créé le :** `{bot.user.created_at.strftime('%d/%m/%Y')}`",
        color=discord.Color.gold(),  # Changement de couleur pour un look premium
        timestamp=datetime.utcnow()
    )
    
    embed.set_thumbnail(url=bot.user.avatar.url)
    if bot.user.banner:  # Vérifie si le bot a une bannière
        embed.set_image(url=bot.user.banner.url)

    embed.set_footer(text=f"Requête faite par {ctx.author}", icon_url=ctx.author.avatar.url)

    # Ajout des stats principales avec formatage des nombres
    embed.add_field(
        name="📊 **Statistiques**",
        value=( 
            f"> **🖥️ Serveurs :** `{total_servers:,}`\n"
            f"> **👥 Utilisateurs :** `{total_users:,}`\n"
            f"> **💬 Textuels :** `{total_text_channels:,}`\n"
            f"> **🔊 Vocaux :** `{total_voice_channels:,}`\n"
            f"> **⌨️ Commandes :** `{total_commands:,}`\n"
            f"> **📡 Latence :** `{latency} ms`\n"
        ),
        inline=False
    )

    # Ajout de l'uptime
    embed.add_field(
        name="⏳ **Uptime**",
        value=f"> `{uptime_days}j {uptime_hours}h {uptime_minutes}m {uptime_seconds}s`",
        inline=False
    )

    # Ajout d'un bouton d'invitation avec ton lien
    view = discord.ui.View()
    invite_button = discord.ui.Button(
        label="📩 Inviter le Bot",
        style=discord.ButtonStyle.link,
        url="https://discord.com/oauth2/authorize?client_id=1346161481988706325&permissions=8&integration_type=0&scope=bot"
    )
    view.add_item(invite_button)

    await ctx.send(embed=embed, view=view)


# Liste d'emojis qui tournent pour éviter la répétition
EMOJIS_SERVEURS = ["🎭", "🌍", "🏰", "🚀", "🔥", "👾", "🏆", "🎮", "🏴‍☠️", "🏕️"]

class ServerInfoView(View):
    def __init__(self, ctx, bot, guilds):
        super().__init__()
        self.ctx = ctx
        self.bot = bot
        self.guilds = sorted(guilds, key=lambda g: g.member_count, reverse=True)  # Tri par popularité
        self.page = 0
        self.servers_per_page = 5
        self.max_page = (len(self.guilds) - 1) // self.servers_per_page
        self.update_buttons()
    
    def update_buttons(self):
        self.children[0].disabled = self.page == 0  # Désactiver "Précédent" si première page
        self.children[1].disabled = self.page == self.max_page  # Désactiver "Suivant" si dernière page

    async def update_embed(self, interaction):
        embed = await self.create_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def create_embed(self):
        total_servers = len(self.guilds)

        embed = discord.Embed(
            title=f"🌍 Serveurs du Bot (`{total_servers}` total)",
            description="🔍 Liste des serveurs où le bot est présent, triés par popularité.",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Page {self.page + 1}/{self.max_page + 1} • Demandé par {self.ctx.author}", icon_url=self.ctx.author.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        start = self.page * self.servers_per_page
        end = start + self.servers_per_page

        for i, guild in enumerate(self.guilds[start:end]):
            emoji = EMOJIS_SERVEURS[i % len(EMOJIS_SERVEURS)]  # Sélectionne un emoji en alternance
            
            invite_url = "🔒 *Aucune invitation disponible*"
            if guild.text_channels:
                invite = await guild.text_channels[0].create_invite(max_uses=1, unique=True)
                invite_url = f"[🔗 Invitation]({invite.url})"

            owner = guild.owner.mention if guild.owner else "❓ *Inconnu*"
            member_display = f"**{guild.member_count}**" if guild.member_count > 1000 else f"{guild.member_count}"
            boost_level = guild.premium_tier if guild.premium_tier > 0 else "0"
            emoji_count = len(guild.emojis)

            embed.add_field(
                name=f"{emoji} **{guild.name}**",
                value=(
                    f"> **👑 Propriétaire** : {owner}\n"
                    f"> **📊 Membres** : `{member_display}`\n"
                    f"> **💎 Boosts** : `Niveau {boost_level}`\n"
                    f"> **🛠️ Rôles** : `{len(guild.roles)}`\n"
                    f"> **💬 Canaux** : `{len(guild.channels)}`\n"
                    f"> **😃 Emojis** : `{emoji_count}`\n"
                    f"> **🆔 ID** : `{guild.id}`\n"
                    f"> **📅 Créé le** : `{guild.created_at.strftime('%d/%m/%Y')}`\n"
                    f"> {invite_url}"
                ),
                inline=False
            )

        embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryaBot_banniere.png?raw=true")
        return embed

    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.green, disabled=True)
    async def previous(self, interaction: discord.Interaction, button: Button):
        self.page -= 1
        await self.update_embed(interaction)

    @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.green)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.page += 1
        await self.update_embed(interaction)

@bot.command()
async def serverinfoall(ctx):
    if is_owner(ctx):
        view = ServerInfoView(ctx, bot, bot.guilds)
        embed = await view.create_embed()
        await ctx.send(embed=embed, view=view)
    else:
        await ctx.send("Seul l'owner peut obtenir ces informations.")
#-------------------------------------------------------------------------- Commandes /premium et /viewpremium
# Dictionnaire pour stocker les serveurs premium
premium_servers = {}

# Code Premium valide
valid_code = "Etherya_Iseyg=91"

# Ajout d'une commande pour afficher le statut du bot
@bot.tree.command(name="statut")
async def statut(interaction: discord.Interaction):
    try:
        # Message d'attente pendant que les données sont récupérées
        await interaction.response.defer(thinking=True)

        # Récupération des informations en parallèle
        latency_task = asyncio.create_task(get_latency())
        premium_task = asyncio.create_task(get_premium_servers_count())
        members_task = asyncio.create_task(get_server_members_count(interaction.guild))
        uptime_task = asyncio.create_task(get_bot_uptime())
        memory_task = asyncio.create_task(get_bot_memory_usage())
        
        # Récupérer les résultats de toutes les tâches
        latency, premium_count, member_count, uptime, memory_usage = await asyncio.gather(
            latency_task, premium_task, members_task, uptime_task, memory_task
        )
        
        # Déterminer la couleur de l'embed en fonction de la latence
        color = discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
        
        # Création de l'embed
        embed = discord.Embed(
            title="🤖 Statut du Bot",
            description="Le bot est actuellement en ligne et opérationnel.",
            color=color
        )
        
        # Ajout des informations dans l'embed
        embed.add_field(name="Version", value="Bot v1.0", inline=True)
        embed.add_field(name="Serveurs Premium", value=f"**{premium_count}** serveurs premium activés.", inline=True)
        embed.add_field(name="Latence", value=f"{latency:.2f} ms", inline=True)
        embed.add_field(name="Membres sur le serveur", value=f"{member_count} membres actifs", inline=True)
        embed.add_field(name="Uptime du Bot", value=uptime, inline=True)
        embed.add_field(name="Utilisation Mémoire", value=f"{memory_usage} MB", inline=True)
        
        # Informations sur l'environnement
        embed.add_field(name="Environnement", value=f"{platform.system()} {platform.release()} - Python {platform.python_version()}", inline=False)
        
        # Footer dynamique
        embed.set_footer(text=f"Bot géré par Etherya | {bot.user.name}")

        # Ajouter le thumbnail du bot
        embed.set_thumbnail(url=bot.user.avatar.url)

        # Envoi du message avec l'embed
        await interaction.followup.send(embed=embed)

    except Exception as e:
        # Gestion d'erreur plus détaillée
        await interaction.followup.send(
            f"Une erreur est survenue lors de la récupération du statut du bot : {str(e)}"
        )


# Fonction pour récupérer la latence du bot
async def get_latency():
    return bot.latency * 1000  # Retourne la latence en millisecondes


# Fonction pour récupérer le nombre de serveurs premium
async def get_premium_servers_count():
    return len(premium_servers)


# Fonction pour récupérer le nombre de membres sur le serveur
async def get_server_members_count(guild):
    return len(guild.members)


# Fonction pour récupérer l'uptime du bot
async def get_bot_uptime():
    uptime_seconds = int((discord.utils.utcnow() - bot.user.created_at).total_seconds())
    uptime = str(datetime.timedelta(seconds=uptime_seconds))
    return uptime


# Fonction pour récupérer l'utilisation de la mémoire du bot
async def get_bot_memory_usage():
    # Utilisation de psutil pour obtenir l'utilisation mémoire du processus Python
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_usage_mb = memory_info.rss / (1024 * 1024)  # Convertir en Mo
    return round(memory_usage_mb, 2)

# Commande slash /premium
@bot.tree.command(name="premium")
@app_commands.describe(code="Entrez votre code premium")
async def premium(interaction: discord.Interaction, code: str):
    await interaction.response.defer(thinking=True)  # Message d'attente pendant le traitement

    try:
        # Vérification si le code est valide
        if code == valid_code:
            # Vérification si le serveur est déjà premium
            if interaction.guild.id in premium_servers:
                embed = discord.Embed(
                    title="⚠️ Serveur déjà Premium",
                    description=f"Le serveur **{interaction.guild.name}** est déjà un serveur premium. 🎉",
                    color=discord.Color.yellow()
                )
                embed.add_field(
                    name="Pas de double activation",
                    value="Ce serveur a déjà activé le code premium. Aucun changement nécessaire.",
                    inline=False
                )
                embed.set_footer(text="Merci d'utiliser nos services premium.")
                embed.set_thumbnail(url=interaction.guild.icon.url)  # Icône du serveur
                await interaction.followup.send(embed=embed)
            else:
                # Enregistrement du serveur comme premium
                premium_servers[interaction.guild.id] = interaction.guild.name
                embed = discord.Embed(
                    title="✅ Serveur Premium Activé",
                    description=f"Le serveur **{interaction.guild.name}** est maintenant premium ! 🎉",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Avantages Premium",
                    value="Profitez des fonctionnalités exclusives réservées aux serveurs premium. 🎁",
                    inline=False
                )
                embed.set_footer(text="Merci d'utiliser nos services premium.")
                embed.set_thumbnail(url=interaction.guild.icon.url)  # Icône du serveur
                await interaction.followup.send(embed=embed)

        else:
            # Code invalide, avec des suggestions supplémentaires
            embed = discord.Embed(
                title="❌ Code Invalide",
                description="Le code que vous avez entré est invalide. Veuillez vérifier votre code ou contactez le support.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Suggestions",
                value="1. Assurez-vous d'avoir saisi le code exactement comme il est fourni.\n"
                      "2. Le code est sensible à la casse.\n"
                      "3. Si vous avez des doutes, contactez le support.",
                inline=False
            )
            embed.add_field(
                name="Code Expiré ?",
                value="Si vous pensez que votre code devrait être valide mais ne l'est pas, il est possible qu'il ait expiré. "
                      "Dans ce cas, veuillez contacter notre équipe de support.",
                inline=False
            )
            await interaction.followup.send(embed=embed)
    
    except Exception as e:
        # Gestion des erreurs
        await interaction.followup.send(
            f"Une erreur est survenue lors de la vérification du code premium : {str(e)}"
        )


# Commande slash /viewpremium
@bot.tree.command(name="viewpremium")
async def viewpremium(interaction: discord.Interaction):
    if not premium_servers:
        # Embed pour indiquer qu'il n'y a aucun serveur premium
        embed = discord.Embed(
            title="🔒 Aucun Serveur Premium",
            description="Aucun serveur premium n'a été activé sur ce bot.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Pourquoi devenir premium ?",
            value="Devenez premium pour profiter de fonctionnalités exclusives et de plus de personnalisation pour votre serveur !\n\n"
                  "👉 **Contactez-nous** pour en savoir plus sur les avantages et les fonctionnalités offertes.",
            inline=False
        )
        embed.set_footer(text="Rejoignez notre programme premium.")
        
        # Ajout d'un bouton pour rejoindre le programme premium
        join_button = Button(label="Rejoindre Premium", style=discord.ButtonStyle.green, url="https://votre-lien-premium.com")

        view = View()
        view.add_item(join_button)

        await interaction.response.send_message(embed=embed, view=view)
    else:
        # Si des serveurs premium existent, afficher la liste
        premium_list = "\n".join([f"**{server_name}**" for server_name in premium_servers.values()])
        
        # Si la liste est courte, tout afficher d'un coup
        embed = discord.Embed(
            title="🌟 Liste des Serveurs Premium",
            description=f"Les serveurs premium activés sont :\n{premium_list}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Merci pour votre soutien !")
        await interaction.response.send_message(embed=embed)

#------------------------------------------------------------------------- Commande SETUP

@bot.tree.command(name="setup", description="Configure les rôles et salons du bot.")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    GUILD_SETTINGS[guild_id] = load_guild_settings(guild_id)
    
    settings = GUILD_SETTINGS[guild_id]
    SROLE_ADMIN = settings.get("admin_role")
    SROLE_STAFF = settings.get("staff_role")
    SOWNER_ID = settings.get("owner")
    SCHANNEL_SANCTIONS = settings.get("sanctions_channel")
    SCHANNEL_REPORTS = settings.get("reports_channel")
    
    embed = discord.Embed(title="Configuration du bot", description="Sélectionnez les rôles et salons.", color=discord.Color.blue())
    embed.add_field(name="Administrateur", value=f"<@&{SROLE_ADMIN}>" if SROLE_ADMIN else "Aucun défini", inline=False)
    embed.add_field(name="Staff", value=f"<@&{SROLE_STAFF}>" if SROLE_STAFF else "Aucun défini", inline=False)
    embed.add_field(name="Owner du serveur", value=f"<@{SOWNER_ID}>" if SOWNER_ID else "Aucun défini", inline=False)
    embed.add_field(name="Salon Sanctions", value=f"<#{SCHANNEL_SANCTIONS}>" if SCHANNEL_SANCTIONS else "Aucun défini", inline=False)
    embed.add_field(name="Salon Signalement", value=f"<#{SCHANNEL_REPORTS}>" if SCHANNEL_REPORTS else "Aucun défini", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
#------------------------------------------------------------------------- Commande Mention ainsi que Commandes d'Administration : Detections de Mots sensible et Mention

# Liste des mots sensibles
sensitive_words = [
    # Insultes et injures
    "connard", "crétin", "idiot", "imbécile", "salopard", "enfoiré", "méchant", "abruti", "débile", "bouffon",
    "clown", "baltringue", "fils de pute", "gros con", "sale type", "ordure", "merdeux", "guignol", "vaurien",
    "tocard", "branleur", "crasseux", "charognard", "raté", "bâtard", "déchet", "parasite",
    
    # Discrimination et discours haineux
    "raciste", "sexiste", "homophobe", "antisémite", "xénophobe", "transphobe", "islamophobe", "misogyne", 
    "misandre", "discriminatoire", "suprémaciste", "extrémiste", "fasciste", "nazi", "néonazi", "dictateur",

    # Violence et criminalité
    "viol", "tuer", "assassin", "attaque", "agression", "meurtre", "génocide", "exécution", "kidnapping",
    "prise d'otage", "armes", "fusillade", "terrorisme", "attentat", "jihad", "bombardement", "suicidaire",
    "décapitation", "immolation", "torture", "lynchage", "massacre", "pillage", "extermination",
    
    # Crimes sexuels et exploitation
    "pédocriminel", "abus", "sexe", "pornographie", "nu", "masturbation", "prostitution", "pédophilie", 
    "inceste", "exhibition", "fétichisme", "harcèlement", "traite humaine", "esclavage sexuel", "viol collectif",

    # Drogues et substances illicites
    "drogue", "cocaïne", "héroïne", "crack", "LSD", "ecstasy", "méthamphétamine", "opium", "cannabis", "alcool", 
    "ivresse", "overdose", "trafic de drogue", "toxicomanie", "drogue de synthèse", "GHB", "fentanyl",

    # Cybercriminalité et piratage
    "hack", "pirater", "voler des données", "phishing", "ddos", "raid", "flood", "spam", "crasher", "exploiter",
    "ransomware", "trojan", "virus informatique", "keylogger", "backdoor", "brute force", "scam", 
    "usurpation d'identité", "darknet", "marché noir", "cheval de Troie", "spyware", "hameçonnage",

    # Fraude et corruption
    "fraude", "extorsion", "chantage", "blanchiment d'argent", "corruption", "pot-de-vin", "abus de pouvoir", 
    "détournement de fonds", "évasion fiscale", "fraude fiscale", "marché noir", "contrefaçon",

    # Manipulation et désinformation
    "dictature", "oppression", "propagande", "fake news", "manipulation", "endoctrinement", "secte", 
    "lavage de cerveau", "désinformation",

    # Groupes criminels et troubles sociaux
    "violence policière", "brutalité", "crime organisé", "mafia", "cartel", "milice", "mercenaire", "guérilla",
    "insurrection", "émeute", "rébellion", "coup d'état", "anarchie", "terroriste", "séparatiste"
]

ADMIN_ID = 792755123587645461  # Remplace avec l'ID de ton Owner

# IDs des utilisateurs qui font le bump
bump_ids = [302050872383242240, 528557940811104258]

# Dictionnaire pour suivre les rappels
bump_reminders = {}

def get_main_guild():
    return bot.guilds[0] if bot.guilds else None

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignorer les bots

    member = message.guild.get_member(message.author.id)

    # Détection des mots sensibles
    for word in sensitive_words:
        if re.search(rf"\b{re.escape(word)}\b", message.content, re.IGNORECASE):
            print(f"🚨 Mot sensible détecté dans le message de {message.author}: {word}")
            asyncio.create_task(send_alert_to_admin(message, word))
            break  # On arrête la boucle dès qu'on trouve un mot interdit

    # Réponse automatique aux mentions du bot
    if bot.user.mentioned_in(message) and message.content.strip().startswith(f"<@{bot.user.id}>"):
        embed = discord.Embed(
            title="👋 Besoin d’aide ?",
            description=(f"Salut {message.author.mention} ! Moi, c’est **{bot.user.name}**, ton assistant sur ce serveur. 🤖\n\n"
                         "🔹 **Pour voir toutes mes commandes :** Appuie sur le bouton ci-dessous ou tape `+aide`\n"
                         "🔹 **Une question ? Un souci ?** Contacte le staff !\n\n"
                         "✨ **Profite bien du serveur et amuse-toi !**"),
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(text="Réponse automatique • Disponible 24/7", icon_url=bot.user.avatar.url)
        
        view = View()
        button = Button(label="📜 Voir les commandes", style=discord.ButtonStyle.primary, custom_id="help_button")

        async def button_callback(interaction: discord.Interaction):
            ctx = await bot.get_context(interaction.message)
            await ctx.invoke(bot.get_command("aide"))
            await interaction.response.send_message("Voici la liste des commandes !", ephemeral=True)

        button.callback = button_callback
        view.add_item(button)

        await message.channel.send(embed=embed, view=view)

    # Vérifie si la commande /bump a été utilisée
    if message.content.startswith("/bump") and message.author.id in bump_ids:
        # Envoie un message de remerciement
        await message.channel.send(f"Merci {message.author.mention} pour ton bump !")

        # Enregistre un rappel pour 2 heures plus tard
        if message.author.id not in bump_reminders:
            bump_reminders[message.author.id] = {}

        # Fonction pour rappeler dans 2 heures
        await asyncio.sleep(7200)  # 2 heures en secondes

        # Vérifie si l'utilisateur a déjà été remercié dans les 2 dernières heures
        if message.author.id in bump_reminders:
            await message.channel.send(f"{message.author.mention}, c'est l'heure de bump à nouveau !")

        # Supprime le rappel une fois envoyé
        del bump_reminders[message.author.id]

    await bot.process_commands(message)

async def send_alert_to_admin(message, detected_word):
    """Envoie une alerte privée à l'admin en cas de mot interdit détecté."""
    try:
        admin = await bot.fetch_user(ADMIN_ID)
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
        if message.guild:
            embed.add_field(name="🔗 Lien vers le message", value=f"[Clique ici]({message.jump_url})", inline=False)
        embed.set_footer(text="Système de détection automatique", icon_url=bot.user.avatar.url)
        await admin.send(embed=embed)
    except Exception as e:
        print(f"⚠️ Erreur lors de l'envoi de l'alerte : {e}")

#------------------------------------------------------------------------- Commandes de Bienvenue : Message de Bienvenue + Ghost Ping Join

private_threads = {}  # Stocke les fils privés des nouveaux membres

ETHERYA_SERVER_ID = 1034007767050104892  # L'ID du serveur Etherya
# ID du salon de bienvenue
WELCOME_CHANNEL_ID = 1344194595092697108

# Liste des salons à pinguer
salon_ids = [
    1342179344889675827
]

class GuideView(View):
    def __init__(self, thread):
        super().__init__()
        self.thread = thread
        self.message_sent = False  # Variable pour contrôler l'envoi du message

    @discord.ui.button(label="📘 Guide", style=discord.ButtonStyle.success, custom_id="guide_button_unique")
    async def guide(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.message_sent:  # Empêche l'envoi du message en doublon
            await interaction.response.defer()
            await start_tutorial(self.thread, interaction.user)
            self.message_sent = True

    @discord.ui.button(label="❌ Non merci", style=discord.ButtonStyle.danger, custom_id="no_guide_button_unique")
    async def no_guide(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Fermeture du fil...", ephemeral=True)
        await asyncio.sleep(2)
        await self.thread.delete()

class NextStepView(View):
    def __init__(self, thread):
        super().__init__()
        self.thread = thread

    @discord.ui.button(label="➡️ Passer à la suite", style=discord.ButtonStyle.primary, custom_id="next_button")
    async def next_step(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user = interaction.user

        # Envoi du message privé
        await send_economy_info(user)

        # Envoi du message de confirmation dans le fil privé
        await self.thread.send("📩 Les détails de cette étape ont été envoyés en message privé.")

        # Attente de 2 secondes
        await asyncio.sleep(2)

        # Message d'avertissement avant suppression
        await self.thread.send("🗑️ Ce fil sera supprimé dans quelques instants.")

        # Suppression du fil privé
        await asyncio.sleep(3)
        await self.thread.delete()

async def wait_for_command(thread, user, command):
    def check(msg):
        return msg.channel == thread and msg.author == user and msg.content.startswith(command)

    await thread.send(f"🕒 En attente de `{command}`...")  # Envoi du message d'attente
    await bot.wait_for("message", check=check)  # Attente du message de la commande
    await thread.send("✅ Commande exécutée ! Passons à la suite. 🚀")  # Confirmation après la commande
    await asyncio.sleep(2)  # Pause avant de passer à l'étape suivante

async def start_tutorial(thread, user):
    tutorial_steps = [
        ("💼 **Commande Travail**", "Utilise `!!work` pour gagner un salaire régulièrement !", "!!work"),
        ("💃 **Commande Slut**", "Avec `!!slut`, tente de gagner de l'argent... Mais attention aux risques !", "!!slut"),
        ("🔫 **Commande Crime**", "Besoin de plus de frissons ? `!!crime` te plonge dans des activités illégales !", "!!crime"),
        ("🌿 **Commande Collecte**", "Avec `!!collect`, tu peux ramasser des ressources utiles !", "!!collect"),
        ("📊 **Classement**", "Découvre qui a le plus d'argent en cash avec `!!lb -cash` !", "!!lb -cash"),
        ("🕵️ **Voler un joueur**", "Tente de dérober l'argent d'un autre avec `!!rob @user` !", "!!rob"),
        ("🏦 **Dépôt Bancaire**", "Pense à sécuriser ton argent avec `!!dep all` !", "!!dep all"),
        ("💰 **Solde Bancaire**", "Vérifie ton argent avec `!!bal` !", "!!bal"),
    ]

    for title, desc, cmd in tutorial_steps:
        embed = discord.Embed(title=title, description=desc, color=discord.Color.blue())
        await thread.send(embed=embed)
        await wait_for_command(thread, user, cmd)  # Attente de la commande de l'utilisateur

    # Embed final des jeux
    games_embed = discord.Embed(
        title="🎲 **Autres Commandes de Jeux**",
        description="Découvre encore plus de moyens de t'amuser et gagner des Ezryn Coins !",
        color=discord.Color.gold()
    )
    games_embed.add_field(name="🐔 Cock-Fight", value="`!!cf` - Combat de Poulet !", inline=False)
    games_embed.add_field(name="🃏 Blackjack", value="`!!bj` - Jeux de Carte !", inline=False)
    games_embed.add_field(name="🎰 Slot Machine", value="`!!sm` - Tente un jeu risqué !", inline=False)
    games_embed.add_field(name="🔫 Roulette Russe", value="`!!rr` - Joue avec le destin !", inline=False)
    games_embed.add_field(name="🎡 Roulette", value="`!!roulette` - Fais tourner la roue de la fortune !", inline=False)
    games_embed.set_footer(text="Amuse-toi bien sur Etherya ! 🚀")

    await thread.send(embed=games_embed)
    await thread.send("Clique sur **Passer à la suite** pour découvrir les systèmes impressionnants de notre Economie !", view=NextStepView(thread))

async def send_economy_info(user: discord.Member):
    try:
        economy_embed = discord.Embed(
            title="📌 **Lis ces salons pour optimiser tes gains !**",
            description=(
                "Bienvenue dans l'économie du serveur ! Pour en tirer le meilleur profit, assure-toi de lire ces salons :\n\n"
                "💰 **Comment accéder à l'economie ?**\n➜ <#1344418391544303627>\n\n"
                "📖 **Informations générales**\n➜ <#1340402373708746802>\n\n"
                "💰 **Comment gagner des Coins ?**\n➜ <#1340402729272737926>\n\n"
                "🏦 **Banque de l'Éco 1**\n➜ <#1340403431923519489>\n\n"
                "🏦 **Banque de l'Éco 2**\n➜ <#1344309260825133100>\n\n"
                "🎟️ **Ticket Finances** *(Pose tes questions ici !)*\n➜ <#1340443101386379486>\n\n"
                "📈 **Astuce :** Plus tu en sais, plus tu gagnes ! Alors prends quelques minutes pour lire ces infos. 🚀"
            ),
            color=discord.Color.gold()
        )
        economy_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1168755764760559637.webp?size=96&quality=lossless")
        economy_embed.set_footer(text="Bon jeu et bons profits ! 💰")

        dm_channel = await user.create_dm()
        await dm_channel.send(embed=economy_embed)
    except discord.Forbidden:
        print(f"Impossible d'envoyer un MP à {user.name} ({user.id})")

@bot.event
async def on_member_join(member):
    # Vérifie si le membre a rejoint le serveur Etherya
    if member.guild.id != ETHERYA_SERVER_ID:
        return  # Stoppe l'exécution si ce n'est pas Etherya
    
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
    
    # Création d'un fil privé pour le membre
    channel_id = 1342179655263977492  # Remplace par l'ID du salon souhaité
    channel = bot.get_channel(channel_id)

    if channel and isinstance(channel, discord.TextChannel):
        thread = await channel.create_thread(name=f"🎉 Bienvenue {member.name} !", type=discord.ChannelType.private_thread)
        await thread.add_user(member)
        private_threads[member.id] = thread

        # Embed de bienvenue
        welcome_embed = discord.Embed(
            title="🌌 Bienvenue à Etherya !",
            description=( 
                "Une aventure unique t'attend, entre **économie dynamique**, **stratégies** et **opportunités**. "
                "Prêt à découvrir tout ce que le serveur a à offrir ?"
            ),
            color=discord.Color.blue()
        )
        welcome_embed.set_thumbnail(url=member.avatar.url if member.avatar else bot.user.avatar.url)
        await thread.send(embed=welcome_embed)

        # Embed du guide
        guide_embed = discord.Embed(
            title="📖 Besoin d'un Guide ?",
            description=( 
                "Nous avons préparé un **Guide de l'Économie** pour t'aider à comprendre notre système monétaire et "
                "les différentes façons d'évoluer. Veux-tu le suivre ?"
            ),
            color=discord.Color.gold()
        )
        guide_embed.set_footer(text="Tu peux toujours y accéder plus tard via la commande /guide ! 🚀")
        await thread.send(embed=guide_embed, view=GuideView(thread))  # Envoie le guide immédiatement

@bot.tree.command(name="guide", description="Ouvre un guide personnalisé pour comprendre l'économie du serveur.")
async def guide_command(interaction: discord.Interaction):
    user = interaction.user

    # Vérifie si le serveur est Etherya avant d'exécuter le reste du code
    if interaction.guild.id != ETHERYA_SERVER_ID:
        await interaction.response.send_message("❌ Cette commande est uniquement disponible sur le serveur Etherya.", ephemeral=True)
        return

    # Crée un nouveau thread privé à chaque commande
    channel_id = 1342179655263977492
    channel = bot.get_channel(channel_id)

    if not channel:
        await interaction.response.send_message("❌ Le canal est introuvable ou le bot n'a pas accès à ce salon.", ephemeral=True)
        return

    # Vérifie si le bot peut créer des threads dans ce canal
    if not channel.permissions_for(channel.guild.me).send_messages or not channel.permissions_for(channel.guild.me).manage_threads:
        await interaction.response.send_message("❌ Le bot n'a pas les permissions nécessaires pour créer des threads dans ce canal.", ephemeral=True)
        return

    try:
        # Crée un nouveau thread à chaque fois que la commande est exécutée
        thread = await channel.create_thread(
            name=f"🎉 Bienvenue {user.name} !", 
            type=discord.ChannelType.private_thread,
            invitable=True
        )
        await thread.add_user(user)  # Ajoute l'utilisateur au thread

        # Embed de bienvenue et guide pour un nouveau thread
        welcome_embed = discord.Embed(
            title="🌌 Bienvenue à Etherya !",
            description="Une aventure unique t'attend, entre **économie dynamique**, **stratégies** et **opportunités**. "
                        "Prêt à découvrir tout ce que le serveur a à offrir ?",
            color=discord.Color.blue()
        )
        welcome_embed.set_thumbnail(url=user.avatar.url if user.avatar else bot.user.avatar.url)
        await thread.send(embed=welcome_embed)

    except discord.errors.Forbidden:
        await interaction.response.send_message("❌ Le bot n'a pas les permissions nécessaires pour créer un thread privé dans ce canal.", ephemeral=True)
        return

    # Embed du guide
    guide_embed = discord.Embed(
        title="📖 Besoin d'un Guide ?",
        description="Nous avons préparé un **Guide de l'Économie** pour t'aider à comprendre notre système monétaire et "
                    "les différentes façons d'évoluer. Veux-tu le suivre ?",
        color=discord.Color.gold()
    )
    guide_embed.set_footer(text="Tu peux toujours y accéder plus tard via cette commande ! 🚀")
    await thread.send(embed=guide_embed, view=GuideView(thread))  # Envoie le guide avec les boutons

    await interaction.response.send_message("📩 Ton guide personnalisé a été ouvert.", ephemeral=True)

    # IMPORTANT : Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)
#-------------------------------------------------------------------------- Commandes Liens Etherya: /etherya

@bot.tree.command(name="etherya", description="Obtiens le lien du serveur Etherya !")
async def etherya(interaction: discord.Interaction):
    """Commande slash pour envoyer l'invitation du serveur Etherya"""
    message = (
        "🌟 **[𝑺ץ] 𝑬𝒕𝒉𝒆𝒓𝒚𝒂 !** 🌟\n\n"
        "🍣 ・ Un serveur **Communautaire**\n"
        "🌸 ・ Des membres sympas et qui **sont actifs** !\n"
        "🌋 ・ Des rôles **exclusifs** avec une **boutique** !\n"
        "🎐 ・ **Safe place** & **Un Système Économique développé** !\n"
        "☕ ・ Divers **Salons** pour un divertissement optimal.\n"
        "☁️ ・ Un staff sympa, à l'écoute et qui **recrute** !\n"
        "🔥 ・ Pas convaincu ? Rejoins-nous et vois par toi-même le potentiel de notre serveur !\n\n"
        "🎫 **[Accès direct au serveur Etherya !](https://discord.com/invite/tVVYC2Ynfy) **\n\n"
        "Rejoins-nous et amuse-toi ! 🎉"
    )

    await interaction.response.send_message(message)
#------------------------------------------------------------------------- Commandes de Gestion : +clear, +nuke, +addrole, +delrole

@bot.command()
async def clear(ctx, amount: int = None):
    # Vérifie si l'utilisateur a la permission de gérer les messages
    if ctx.author.guild_permissions.manage_messages:
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
    # Vérifie si l'utilisateur a la permission de gérer les rôles
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")
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
    # Vérifie si l'utilisateur a la permission de gérer les rôles
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")
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
    # Vérifie si l'utilisateur a la permission Administrateur
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Tu n'as pas les permissions nécessaires pour exécuter cette commande.")
        return

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
            # Supprime le salon actuel
            await channel.delete()

            # Crée un nouveau salon avec les mêmes permissions, catégorie et position
            new_channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                category=category
            )

            # Réajuste la position du salon
            await new_channel.edit(position=position)

            # Envoie un message dans le nouveau salon pour confirmer la recréation
            await new_channel.send(
                f"💥 {ctx.author.mention} a **nuké** ce salon. Il a été recréé avec succès."
            )
        except Exception as e:
            await ctx.send(f"Une erreur est survenue lors de la recréation du salon : {e}")
    else:
        await ctx.send("Cette commande doit être utilisée dans un salon texte.")
    # IMPORTANT : Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)
    
#------------------------------------------------------------------------- Commandes d'aide : +aide, /help
@bot.command()
async def aide(ctx):
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
    embed.add_field(name="📚 **Informations**", value=f"• **Mon préfixe** : +\n• **Nombre de commandes** : 70", inline=False)

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


@bot.command()
async def say(ctx, *, text: str = None):
    # Vérifie si l'utilisateur a les permissions d'admin
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")
        return
    
    if text is None:
        await ctx.send("Tu n'as pas écrit de texte à dire !")
        return

    # Supprime le message originel
    await ctx.message.delete()

    # Envoie le texte spécifié
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

# ID du serveur autorisé (Etherya)
AUTORIZED_SERVER_ID = 1034007767050104892

# Commande +prison
@bot.command()
@commands.has_role(1165936153418006548)  # ID du rôle sans guillemets
async def prison(ctx, member: discord.Member = None):
    if ctx.guild.id != AUTORIZED_SERVER_ID:
        embed = discord.Embed(
            title="Commande non autorisée",
            description="Cette commande n'est pas disponible sur ce serveur.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

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
    if ctx.guild.id != AUTORIZED_SERVER_ID:
        embed = discord.Embed(
            title="Commande non autorisée",
            description="Cette commande n'est pas disponible sur ce serveur.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

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
    if ctx.guild.id != AUTORIZED_SERVER_ID:
        embed = discord.Embed(
            title="Commande non autorisée",
            description="Cette commande n'est pas disponible sur ce serveur.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

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
    if ctx.guild.id != AUTORIZED_SERVER_ID:
        embed = discord.Embed(
            title="Commande non autorisée",
            description="Cette commande n'est pas disponible sur ce serveur.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

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

# Commande cautionpayer
@bot.command()
@commands.has_role(1347165421958205470)
async def cautionpayer(ctx, member: discord.Member = None):
    if ctx.guild.id != AUTORIZED_SERVER_ID:
        embed = discord.Embed(
            title="Commande non autorisée",
            description="Cette commande n'est pas disponible sur ce serveur.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

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

# Commande ticket_euro_million
@bot.command()
async def ticket_euro_million(ctx, user: discord.Member):
    if ctx.guild.id != AUTORIZED_SERVER_ID:
        embed = discord.Embed(
            title="Commande non autorisée",
            description="Cette commande n'est pas disponible sur ce serveur.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        return

    # Générer 5 chiffres entre 0 et 5
    numeros = [str(random.randint(0, 5)) for _ in range(5)]
    combinaison = " - ".join(numeros)

    embed_user = discord.Embed(
        title="🎟️ Ticket Euro Million",
        description=f"Voici votre combinaison, **{user.mention}** : **{combinaison}**\n\n"
                    f"Bonne chance ! 🍀",
        color=discord.Color.gold()
    )
    embed_user.set_footer(text="Ticket généré par " + ctx.author.name)
    embed_user.set_footer(text=f"♥️by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed_user)

    embed_announce = discord.Embed(
        title="🎟️ Euro Million - Résultat",
        description=f"**{user.mention}** a tiré le combiné suivant : **{combinaison}**\n\n"
                    f"Commande exécutée par : **{ctx.author.mention}**",
        color=discord.Color.green()
    )
    embed_announce.set_footer(text="Ticket généré avec succès !")
    embed_announce.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

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

async def send_log(ctx, member, action, reason, duration=None):
    guild_id = ctx.guild.id
    settings = GUILD_SETTINGS.get(guild_id, {})
    log_channel_id = settings.get("sanctions_channel")  # Récupération dynamique du salon de logs
    
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            embed = discord.Embed(title="Formulaire des sanctions", color=discord.Color.red())
            embed.add_field(name="Pseudo de la personne sanctionnée:", value=member.mention, inline=False)
            embed.add_field(name="Pseudo du modérateur:", value=ctx.author.mention, inline=False)
            embed.add_field(name="Sanction:", value=action, inline=False)
            embed.add_field(name="Raison:", value=reason, inline=False)
            if duration:
                embed.add_field(name="Durée:", value=duration, inline=False)
            await log_channel.send(embed=embed)
        else:
            await ctx.send("⚠️ Le salon de sanctions configuré est introuvable.", ephemeral=True)
    else:
        await ctx.send("⚠️ Aucun salon de sanctions configuré ! Utilisez /setup.", ephemeral=True)

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

async def check_permissions(user: discord.Member) -> bool:
    if not isinstance(user, discord.Member):  # Vérifie que user est bien un membre
        return False

    mod_role = discord.utils.get(user.guild.roles, id=MOD_ROLE_ID)
    if mod_role and mod_role in user.roles:
        return True
    return False

async def is_immune(member):
    immune_role = discord.utils.get(member.guild.roles, id=IMMUNE_ROLE_ID)
    return immune_role and immune_role in member.roles

@bot.tree.command(name="ban")  # Tout en minuscules
@app_commands.describe(member="Le membre à bannir", reason="Raison du bannissement")
async def ban(ctx, member: discord.Member, reason: str = "Aucune raison spécifiée"):
    if await check_permissions(ctx) and not await is_immune(member):
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} a été banni.")
        await send_log(ctx, member, "Ban", reason)
        await send_dm(member, "Ban", reason)

@bot.tree.command(name="unban")
@app_commands.describe(user_id="ID du membre à débannir")
async def unban(interaction: discord.Interaction, user_id: int):
    if await check_permissions(interaction):
        user = await bot.fetch_user(user_id)
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"{user.mention} a été débanni.")
        await send_log(interaction, user, "Unban", "Réintégration")
        await send_dm(user, "Unban", "Réintégration")


@bot.tree.command(name="kick")  # Tout en minuscules
@app_commands.describe(member="Expulse un membre", reason="Raison du kick")
async def kick(ctx, member: discord.Member, reason: str = "Aucune raison spécifiée"):
    if await check_permissions(ctx) and not await is_immune(member):
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} a été expulsé.")
        await send_log(ctx, member, "Kick", reason)
        await send_dm(member, "Kick", reason)


@bot.tree.command(name="mute")  # Tout en minuscules
@app_commands.describe(member="Mute un membre")
async def mute(ctx, member: discord.Member, duration_with_unit: str, *, reason: str = "Aucune raison spécifiée"):
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

@bot.tree.command(name="unmute")  # Tout en minuscules
@app_commands.describe(member="Unmute un membre")
async def unmute(ctx, member: discord.Member):
    if await check_permissions(ctx) and not await is_immune(member):
        muted_role = discord.utils.get(ctx.guild.roles, id=MUTED_ROLE_ID)
        await member.remove_roles(muted_role)
        await ctx.send(f"{member.mention} a été démuté.")
        await send_log(ctx, member, "Unmute", "Réhabilitation")
        await send_dm(member, "Unmute", "Réhabilitation")

@bot.tree.command(name="warn")  # Tout en minuscules
@app_commands.describe(member="Avertir un membre", reason="Raison de l'avertissement")
async def warn(interaction: discord.Interaction, member: discord.Member, *, reason: str = "Aucune raison spécifiée"):
    if not await check_permissions(interaction.user):
        await interaction.response.send_message("🚫 Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    if await is_immune(member):
        await interaction.response.send_message(f"⚠️ {member.mention} est immunisé contre les avertissements.", ephemeral=True)
        return

    await interaction.response.send_message(f"{member.mention} a reçu un avertissement.", ephemeral=True)
    await send_log(interaction, member, "Warn", reason)
    await send_dm(member, "Warn", reason)

#------------------------------------------------------------------------- Commandes Utilitaires : +vc, +alerte, +uptime, +ping, +roleinfo

# Nouvelle fonction pour récupérer le ping role et le channel id dynamiquement depuis la base de données
def get_guild_setup_data(guild_id):
    setup_data = load_guild_settings(guild_id)
    ping_role_id = setup_data.get('staff_role_id')  # Assure-toi que le champ existe dans ta base de données
    channel_id = setup_data.get('sanctions_channel_id')  # Pareil pour le channel ID
    return ping_role_id, channel_id

@bot.command()
async def alerte(ctx, member: discord.Member, *, reason: str):
    # Vérification si l'utilisateur a le rôle nécessaire pour exécuter la commande
    if access_role_id not in [role.id for role in ctx.author.roles]:
        await ctx.send("Vous n'avez pas les permissions nécessaires pour utiliser cette commande.")
        return

    # Récupération des valeurs dynamiques
    ping_role_id, channel_id = get_guild_setup_data(ctx.guild.id)

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

@bot.tree.command(name="info-rôle", description="Obtenez des informations détaillées sur un rôle")
async def roleinfo(interaction: discord.Interaction, role: discord.Role):
    # Vérifier si le rôle existe
    if role is None:
        embed = discord.Embed(title="Erreur", description="Rôle introuvable.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    else:
        # Obtenir tous les rôles triés du plus haut au plus bas
        sorted_roles = sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True)
        total_roles = len(sorted_roles)
        
        # Trouver la position inversée du rôle
        inverse_position = total_roles - sorted_roles.index(role)

        embed = discord.Embed(
            title=f"Informations sur le rôle: {role.name}",
            color=role.color,
            timestamp=interaction.created_at
        )
        
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.add_field(name="ID", value=role.id, inline=False)
        embed.add_field(name="Couleur", value=str(role.color), inline=False)
        embed.add_field(name="Nombre de membres", value=len(role.members), inline=False)
        embed.add_field(name="Position dans la hiérarchie", value=f"{inverse_position}/{total_roles}", inline=False)
        embed.add_field(name="Mentionnable", value=role.mentionable, inline=False)
        embed.add_field(name="Gérer les permissions", value=role.managed, inline=False)
        embed.add_field(name="Créé le", value=role.created_at.strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
        embed.add_field(name="Mention", value=role.mention, inline=False)

        embed.set_footer(text=f"Commande demandée par {interaction.user.name}", icon_url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=embed)

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
async def start9(ctx):
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
async def start7(ctx):
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
async def start1(ctx):
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
async def start3(ctx):
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
async def start2(ctx):
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
async def start8(ctx):
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
async def start5(ctx):
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

class FightView(View):
    def __init__(self):
        super().__init__()
        self.player_hp = 100
        self.guard_hp = 100

    def update_embed(self, interaction):
        embed = discord.Embed(title="Neutraliser la Sécurité", description="Un combat contre les gardes !", color=discord.Color.red())
        embed.add_field(name="Votre Vie", value=f"❤️ {self.player_hp}/100", inline=True)
        embed.add_field(name="Vie des Gardes", value=f"🛡️ {self.guard_hp}/100", inline=True)
        return embed
    
    async def check_winner(self, interaction):
        if self.player_hp <= 0:
            embed_lose = discord.Embed(title="Défaite...", description="💀 Vous avez perdu contre la sécurité !", color=discord.Color.dark_red())
            embed_lose.set_footer(text="Retentez votre chance plus tard.")
            await interaction.response.edit_message(embed=embed_lose, view=None)
            return True
        elif self.guard_hp <= 0:
            embed_win = discord.Embed(title="Victoire !", description="🎉 Vous avez vaincu la sécurité et poursuivez le braquage !", color=discord.Color.green())
            embed_win.set_footer(text="Bonne chance pour la suite du braquage !")
            await interaction.response.edit_message(embed=embed_win, view=None)
            return True
        return False

    @discord.ui.button(label="Attaquer", style=discord.ButtonStyle.danger)
    async def attack(self, interaction: discord.Interaction, button: Button):
        player_damage = random.randint(15, 25)  # Augmenté pour que le joueur inflige plus de dégâts
        guard_damage = random.randint(10, 20)  # Réduit pour équilibrer le combat
        self.guard_hp -= player_damage
        self.player_hp -= guard_damage
        
        if await self.check_winner(interaction):
            return
        
        await interaction.response.edit_message(embed=self.update_embed(interaction))
    
    @discord.ui.button(label="Esquiver", style=discord.ButtonStyle.primary)
    async def dodge(self, interaction: discord.Interaction, button: Button):
        if random.random() > 0.5:
            await interaction.response.edit_message(content="✨ Vous avez esquivé l'attaque des gardes !", embed=self.update_embed(interaction))
        else:
            damage = random.randint(5, 15)  # Réduit pour rendre l'échec moins punitif
            self.player_hp -= damage
            if await self.check_winner(interaction):
                return
            await interaction.response.edit_message(content=f"❌ Échec de l'esquive ! Vous perdez {damage} HP.", embed=self.update_embed(interaction))
    
    @discord.ui.button(label="Assommer", style=discord.ButtonStyle.success)
    async def knock_out(self, interaction: discord.Interaction, button: Button):
        if random.random() > 0.7:
            self.guard_hp -= 30
            if await self.check_winner(interaction):
                return
            await interaction.response.edit_message(content="💥 Vous avez assommé un garde ! Il perd 30 HP.", embed=self.update_embed(interaction))
        else:
            await interaction.response.edit_message(content="🚨 Tentative d'assommage échouée !", embed=self.update_embed(interaction))

@bot.command()
async def start6(ctx):
    view = FightView()
    embed = view.update_embed(ctx)
    await ctx.send(embed=embed, view=view)
    
class HackView(View):
    def __init__(self):
        super().__init__()
        self.progress = 0  # Avancement du hack (3 étapes à réussir)
        self.failures = 0  # Nombre d'échecs
        self.max_failures = 3  # Nombre d'erreurs max avant échec total

    async def update_step(self, interaction):
        if self.failures >= self.max_failures:
            embed = discord.Embed(title="❌ Hack Échoué !", description="🚨 Les systèmes de sécurité vous ont repéré !", color=discord.Color.red())
            await interaction.response.edit_message(embed=embed, view=None)
            return

        if self.progress == 0:
            embed = discord.Embed(title="🔑 Étape 1 : Forcer le mot de passe", description="Essayez de deviner ou de forcer le mot de passe du système !", color=discord.Color.blue())
            view = PasswordHackView(self)
        elif self.progress == 1:
            embed = discord.Embed(title="🔥 Étape 2 : Bypass le pare-feu", description="Trouvez une faille pour contourner le pare-feu !", color=discord.Color.orange())
            view = FirewallHackView(self)
        elif self.progress == 2:
            embed = discord.Embed(title="📷 Étape 3 : Déconnecter les caméras", description="Désactivez les caméras de surveillance pour ne pas être repéré !", color=discord.Color.green())
            view = CameraHackView(self)
        else:
            embed = discord.Embed(title="✅ Hack Réussi !", description="🎉 Vous avez désactivé les caméras de sécurité !", color=discord.Color.green())
            embed.set_footer(text="La voie est libre pour continuer le braquage !")
            await interaction.response.edit_message(embed=embed, view=None)
            return
        
        await interaction.response.edit_message(embed=embed, view=view)

class BaseHackView(View):
    def __init__(self, hack_view):
        super().__init__()
        self.hack_view = hack_view

    async def attempt_hack(self, interaction, success_rate, failure_message):
        if random.random() < success_rate:
            self.hack_view.progress += 1
            await self.hack_view.update_step(interaction)
        else:
            self.hack_view.failures += 1
            if self.hack_view.failures >= self.hack_view.max_failures:
                await self.hack_view.update_step(interaction)
            else:
                await interaction.response.edit_message(content=f"{failure_message} ({self.hack_view.failures}/{self.hack_view.max_failures} erreurs)")

class PasswordHackView(BaseHackView):
    @discord.ui.button(label="Forcer le mot de passe", style=discord.ButtonStyle.primary)
    async def force_password(self, interaction: discord.Interaction, button: Button):
        await self.attempt_hack(interaction, 0.5, "❌ Mot de passe incorrect !")

class FirewallHackView(BaseHackView):
    @discord.ui.button(label="Bypass le pare-feu", style=discord.ButtonStyle.danger)
    async def bypass_firewall(self, interaction: discord.Interaction, button: Button):
        await self.attempt_hack(interaction, 0.4, "⚠️ Le pare-feu vous bloque !")

class CameraHackView(BaseHackView):
    @discord.ui.button(label="Déconnecter les caméras", style=discord.ButtonStyle.success)
    async def disconnect_cameras(self, interaction: discord.Interaction, button: Button):
        await self.attempt_hack(interaction, 0.35, "❌ Tentative échouée !")

@bot.command()
async def start4(ctx):
    view = HackView()
    embed = discord.Embed(title="🔑 Étape 1 : Forcer le mot de passe", description="Essayez de deviner ou de forcer le mot de passe du système !", color=discord.Color.blue())
    await ctx.send(embed=embed, view=PasswordHackView(view))

class EscapeView(View):
    def __init__(self):
        super().__init__()
        self.choice_made = False  # Vérifie si une option a été choisie

    async def update_step(self, interaction):
        if self.choice_made:
            embed = discord.Embed(title="✅ Action terminée", description="Vous avez fait votre choix. Résultat imminent.", color=discord.Color.green())
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(title="💥 Fuite explosive", description="Une voiture piégée bloque l'issue, choisissez une option :", color=discord.Color.red())
            await interaction.response.edit_message(embed=embed, view=self)

class EscapeDecisionView(View):
    def __init__(self, escape_view):
        super().__init__()
        self.escape_view = escape_view

    async def handle_choice(self, interaction, choice, success_rate, success_message, failure_message):
        if random.random() < success_rate:
            self.escape_view.choice_made = True
            embed = discord.Embed(title="✅ Succès", description=success_message, color=discord.Color.green())
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(title="❌ Échec", description=failure_message, color=discord.Color.red())
            await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Désamorcer la bombe", style=discord.ButtonStyle.green)
    async def disarm_bomb(self, interaction: discord.Interaction, button: Button):
        await self.handle_choice(interaction, "désamorcer", 0.7, "La bombe a été désamorcée avec succès, vous êtes sauvé !", "Vous avez échoué à désamorcer la bombe, elle explose !")

    @discord.ui.button(label="Foncez dans la voiture", style=discord.ButtonStyle.danger)
    async def crash_car(self, interaction: discord.Interaction, button: Button):
        await self.handle_choice(interaction, "foncer", 0.4, "Vous avez réussi à foncer à travers la voiture, mais vous subissez des dégâts !", "Vous avez foncé dans la voiture, vous subissez de lourds dégâts !")

@bot.command()
async def start10(ctx):
    view = EscapeView()
    embed = discord.Embed(title="💥 Fuite explosive", description="Une voiture piégée bloque l'issue, choisissez une option :", color=discord.Color.red())
    await ctx.send(embed=embed, view=EscapeDecisionView(view))

bounties = {}  # Dictionnaire stockant les primes
hunter_rewards = {}  # Dictionnaire stockant les récompenses des chasseurs
BOUNTY_CHANNEL_ID = 1352651647955898440  # Salon où les victoires sont annoncées
PRIME_IMAGE_URL = "https://cdn.gamma.app/m6u5udkwwfl3cxy/generated-images/MUnIIu5yOv6nMFAXKteig.jpg"

class DuelView(discord.ui.View):
    def __init__(self, player1, player2, prize, ctx):
        super().__init__(timeout=60)
        self.player1 = player1
        self.player2 = player2
        self.hp1 = 100
        self.hp2 = 100
        self.turn = player1  # Le joueur 1 commence
        self.prize = prize
        self.ctx = ctx
        self.winner = None

    async def update_message(self, interaction):
        embed = discord.Embed(title="⚔️ Duel en cours !", color=discord.Color.red())
        embed.add_field(name=f"{self.player1.display_name}", value=f"❤️ {self.hp1} PV", inline=True)
        embed.add_field(name=f"{self.player2.display_name}", value=f"❤️ {self.hp2} PV", inline=True)
        embed.set_footer(text=f"Tour de {self.turn.display_name}")
        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Attaquer", style=discord.ButtonStyle.red)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.turn:
            await interaction.response.send_message("Ce n'est pas ton tour !", ephemeral=True)
            return

        success_chance = random.random()
        if success_chance > 0.2:  # 80% chance de succès
            damage = random.randint(15, 50)
            if self.turn == self.player1:
                self.hp2 -= damage
                self.turn = self.player2
            else:
                self.hp1 -= damage
                self.turn = self.player1
        else:
            await interaction.response.send_message(f"{interaction.user.mention} rate son attaque !", ephemeral=False)
            self.turn = self.player2 if self.turn == self.player1 else self.player1

        await self.check_winner(interaction)

    @discord.ui.button(label="Esquiver", style=discord.ButtonStyle.blurple)
    async def dodge(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.turn:
            await interaction.response.send_message("Ce n'est pas ton tour !", ephemeral=True)
            return

        success = random.random() < 0.5
        if success:
            await interaction.response.send_message(f"{interaction.user.mention} esquive l'attaque avec succès !", ephemeral=False)
        else:
            damage = random.randint(15, 30)
            if self.turn == self.player1:
                self.hp1 -= damage
            else:
                self.hp2 -= damage

        await self.check_winner(interaction)
        await self.update_message(interaction)

    async def check_winner(self, interaction):
        if self.hp1 <= 0:
            self.winner = self.player2
            await self.end_duel(interaction, self.player2, self.player1)
        elif self.hp2 <= 0:
            self.winner = self.player1
            await self.end_duel(interaction, self.player1, self.player2)
        else:
            await self.update_message(interaction)

    async def end_duel(self, interaction, winner, loser):
        embed = discord.Embed(title="🏆 Victoire !", description=f"{winner.mention} remporte le duel !", color=discord.Color.green())
        await interaction.response.edit_message(embed=embed, view=None)
        channel = self.ctx.guild.get_channel(BOUNTY_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

        # Vérifier si le perdant avait une prime
        if loser.id in bounties:
            if winner.id != loser.id:  # Seulement si le gagnant n'était PAS celui avec la prime
                if winner.id not in hunter_rewards:
                    hunter_rewards[winner.id] = 0
                hunter_rewards[winner.id] += self.prize  # Ajouter la prime au chasseur

            # Supprimer la prime du joueur capturé
            del bounties[loser.id]

@bot.command()
async def bounty(ctx, member: discord.Member, prize: int):
    """Met une prime sur un joueur (réservé aux administrateurs)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Tu n'as pas la permission d'exécuter cette commande.")
        return

    bounties[member.id] = prize
    embed = discord.Embed(title="📜 Nouvelle Prime !", description=f"Une prime de {prize} Ezryn Coins a été placée sur {member.mention} !", color=discord.Color.gold())
    embed.set_image(url=PRIME_IMAGE_URL)
    await ctx.send(embed=embed)

@bot.command()
async def capture(ctx, target: discord.Member):
    """Déclenche un duel pour capturer un joueur avec une prime"""
    if target.id not in bounties:
        await ctx.send("Ce joueur n'a pas de prime sur sa tête !")
        return

    prize = bounties[target.id]
    view = DuelView(ctx.author, target, prize, ctx)
    embed = discord.Embed(title="🎯 Chasse en cours !", description=f"{ctx.author.mention} tente de capturer {target.mention} ! Un duel commence !", color=discord.Color.orange())
    await ctx.send(embed=embed, view=view)


@bot.command()
async def prime(ctx, member: discord.Member = None):
    """Affiche la prime du joueur ou de l'utilisateur"""
    member = member or ctx.author  # Par défaut, on affiche la prime du commanditaire
    if member.id not in bounties:
        embed = discord.Embed(title="📉 Aucune prime !", description=f"Aucune prime n'est actuellement placée sur **{member.mention}**.", color=discord.Color.red())
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)
    else:
        prize = bounties[member.id]
        embed = discord.Embed(title="💰 Prime actuelle", description=f"La prime sur **{member.mention}** est de **{prize} Ezryn Coins**.", color=discord.Color.green())
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)

@bot.command()
async def rewards(ctx, member: discord.Member = None):
    """Affiche les récompenses accumulées par un joueur ou par soi-même"""
    member = member or ctx.author  # Si aucun membre n'est spécifié, on affiche pour l'auteur
    reward = hunter_rewards.get(member.id, 0)
    embed = discord.Embed(
        title="🏅 Récompenses de chasse",
        description=f"💰 **{member.mention}** possède **{reward} Ezryn Coins** en récompenses.",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def rrewards(ctx, target: discord.Member, amount: int):
    """Commande réservée aux admins pour retirer des récompenses à un joueur"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("🚫 Tu n'as pas la permission d'utiliser cette commande.")
        return

    if target.id not in hunter_rewards or hunter_rewards[target.id] < amount:
        await ctx.send(f"❌ **{target.mention}** n'a pas assez de récompenses.")
        return

    hunter_rewards[target.id] -= amount
    embed = discord.Embed(
        title="⚠️ Récompenses modifiées",
        description=f"🔻 **{amount}** Ezryn Coins retirés à **{target.mention}**.\n💰 Nouveau solde : **{hunter_rewards[target.id]}**.",
        color=discord.Color.orange()
    )
    embed.set_thumbnail(url=target.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def ptop(ctx):
    """Affiche le classement des primes en ordre décroissant"""
    if not bounties:
        await ctx.send("📉 Il n'y a actuellement aucune prime en cours.")
        return

    sorted_bounties = sorted(bounties.items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(title="🏆 Classement des Primes", color=discord.Color.gold())
    
    for index, (user_id, prize) in enumerate(sorted_bounties, start=1):
        member = ctx.guild.get_member(user_id)
        if member:
            embed.add_field(name=f"#{index} - {member.display_name}", value=f"💰 **{prize} Ezryn Coins**", inline=False)

    embed.set_thumbnail(url=PRIME_IMAGE_URL)
    await ctx.send(embed=embed)


@bot.tree.command(name="calcul", description="Effectue une opération mathématique")
@app_commands.describe(nombre1="Le premier nombre", operation="L'opération à effectuer (+, -, *, /)", nombre2="Le deuxième nombre")
async def calcul(interaction: discord.Interaction, nombre1: float, operation: str, nombre2: float):
    await interaction.response.defer()  # ✅ Correctement placé à l'intérieur de la fonction

    if operation == "+":
        resultat = nombre1 + nombre2
    elif operation == "-":
        resultat = nombre1 - nombre2
    elif operation == "*":
        resultat = nombre1 * nombre2
    elif operation == "/":
        if nombre2 != 0:
            resultat = nombre1 / nombre2
        else:
            await interaction.followup.send("❌ Erreur : Division par zéro impossible.")
            return
    else:
        await interaction.followup.send("❌ Opération invalide. Utilisez '+', '-', '*', ou '/'.")
        return

    embed = discord.Embed(
        title="📊 Résultat du calcul",
        description=f"{nombre1} {operation} {nombre2} = **{resultat}**",
        color=discord.Color.green()
    )

    await interaction.followup.send(embed=embed)


# Installer PyNaCl 
try:
    import nacl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyNaCl"])

#------------------------------------------------------------------------- Commande Voice : /connect, /disconnect
# Commande /connect
@bot.tree.command(name="connect", description="Connecte le bot à un salon vocal spécifié.")
@app_commands.describe(channel="Choisissez un salon vocal où connecter le bot")
@commands.has_permissions(administrator=True)
async def connect(interaction: discord.Interaction, channel: discord.VoiceChannel):
    try:
        if not interaction.guild.voice_client:
            await channel.connect()
            embed = discord.Embed(
                title="✅ Connexion réussie !",
                description=f"Le bot a rejoint **{channel.name}**.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="⚠️ Déjà connecté",
                description="Le bot est déjà dans un salon vocal.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"Une erreur est survenue : `{e}`",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# Commande /disconnect
@bot.tree.command(name="disconnect", description="Déconnecte le bot du salon vocal.")
@commands.has_permissions(administrator=True)
async def disconnect(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        embed = discord.Embed(
            title="🚫 Déconnexion réussie",
            description="Le bot a quitté le salon vocal.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="⚠️ Pas connecté",
            description="Le bot n'est dans aucun salon vocal.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
#------------------------------------------------------------------------------------------

# Dictionnaire pour stocker les idées temporairement
idees_dict = {}

# Commande pour ajouter une idée
@bot.tree.command(name="idees", description="Rajoute une idée dans la liste")
@app_commands.checks.has_permissions(administrator=True)
async def ajouter_idee(interaction: discord.Interaction, idee: str):
    user_id = interaction.user.id  # Remplace ctx.author.id par interaction.user.id

    if user_id not in idees_dict:
        idees_dict[user_id] = []
    idees_dict[user_id].append(idee)
    
    embed = discord.Embed(title="Idée ajoutée !", description=f"**{idee}** a été enregistrée.", color=discord.Color.green())

    await interaction.response.send_message(embed=embed)  # Utilise interaction.response.send_message


# Commande pour lister les idées
@bot.command(name="listi")
async def liste_idees(ctx):
    user_id = ctx.author.id
    idees = idees_dict.get(user_id, [])
    
    if not idees:
        embed = discord.Embed(title="Aucune idée enregistrée", description="Ajoute-en une avec /idées !", color=discord.Color.red())
    else:
        embed = discord.Embed(title="Tes idées", color=discord.Color.blue())
        for idx, idee in enumerate(idees, start=1):
            embed.add_field(name=f"Idée {idx}", value=idee, inline=False)
    
    await ctx.send(embed=embed)

#--------------------------------------------------------------------------------------------

SUGGESTION_CHANNEL_ID = 1352366542557282356  # ID du salon des suggestions
NEW_USER_ID = 1166334631784759307  # Nouvel ID à mentionner

# Stockage des suggestions
suggestions = []

# Dictionnaire pour gérer le cooldown des utilisateurs
user_cooldown = {}

class SuggestionModal(discord.ui.Modal, title="💡 Nouvelle Suggestion"):
    def __init__(self):
        super().__init__()

        self.add_item(discord.ui.TextInput(
            label="💬 Votre suggestion",
            style=discord.TextStyle.long,
            placeholder="Décrivez votre suggestion ici...",
            required=True,
            max_length=500
        ))

        self.add_item(discord.ui.TextInput(
            label="🎯 Cela concerne Etherya ou le Bot ?",
            style=discord.TextStyle.short,
            placeholder="Tapez 'Etherya' ou 'Bot'",
            required=True
        ))

        self.add_item(discord.ui.TextInput(
            label="❔ Pourquoi cette suggestion ?",
            style=discord.TextStyle.paragraph,
            placeholder="Expliquez pourquoi cette idée est utile...",
            required=False
        ))

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        # Anti-spam: vérifier cooldown
        if user_id in user_cooldown and time.time() - user_cooldown[user_id] < 60:
            return await interaction.response.send_message(
                "❌ Tu dois attendre avant de soumettre une nouvelle suggestion. Patiente un peu !", ephemeral=True
            )

        user_cooldown[user_id] = time.time()  # Enregistrer le temps du dernier envoi

        suggestion = self.children[0].value.strip()  # Texte de la suggestion
        choice = self.children[1].value.strip().lower()  # Sujet (etherya ou bot)
        reason = self.children[2].value.strip() if self.children[2].value else "Non précisé"

        # Vérification du choix
        if choice in ["etherya", "eth", "e"]:
            choice = "Etherya"
            color = discord.Color.gold()
        elif choice in ["bot", "b"]:
            choice = "Le Bot"
            color = discord.Color.blue()
        else:
            return await interaction.response.send_message(
                "❌ Merci de spécifier un sujet valide : 'Etherya' ou 'Bot'.", ephemeral=True
            )

        channel = interaction.client.get_channel(SUGGESTION_CHANNEL_ID)
        if not channel:
            return await interaction.response.send_message("❌ Je n'ai pas pu trouver le salon des suggestions.", ephemeral=True)

        new_user_mention = f"<@&{NEW_USER_ID}>"

        # Envoie un message de notification à l'utilisateur spécifique
        await channel.send(f"{new_user_mention} 🔔 **Nouvelle suggestion concernant {choice} !**")

        # Création de l'embed
        embed = discord.Embed(
            title="💡 Nouvelle Suggestion !",
            description=f"📝 **Proposée par** {interaction.user.mention}\n\n>>> {suggestion}",
            color=color,
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3039/3039569.png")  # Icône idée
        embed.add_field(name="📌 Sujet", value=f"**{choice}**", inline=True)
        embed.add_field(name="❔ Pourquoi ?", value=reason, inline=False)
        embed.set_footer(
            text=f"Envoyée par {interaction.user.display_name}",
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )

        # Envoi de l'embed
        message = await channel.send(embed=embed)

        # Ajouter les réactions
        await message.add_reaction("❤️")  # Aimer l'idée
        await message.add_reaction("🔄")  # Idée à améliorer
        await message.add_reaction("✅")  # Pour
        await message.add_reaction("❌")  # Contre

        # Sauvegarde de la suggestion pour afficher avec la commande /suggestions
        suggestions.append({
            "message_id": message.id,
            "author": interaction.user,
            "suggestion": suggestion,
            "timestamp": time.time()
        })

        # Confirme l'envoi avec un message sympathique
        await interaction.response.send_message(
            f"✅ **Ta suggestion a été envoyée avec succès !**\nNous attendons les votes des autres membres... 🕒",
            ephemeral=True
        )

        # Envoi d'un message privé à l'auteur
        try:
            dm_embed = discord.Embed(
                title="📩 Suggestion envoyée !",
                description=f"Merci pour ta suggestion ! Voici les détails :\n\n**🔹 Sujet** : {choice}\n**💡 Suggestion** : {suggestion}",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            dm_embed.set_footer(text="Nous te remercions pour ton aide et tes idées ! 🙌")
            await interaction.user.send(embed=dm_embed)
        except discord.Forbidden:
            print(f"[ERREUR] Impossible d'envoyer un MP à {interaction.user.display_name}.")
            # Avertir l'utilisateur dans le salon de suggestions si DM est bloqué
            await channel.send(f"❗ **{interaction.user.display_name}**, il semble que je ne puisse pas t'envoyer un message privé. Vérifie tes paramètres de confidentialité pour autoriser les MPs.")
            
@bot.tree.command(name="suggestion", description="💡 Envoie une suggestion pour Etherya ou le Bot")
async def suggest(interaction: discord.Interaction):
    """Commande pour envoyer une suggestion"""
    await interaction.response.send_modal(SuggestionModal())

# Commande pour afficher les dernières suggestions
@bot.tree.command(name="suggestions", description="📢 Affiche les dernières suggestions")
async def suggestions_command(interaction: discord.Interaction):
    """Commande pour afficher les dernières suggestions"""
    if not suggestions:
        return await interaction.response.send_message("❌ Aucune suggestion en cours. Sois le premier à proposer une idée !", ephemeral=True)

    # Récupérer les 5 dernières suggestions
    recent_suggestions = suggestions[-5:]

    embeds = []
    for suggestion_data in recent_suggestions:
        embed = discord.Embed(
            title="💡 Suggestion",
            description=f"📝 **Proposée par** {suggestion_data['author'].mention}\n\n>>> {suggestion_data['suggestion']}",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"Envoyée le {discord.utils.format_dt(discord.utils.snowflake_time(suggestion_data['message_id']), 'F')}")
        embeds.append(embed)

    # Envoi des embeds
    await interaction.response.send_message(embeds=embeds)

#-------------------------------------------------------------------------------- Rappel: /rappel

# Commande de rappel
@bot.tree.command(name="rappel", description="Définis un rappel avec une durée, une raison et un mode d'alerte.")
@app_commands.describe(
    duree="Durée en secondes",
    raison="Pourquoi veux-tu ce rappel ?",
    prive="Voulez-vous un rappel en privé ? (True/False)"
)
async def rappel(interaction: discord.Interaction, duree: int, raison: str, prive: bool):
    # Confirmation du rappel
    embed = discord.Embed(
        title="🔔 Rappel programmé !",
        description=f"**Raison :** {raison}\n**Durée :** {duree} secondes\n**Mode :** {'Privé' if prive else 'Public'}",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Je te rappellerai à temps ⏳")
    await interaction.response.send_message(embed=embed, ephemeral=True)  # Message visible que par l'utilisateur

    # Attendre le temps indiqué
    await asyncio.sleep(duree)

    # Envoyer le rappel
    rappel_embed = discord.Embed(
        title="⏰ Rappel !",
        description=f"**Raison :** {raison}\n\n⏳ Temps écoulé : {duree} secondes",
        color=discord.Color.green()
    )
    rappel_embed.set_footer(text="Pense à ne pas oublier ! 😉")

    # Envoi en MP ou dans le salon
    if prive:
        await interaction.user.send(embed=rappel_embed)
    else:
        await interaction.channel.send(f"{interaction.user.mention}", embed=rappel_embed)

# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
