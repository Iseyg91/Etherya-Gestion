import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
from keep_alive import keep_alive
from discord.ui import Button, View

token = os.environ['ETHERYA']
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True 
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="+", intents=intents)

OWNER_ID = 792755123587645461
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

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild = message.guild
    member = guild.get_member(message.author.id)

    # Vérifier si la personne a le rôle à ignorer
    ignored_role_id = 1170326040485318686
    if any(role.id == ignored_role_id for role in member.roles):
        return

    # Vérifier si le message mentionne l'Owner
    if f"<@{OWNER_ID}>" in message.content:
        embed = discord.Embed(
            title="🔹 Hey, besoin d'aide ?",  
            description=(
                f"Salut {message.author.mention}, merci d’éviter de mentionner le Owner inutilement.\n\n"
                "👥 **L'équipe d'administration est là pour répondre à tes questions et t’aider !**\n"
                "📩 **Besoin d'aide ? Clique sur le bouton ci-dessous ou va dans <#1166093151589634078>.**"
            ),
            color=0x00aaff  # Bleu cyan chill
        )

        # Ajouter l'image personnalisée en bannière
        embed.set_image(url="https://raw.githubusercontent.com/Cass64/EtheryaBot/refs/heads/main/images_etherya/etheryaBot_banniere.png") 

        # Ajouter la photo de profil du bot en thumbnail
        if bot.user.avatar:
            embed.set_thumbnail(url=bot.user.avatar.url) 
        
        # Ajouter un champ explicatif
        embed.add_field(
            name="❓ Pourquoi éviter de mentionner le Owner ?", 
            value="Le Owner est souvent occupé avec la gestion du serveur. Pour une réponse rapide et efficace, passe par le support ou un admin ! 🚀",
            inline=False
        )

        # Footer avec l'équipe d'administration
        embed.set_footer(text="Merci de ta compréhension • L'équipe d'administration", icon_url=bot.user.avatar.url)

        # Ajouter un bouton interactif vers le support (avec le lien mis à jour)
        button = Button(label="📩 Ouvrir un ticket", style=discord.ButtonStyle.primary, url="https://discord.com/channels/1034007767050104892/1166093151589634078/1340663542335934488")

        view = View()
        view.add_item(button)

        await message.channel.send(embed=embed, view=view)
    
    # IMPORTANT : Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)

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
    
# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
