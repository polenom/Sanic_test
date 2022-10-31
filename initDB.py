from tortoise import Tortoise, run_async


async def init():
    await Tortoise.init(
        db_url='postgres://sanic:sanic@0.0.0.0:2020/sanicproject',
        modules={"models": ["app.models"]}
    )
    await Tortoise.generate_schemas()


run_async(init())