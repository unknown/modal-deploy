<div class="bg-static-gradient absolute top-0 -z-10 w-full"></div>

<style>
	.bg-static-gradient {
		background-image: url('$lib/assets/static-gradient.svg');
		background-repeat: no-repeat;
		background-size: 100% auto;

		/* padding-top percentage is based on width, so this ensures that height >= 40% width.
        It works for any image with an aspect ratio of 5:2 or wider */
		padding-top: 40%;
	}
</style>
