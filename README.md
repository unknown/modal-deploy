# modal-deploy

Modal Deploy makes it easy to deploy Modal apps without having to open a terminal or use the command line. It works on any Modal app, but is most useful for deploying web endpoints because they provide accessible entry points to your app.

This project is inspired by both [Supafork](https://github.com/chroxify/supafork) and [Vercel's Deploy Button](https://vercel.com/docs/deployments/deploy-button).

## How it works

Modal Deploy first creates a new token that will be used to deploy your app. It then clones the repository
you provide and runs `modal deploy` (using the newly created token) on the file you provide. Tokens are only used once and are not stored.

While tokens are not persisted, use Modal Deploy at your own risk.
