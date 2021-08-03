from fastapi import FastAPI


def create_app() -> FastAPI:
    from core.settings import settings

    if settings.dev:
        app = FastAPI()
    else:
        app = FastAPI(root_path="/api/mediaserver")

    from core.file_uploder import router as file_uploder_router

    app.include_router(file_uploder_router, tags=["File uploader"])

    return app


app = create_app()


@app.get("/", include_in_schema=False)
async def root():
    return "Welcome to the mediaserver!!!"


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title="Mediaserver API",
        version="0.0",
        description=(
            "Mediaserver keeps video and image files and returnes them if needed"
        ),
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://avatars2.githubusercontent.com/u/64712541"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7000)
