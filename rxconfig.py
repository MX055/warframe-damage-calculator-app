import reflex as rx

config = rx.Config(
    app_name="warframe_reflex",
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="dark",
                accent_color="tomato",
                gray_color="slate",
                radius="medium",
                scaling="100%",
            )
        ),
        rx.plugins.SitemapPlugin(),
    ],
)
