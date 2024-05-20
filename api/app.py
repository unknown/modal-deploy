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
    pattern = r"https:\/\/github\.com\/([^\/]+)\/([^\/]+)\/blob\/([^\/]+)\/(.+)"

    match = re.search(pattern, url)

    if match:
        org = match.group(1)
        repo = match.group(2)
        branch = match.group(3)
        path = match.group(4)

        return (org, repo, branch, path)
    else:
        raise ValueError(
            "The URL is not in the expected format: https://github.com/{org}/{repo}/blob/{branch}/{path}"
        )


def deploy_repo(github_file_url: str):
    try:
        org, repo, branch, path = extract_github_info(github_file_url)

        repo_url = f"https://github.com/{org}/{repo}"
        repo_url_with_creds = repo_url.replace(
            "https://", "https://" + os.environ["GITHUB_TOKEN"] + "@"
        )
        with tempfile.TemporaryDirectory() as dir_name:
            print(f"Cloning {repo_url} to {dir_name}")
            git.Repo.clone_from(repo_url_with_creds, dir_name, branch=branch)

            file_path = os.path.join(dir_name, path)
            if not os.path.exists(file_path):
                raise ValueError(f"The path {path} does not exist in {repo_url}")
            elif not os.path.isfile(file_path):
                raise ValueError(f"The path {path} is not a file in {repo_url}")

            print("Starting token flow...")
            token_flow = TokenFlow(ModalClient())
            _, web_url, code = token_flow.start()

            print("Waiting for token flow to complete...")
            yield json.dumps({"success": True, "web_url": web_url, "code": code}) + "\n"

            result = None
            for attempt in range(5):
                result = token_flow.finish()
                if result is not None:
                    break
                print(f"Waiting for token flow to complete... (attempt {attempt + 2})")

            if result is None:
                raise ValueError("Timeout waiting for token flow to complete")

            print("Web authentication finished successfully!")
            yield json.dumps({"success": True})

            modal_env = {}
            modal_env["PATH"] = os.environ["PATH"]
            modal_env["MODAL_TOKEN_ID"] = result.token_id
            modal_env["MODAL_TOKEN_SECRET"] = result.token_secret

            process = subprocess.Popen(
                ["modal", "deploy", file_path],
                env=modal_env,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            _, stderr = process.communicate()
            exit_code = process.wait()

            if exit_code != 0:
                raise ValueError("Deployment failed: " + stderr.decode("utf-8"))

            print("Deployment finished successfully!")
            yield json.dumps(
                {
                    "success": True,
                    "modal_url": f"https://modal.com/{result.workspace_username}/apps",
                }
            ) + "\n"
    except ValueError as e:
        yield json.dumps(
            {
                "success": False,
                "error": str(e),
            }
        )
    except git.exc.GitCommandError as e:
        yield json.dumps({"success": False, "error": str(e)})
    except Exception as e:
        yield json.dumps({"success": False, "error": "Unhandled exception"})


@app.function(image=image, secrets=[modal.Secret.from_name("github-secret")])
@modal.web_endpoint()
def deploy_repo_endpoint(github_file_url: str):
    return StreamingResponse(
        deploy_repo(github_file_url), media_type="text/event-stream"
    )
