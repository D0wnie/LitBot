import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} prisijungė!")

# !hello
@bot.command()
async def hello(ctx):
    await ctx.send(f"Labas, {ctx.author.name}! 👋")

# !ping
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

# !kick
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Nenurodyta"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.name} buvo išmestas! Priežastis: {reason}")

# !ban
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Nenurodyta"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.name} buvo užbannintas! Priežastis: {reason}")

# !unban
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, username):
    banned = [entry async for entry in ctx.guild.bans()]
    for entry in banned:
        if entry.user.name == username:
            await ctx.guild.unban(entry.user)
            await ctx.send(f"✅ {username} buvo atbannintas!")
            return
    await ctx.send("❌ Vartotojas nerastas!")

# !mute
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason="Nenurodyta"):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False, speak=False)
    await member.add_roles(muted_role)
    await ctx.send(f"🔇 {member.name} buvo nutildytas! Priežastis: {reason}")

# !unmute
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f"🔊 {member.name} buvo nutildymas panaikintas!")
    else:
        await ctx.send("❌ Šis narys nėra nutildytas!")

# !clear
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🗑️ Ištrinta {amount} žinučių!", delete_after=3)

# Welcome sistema
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if channel:
        embed = discord.Embed(
            title=f"👋 Sveikas, {member.name}!",
            description=f"Džiaugiamės tave matydami **{member.guild.name}** serveryje!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="📋 Narių skaičius", value=f"{member.guild.member_count}", inline=False)
        embed.set_footer(text="LitBot • Welcome!")
        await channel.send(embed=embed)

# Ticket sistema
class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Atidaryti Ticketą", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
        if existing:
            await interaction.response.send_message("❌ Jau turi atidarytą ticketą!", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            f"ticket-{user.name.lower()}",
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Ticket Atidarytas!",
            description=f"Sveiki, {user.mention}!\nAprašyk savo problemą ir moderatoriai padės!",
            color=discord.Color.blue()
        )
        embed.set_footer(text="LitBot • Ticket Sistema")

        close_view = CloseTicketButton()
        await channel.send(embed=embed, view=close_view)
        await interaction.response.send_message(f"✅ Ticket atidarytas! {channel.mention}", ephemeral=True)

class CloseTicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Uždaryti Ticketą", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ticket uždaromas...")
        await interaction.channel.delete()

# !ticket komanda - išsiunčia ticket mygtuką
@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    embed = discord.Embed(
        title="🎫 Pagalbos Ticketai",
        description="Spauski mygtuką žemiau kad atidarytum ticketą!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketButton())

# Klaidų handleris
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Neturi teisių šiai komandai!")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Narys nerastas!")

import os
bot.run(os.environ['MTQ5NTkyMzg2NDQzNjIxMTg5Mw.GrOOJW.buhlH0uG8bnLUQiC8DzeV2i4DeuAPyDy2jFCSw'])