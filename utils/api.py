# Standard
import asyncio
import requests
import urllib3
import discord
from discord.ext import commands
from typing import Any

# Local
from .auth import Auth
from .pillow import generate_image
from .errors import UserInputErrors

# disable urllib3 warnings that might arise from making requests to 127.0.0.1
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ValorantAPI:
    def __init__(self, interaction=None, username=None, password=None, region=None):
        self.interaction = interaction
        self.username = username
        self.password = password
        self.region = region
        self.session = requests.session()

    def spl(self, word):
        return [char for char in word]
        
    def fetch(self, endpoint="/") -> dict:
        response = self.session.get(f"https://pd.{self.region}.a.pvp.net{endpoint}", headers=self.headers, verify=False)
        return response.json()

    def store_fetch_offers(self) -> dict:
        data = self.fetch("/store/v2/storefront/{user_id}".format(user_id=self.user_id))
        return data["SkinsPanelLayout"]["SingleItemOffers"]
    
    def store_fetch_price(self) -> dict:
        data = self.fetch('/store/v1/offers/')
        return data['Offers']

    def my_daily_offter(self) -> None:
        skinid = self.store_fetch_offers()
        get_price = self.store_fetch_price()
        skin = []
        icon = []
        price = []
        for i in skinid:
            response = self.session.get(
                f"https://valorant-api.com/v1/weapons/skinlevels/{i}")
            api = response.json()
            skin.append(api['data']['displayName'])
            icon.append(api['data']['displayIcon'])
            for x in get_price:
                if x['OfferID'] == i:
                    price.append(str(*x['Cost'].values()))

        return skin, icon, price

    def build_embed(self) -> discord.Embed:
        user = self.interaction.user
        duset = self.spl(self.username)
        cs = "*" * len(duset)
        duser = str(str(duset[0])+str(duset[1])+str(duset[2])+str(cs))
        embed = discord.Embed(title=f"{duser}'s Valorant Store", color=0xfe676e, timestamp=discord.utils.utcnow()) #0x2F3136
        embed.set_image(url='attachment://store-offers.png')        
        embed.set_footer(text=f'Requested by {user.display_name}')
        if user.avatar is not None:
            embed.set_footer(text=f'Requested by {user.display_name}', icon_url=user.avatar)
        return embed

    async def start(self):
        interaction = self.interaction
        try:

            # defers the interaction response.
            await interaction.defer(ephemeral=True)

            # authenticate
            self.user_id, self.headers = Auth(self.username, self.password).authenticate()   

            # generate image
            file = generate_image(self.my_daily_offter())

            # build embed 
            embed = self.build_embed()
            
            # send message for public server
            await interaction.respond('\u200B') #empty text
            await interaction.channel.send(embed=embed, file=file)

        except RuntimeError as e:
            raise UserInputErrors(f'{e}')
        except discord.Forbidden:
            raise UserInputErrors(f"**I don't have enough permission to send message**")
        except discord.HTTPException:
            raise UserInputErrors(f"**Sending the message failed.**")