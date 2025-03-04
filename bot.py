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
bot = commands.Bot(command_prefix="+", intents=intents)

OWNER_ID = 792755123587645461
STAFF_ROLE_ID = 1244339296706760726

# Lorsque le bot est prêt
@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt ! ✅")
    await bot.tree.sync()

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

#------------------------------------------------------------------------- Ignorer les messages des autres bots
@bot.event
async def on_message(message):
    # Ignorer les messages envoyés par d'autres bots
    if message.author.bot:
        return

    # Vérifie si le message mentionne uniquement le bot
    if bot.user.mentioned_in(message) and message.content.strip().startswith(f"<@{bot.user.id}>"):
        embed = discord.Embed(
            title="📜 Commandes du Bot Etherya",
            description="Voici la liste des commandes disponibles :",
            color=discord.Color(0xFFFFFF)
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
    embed.add_field(
        name="🔔 **/embed**", 
        value="Crée un message personnalisé sous forme d'embed avec un titre, une description, une couleur, et une image."
              "Utilisé pour ajouter des messages visuellement attrayants et bien structurés dans le salon.",
        inline=False
   )

 # Image à inclure
    embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryaBot_banniere.png?raw=true")
    
    # Mention du créateur en bas
    embed.add_field(name="Bot développé par 👑 Iseyg", value="Merci à Iseyg pour ce bot incroyable !", inline=False)

    # Envoi de l'embed dans le salon
    await ctx.send(embed=embed)

        await message.channel.send(embed=embed)

    # Assurez-vous que le bot continue de traiter les commandes
    await bot.process_commands(message)
#------------------------------------------------------------------------- Commandes de Gestion : /embed

THUMBNAIL_URL = "https://github.com/Iseyg91/Etherya-Gestion/blob/main/IMG_2571.jpg?raw=true"

# Fonction pour vérifier si une URL est valide
def is_valid_url(url):
    regex = re.compile(
        r'^(https?://)?'  # http:// ou https:// (optionnel)
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # domaine
        r'(/.*)?$'  # chemin (optionnel)
    )
    return bool(re.match(regex, url))

class EmbedBuilderView(discord.ui.View):
    def __init__(self, author: discord.User, channel: discord.TextChannel):
        super().__init__(timeout=180)
        self.author = author
        self.channel = channel
        self.embed = discord.Embed(title="Titre", description="Description", color=discord.Color.blue())
        self.embed.set_thumbnail(url=THUMBNAIL_URL)
        self.second_image_url = None
        self.message = None  # Stocke le message contenant l'embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Vous ne pouvez pas modifier cet embed.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Modifier le titre", style=discord.ButtonStyle.primary)
    async def edit_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedTitleModal(self))

    @discord.ui.button(label="Modifier la description", style=discord.ButtonStyle.primary)
    async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedDescriptionModal(self))

    @discord.ui.button(label="Changer la couleur", style=discord.ButtonStyle.primary)
    async def edit_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = discord.Color.random()
        if self.message:
            await self.message.edit(embed=self.embed, view=self)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

    @discord.ui.button(label="Ajouter une image", style=discord.ButtonStyle.secondary)
    async def add_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedImageModal(self))

    @discord.ui.button(label="Ajouter 2ème image", style=discord.ButtonStyle.secondary)
    async def add_second_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedSecondImageModal(self))

    @discord.ui.button(label="Envoyer", style=discord.ButtonStyle.success)
    async def send_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        embeds = [self.embed]
        if self.second_image_url:
            second_embed = discord.Embed(color=self.embed.color)
            second_embed.set_image(url=self.second_image_url)
            embeds.append(second_embed)

        await self.channel.send(embeds=embeds)
        await interaction.response.send_message("✅ Embed envoyé !", ephemeral=True)

class EmbedTitleModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Modifier le Titre")
        self.view = view
        self.title_input = discord.ui.TextInput(label="Nouveau Titre", required=True)
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.title = self.title_input.value
        if self.view.message:
            await self.view.message.edit(embed=self.view.embed, view=self.view)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

class EmbedDescriptionModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Modifier la description")
        self.view = view
        self.description = discord.ui.TextInput(
            label="Nouvelle description",
            style=discord.TextStyle.paragraph,
            max_length=4000
        )
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.description = self.description.value
        if self.view.message:
            await self.view.message.edit(embed=self.view.embed, view=self.view)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

class EmbedImageModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Ajouter une image")
        self.view = view
        self.image_input = discord.ui.TextInput(label="URL de l'image", required=False)
        self.add_item(self.image_input)

    async def on_submit(self, interaction: discord.Interaction):
        if self.image_input.value and is_valid_url(self.image_input.value):
            self.view.embed.set_image(url=self.image_input.value)
            if self.view.message:
                await self.view.message.edit(embed=self.view.embed, view=self.view)
            else:
                await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ URL invalide.", ephemeral=True)

class EmbedSecondImageModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Ajouter une 2ème image")
        self.view = view
        self.second_image_input = discord.ui.TextInput(label="URL de la 2ème image", required=False)
        self.add_item(self.second_image_input)

    async def on_submit(self, interaction: discord.Interaction):
        if self.second_image_input.value and is_valid_url(self.second_image_input.value):
            self.view.second_image_url = self.second_image_input.value
            if self.view.message:
                await self.view.message.edit(embed=self.view.embed, view=self.view)
            else:
                await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ URL invalide.", ephemeral=True)

@bot.tree.command(name="embed", description="Créer un embed personnalisé")
async def embed_builder(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    role_id = 1170326040485318686  # ID du rôle requis
    if not any(role.id == role_id for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)

    view = EmbedBuilderView(interaction.user, interaction.channel)
    response = await interaction.followup.send(embed=view.embed, view=view, ephemeral=True)
    view.message = response  # Stocke le message contenant la View

    await bot.process_commands(message)
# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
