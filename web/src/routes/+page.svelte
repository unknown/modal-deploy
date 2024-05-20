<script lang="ts">
	import Footer from '$lib/ui/Footer.svelte';
	import StaticGradient from '$lib/ui/StaticGradient.svelte';

	let fileUrlInput: HTMLInputElement;

	function onSubmit(e: Event) {
		e.preventDefault();
		const fileUrl = fileUrlInput.value;
		console.log('File URL:', fileUrl);
	}
</script>

<StaticGradient />
<div class="flex min-h-screen flex-col">
	<main class="flex max-w-screen-xl flex-1 flex-col items-center justify-center">
		<div class="rounded-lg border border-white/10 bg-white/5 p-4 md:p-6">
			<h2 class="mb-2 text-2xl">Deploy Modal Endpoints</h2>
			<p class="pb-3 text-sm text-zinc-400">
				Deploy web endpoints to Modal with a single click of a button.
			</p>
			<form on:submit={onSubmit} class="flex flex-col items-center gap-4">
				<div class="w-full space-y-1">
					<label for="file-url" class="text-sm font-medium">GitHub File URL</label>
					<input
						type="text"
						id="file-url"
						bind:this={fileUrlInput}
						class="w-full flex-1 rounded-md text-sm text-white/60"
						placeholder="https://github.com/unknown/modal-deploy/blob/main/api/app.py"
					/>
				</div>
				<button class="btn btn-outlined btn-primary">Deploy to Modal</button>
			</form>
		</div>
	</main>
	<Footer />
</div>
