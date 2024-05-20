import git
import tempfile
import os
import re
import json
import subprocess
from fastapi.responses import StreamingResponse
from client import ModalClient
from token_flow import TokenFlow

import modal

app = modal.App("modal-deploy")
image = (
    modal.Image.debian_slim()
    .apt_install("git")
    .pip_install("GitPython")
    .pip_install("grpcio>=1.59.0")
    .pip_install("modal")
)


def extract_github_info(url: str):
    pattern = r"https:\/\/github\.com\/([^\/]+)\/([^\/]+)\/(.+)"

    match = re.search(pattern, url)

    if match:
        org = match.group(1)
        repo = match.group(2)
        path = match.group(3)

        return (org, repo, path)
    else:
        raise ValueError(
            "The URL is not in the expected format: https://github.com/{org}/{repo}/{path}"
        )


def deploy_repo(github_file_url: str):
    org, repo, path = extract_github_info(github_file_url)

    repo_url = f"https://github.com/{org}/{repo}"
    with tempfile.TemporaryDirectory() as dir_name:
        print(f"Cloning {repo_url} to {dir_name}")

        git.Repo.clone_from(repo_url, dir_name)
        file_path = os.path.join(dir_name, path)

        print(f"Deploying {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"The file {path} does not exist in {repo_url}")

        token_flow = TokenFlow(ModalClient())
        _, web_url, code = token_flow.start()

        yield json.dumps({"web_url": web_url, "code": code})

        print("Waiting for token flow to complete...")

        result = None
        for attempt in range(5):
            result = token_flow.finish()
            if result is not None:
                break
            print(f"Waiting for token flow to complete... (attempt {attempt + 2})")

        if result is None:
            yield json.dumps({"error": "Timeout waiting for token flow to complete"})
            return

        print("Web authentication finished successfully!")

        yield json.dumps(
            {"token_id": result.token_id, "token_secret": result.token_secret}
        )

        modal_env = os.environ.copy()
        modal_env["MODAL_TOKEN_ID"] = result.token_id
        modal_env["MODAL_TOKEN_SECRET"] = result.token_secret
        subprocess.run(["modal", "deploy", file_path], env=modal_env)


@app.function(image=image, secrets=[modal.Secret.from_name("github-secret")])
@modal.web_endpoint()
def deploy_repo_endpoint(github_file_url: str):
    return StreamingResponse(
        deploy_repo(github_file_url), media_type="text/event-stream"
    )
