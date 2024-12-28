<script>
  import { onMount } from 'svelte';
  let workouts = [];

  onMount(async () => {
    const response = await fetch('/data');
    workouts = await response.json();
  });
</script>

<main>
	<h1>Fitness Tracker</h1>
	<ul>
		{#each workouts as workout}
		  <li>{workout.name}</li>
		{/each}
	  </ul>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>