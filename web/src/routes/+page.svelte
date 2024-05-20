<script lang="ts">
	import { deploySchema, tokenFlowSchema, tokenFlowWaitSchema } from '$lib/schemas';
	import Footer from '$lib/ui/Footer.svelte';
	import StaticGradient from '$lib/ui/StaticGradient.svelte';

	let fileUrlInput: HTMLInputElement;

	let loading = false;
	let errorMessage: string = '';
	let statusMessage: string = '';

	async function getChunk(reader: ReadableStreamDefaultReader<Uint8Array>) {
		const { value } = await reader.read();
		const chunk = new TextDecoder().decode(value);
		return chunk;
	}

	async function onSubmit(e: Event) {
		e.preventDefault();
		loading = true;
		errorMessage = '';
		statusMessage = '';

		if (!URL.canParse(fileUrlInput.value)) {
			errorMessage = 'Invalid URL';
			loading = false;
			return;
		}

		const fileUrl = fileUrlInput.value;
		const url =
			'https://unknown--modal-deploy-deploy-repo-endpoint.modal.run/?github_file_url=' +
			encodeURIComponent(fileUrl);

		const reader = await fetch(url)
			.then((response) => response.body?.getReader())
			.catch((error) => {
				errorMessage = error;
				return null;
			});

		// TODO: handle errors
		if (!reader) {
			loading = false;
			return;
		}

		const tokenFlow = await getChunk(reader);
		const tokenFlowResult = tokenFlowSchema.parse(JSON.parse(tokenFlow));
		if (!tokenFlowResult.success) {
			loading = false;
			errorMessage = tokenFlowResult.error;
			statusMessage = '';
			return;
		}

		statusMessage = tokenFlowResult.web_url + ' ' + tokenFlowResult.code;
		window.open(tokenFlowResult.web_url, '_blank');

		const tokenFlowWait = await getChunk(reader);
		const tokenFlowWaitResult = tokenFlowWaitSchema.parse(JSON.parse(tokenFlowWait));
		if (!tokenFlowWaitResult.success) {
			loading = false;
			errorMessage = tokenFlowWaitResult.error;
			statusMessage = '';
			return;
		}

		statusMessage = 'Deploying... (this may take a few minutes)';

		const deploy = await getChunk(reader);
		const deployResult = deploySchema.parse(JSON.parse(deploy));
		if (!deployResult.success) {
			loading = false;
			errorMessage = deployResult.error;
			statusMessage = '';
			return;
		}

		loading = false;
		statusMessage = 'Deployment finished successfully!';
		window.open(deployResult.modal_url, '_blank');
	}
</script>

<StaticGradient />
<div class="flex min-h-screen flex-col">
	<main class="relative flex w-full flex-1 flex-col items-center justify-center">
		<a
			href="https://github.com/unknown/modal-deploy"
			rel="noopener noreferrer"
			target="_blank"
			class="btn btn-outlined absolute right-8 top-8 text-sm"
		>
			Star on GitHub
		</a>
		<div class="max-w-screen-sm rounded-lg border border-white/10 bg-white/5 p-4 md:p-6">
			<h2 class="mb-2 text-2xl">Deploy Modal Endpoints</h2>
			<p class="pb-3 text-sm text-zinc-400">
				Deploy web endpoints to Modal with a single click of a button.
			</p>
			<form on:submit={onSubmit} class="mb-3 flex flex-col items-center gap-4">
				<div class="w-full space-y-1">
					<label for="file-url" class="text-sm font-medium">GitHub File URL</label>
					<input
						type="text"
						id="file-url"
						bind:this={fileUrlInput}
						class="w-full flex-1 rounded-md text-sm"
						placeholder="https://github.com/unknown/modal-deploy/blob/main/api/app.py"
					/>
				</div>
				<button class="btn btn-outlined btn-primary" disabled={loading}>Deploy to Modal</button>
				<p class="text-sm text-zinc-400">
					Your credentials are never saved! To deploy your app, you will be prompted to create a new
					token which will be used to deploy your app. This token is not persisted anywhere.
				</p>
			</form>
			{#if errorMessage}
				<div class="text-sm text-red-500">{errorMessage}</div>
			{/if}
			{#if statusMessage}
				<div class="text-sm text-primary">{statusMessage}</div>
			{/if}
		</div>
	</main>
	<Footer />
</div>
