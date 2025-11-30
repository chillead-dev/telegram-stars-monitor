import asyncio
import json
import os
import sys
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.payments import GetStarGiftsRequest

try:
    import config
except ImportError:
    print("❌ Файл config.py не найден!")
    print("Скопируйте config.example.py в config.py и настройте параметры")
    sys.exit(1)

class TelegramStarsMonitor:
    def __init__(self):
        self.client = None
        self.data_file = getattr(config, 'DATA_FILE', 'known_gifts.json')
        
    def load_known_gifts(self):
        """Загружает список известных подарков"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Ошибка загрузки данных: {e}")
                return {}
        return {}

    def save_known_gifts(self, gifts_data):
        """Сохраняет список известных подарков"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(gifts_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")

    async def get_available_gifts(self):
        """Получает список доступных подарков"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if not self.client.is_connected():
                    await self.client.connect()
                
                result = await self.client(GetStarGiftsRequest(hash=0))
                gifts = {}
                
                for gift in result.gifts:
                    gift_id = gift.id
                    
                    # Получаем эмодзи стикера
                    sticker_emoji = None
                    if hasattr(gift, 'sticker') and gift.sticker:
                        if hasattr(gift.sticker, 'attributes'):
                            for attr in gift.sticker.attributes:
                                if hasattr(attr, 'alt') and attr.alt:
                                    sticker_emoji = attr.alt
                                    break
                    
                    gifts[gift_id] = {
                        'id': gift_id,
                        'emoji': sticker_emoji,
                        'stars': gift.stars,
                        'convert_stars': getattr(gift, 'convert_stars', None),
