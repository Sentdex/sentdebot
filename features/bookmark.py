import disnake
import re
from util import general_util

def create_image_embed(message, image, title_name):
  """Create embed from image only"""
  embed = disnake.Embed(title=title_name, color=message.author.colour)
  embed.set_author(name=message.author, icon_url=message.author.avatar)
  embed.set_image(image)
  embed.add_field(
    name="Channel",
    value=f"[Jump to original message]({message.jump_url}) in {message.channel.mention}"
  )
  return embed


async def create_bookmark_embed(message, title_name):
  embed = disnake.Embed(title=title_name, colour=message.author.colour)
  embed.set_author(name=message.author, icon_url=message.author.avatar)

  content = ""
  if message.embeds:
    for embed in message.embeds:
      embed.title, embed.colour = title_name, message.author.colour
      embed.set_author(name=message.author, icon_url=message.author.avatar)
  if message.content:
    content = message.content
  else:
    content += "*Empty*"

  # create list of attachments
  images = []
  files_attached = []
  if message.attachments:
    for attachment in message.attachments:
      if re.search(r"\.png|\.jpg|\.jpeg|\.gif$", str(attachment)):
        images.append(attachment)
      else:
        files_attached.append(await attachment.to_file())

  if images:
    embed.set_image(images[0])
    del images[0]
  if len(content) > 1024:
    parts = general_util.split_to_parts(content, 1024)
    for msg in parts:
      embed.add_field(name="Original message", value=msg, inline=False)
  else:
    embed.add_field(name="Original message", value=content, inline=False)
  embed.add_field(
    name="Channel",
    value=f"[Jump to original message]({message.jump_url}) in {message.channel.mention}"
  )
  return [embed], images, files_attached