import asyncio
import json

from playwright.async_api import async_playwright
from playwright.async_api import Playwright
from aio_pika import Message, connect, DeliveryMode


async def run(playwright: Playwright):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url="https://m.my.mail.ru/v/topclips/video/alltop/68100.html")
    # await page.goto(url="https://www.youtube.com/shorts/vJU0Sr3WvmU")
    video = await page.get_attribute("xpath=//video", "src")
    connection = await connect("amqp://guest:guest@localhost/")
    title = await page.title()
    async with connection:
        for i in range(10):
            url = page.url
            body = {
                "link": url,
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "merge_output_format": "mp4",
                "outtmpl": f"downloads/%(extractor_key)s/%(id)s_%(width)sp.%(ext)s",
            }


        # Creating a channel
            channel = await connection.channel()

            # Sending the message
            message = Message(
                json.dumps(body, indent=4).encode('utf-8'), delivery_mode=DeliveryMode.PERSISTENT,
            )
            await channel.default_exchange.publish(
                message,
                routing_key='hello',
            )

            print(f" [x] Sent '{body}'")
            await page.keyboard.press("ArrowDown")

            while title == await page.title():
                await page.title()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())