# Created by funnyboy_roks
# github.com/funnyboy-roks

import discord
import toml
from discord.ext import commands

config = toml.load('config.toml')  # Load Config from config.toml

bot = commands.Bot(command_prefix=config['command_prefix'])  # Initialise bot


@bot.event
async def on_ready():
    global role_template, guild, all_channels
    print(f'Logged in as: {bot.user.name}')
    print(f'With ID: {bot.user.id}')
    guild = await bot.fetch_guild(config['guild_id'])  # Fetch Guild
    role_template = guild.get_role(
        config['role_template_id'])  # Get Template Role
    all_channels = []
    for channel in bot.get_all_channels():
        channel_data = {}
        channel_ignored = channel.id in config['ignored_channel_ids'] or channel.category_id in config['ignored_category_ids']
        if str(channel.type) != 'category' and not channel_ignored:  # If channel is not a 'category' channel
            channel_data['channel'] = channel
            channel_data['overwrite'] = channel.overwrites_for(role_template)
            all_channels.append(channel_data)  # Add channel to list
    # print('\n'.join([','.join((c['channel'].name, str(c['channel'].type))) for c in all_channels]))


@bot.command()
@commands.has_permissions(manage_guild=True)
async def create_role(ctx, *role_name):
    if len(role_name) == 0:
        await ctx.send(config['messages']['no_name'])
        return

    # Convert list to string from *role_name parameter
    new_role_name = ' '.join(role_name)
    # Create the role
    new_role = await guild.create_role(name=new_role_name, permissions=role_template.permissions)
    for channel in all_channels:
        # If the channel doesn't have the same permissions as the default role(@everyone)
        if channel['overwrite'] != channel['channel'].overwrites_for(guild.default_role):
            # Set the custom permissions
            # print(channel['channel'].name)
            await channel['channel'].set_permissions(new_role, overwrite=channel['overwrite'])
    if len(config['messages']['role_created']) == 0:
        await ctx.send(
            config['messages']['role_created']
                .format(
                    mention=new_role.mention,  
                    name=new_role.name,
                    author=ctx.author.name,
                    id=new_role.id
                ))  # Send the complete message


@create_role.error
async def create_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions): # User doesn't have "manage_guild" permission
        await ctx.send(config['messages']['no_permission'])
    else:
        await ctx.send(config['messages']['unknown_error'])
        print(error)
bot.run(config['bot_token'])  # Run Bot
