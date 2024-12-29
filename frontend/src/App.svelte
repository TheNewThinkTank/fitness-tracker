<script>
	import { onMount } from 'svelte';
	let workouts = [];
	let dates = [];
	let datesAndSplits = {};
	let workoutDetails = null;
	let selectedDate = '';
  
	async function fetchData(endpoint, setter) {
	  try {
		const response = await fetch(`http://localhost:8000/${endpoint}`);
		if (!response.ok) {
		  throw new Error(`HTTP error! status: ${response.status}`);
		}
		const data = await response.json();
		setter(data);
		console.log(`Fetched ${endpoint}:`, data); // Debugging log
	  } catch (error) {
		console.error(`Error fetching ${endpoint}:`, error); // Debugging log
	  }
	}
  
	function resetState() {
	  workouts = [];
	  dates = [];
	  datesAndSplits = {};
	  workoutDetails = null;
	  selectedDate = '';
	}
  
	function showWorkouts() {
	  resetState();
	  fetchData('data', data => workouts = data);
	}
  
	function showDates() {
	  resetState();
	  fetchData('dates', data => dates = data);
	}
  
	function showDatesAndSplits() {
	  resetState();
	  fetchData('dates_and_splits', data => datesAndSplits = data);
	}
  
	function showWorkoutDetails(date) {
	  resetState();
	  selectedDate = date;
	  fetchData(`dates/${date}`, data => workoutDetails = data);
	}
  </script>
  
  <main>
	<h1>Fitness Tracker</h1>
	<button on:click={showWorkouts}>Show all 2024 workouts</button>
	<button on:click={showDates}>Show all workout dates</button>
	<button on:click={showDatesAndSplits}>Show dates and splits</button>
  
	{#if workouts.length > 0}
	  <h2>All 2024 Workouts</h2>
	  <ul>
		{#each workouts as workout}
		  <li>
			<strong>Date:</strong> {workout.date}<br>
			<strong>Start Time:</strong> {workout.start_time}<br>
			<strong>End Time:</strong> {workout.end_time}<br>
			<strong>Timezone:</strong> {workout.timezone}<br>
			<strong>Split:</strong> {workout.split}<br>
			<strong>Exercises:</strong>
			<ul>
			  {#each Object.entries(workout.exercises) as [exercise, sets]}
				<li>
				  <strong>{exercise}:</strong>
				  <ul>
					{#each sets as set}
					  <li>Set {set.set_number}: {set.reps} reps @ {set.weight}</li>
					{/each}
				  </ul>
				</li>
			  {/each}
			</ul>
		  </li>
		{/each}
	  </ul>
	{/if}
  
	{#if dates.length > 0}
	  <h2>All Workout Dates</h2>
	  <ul>
		{#each dates as date}
		  <li>
			{date} <button on:click={() => showWorkoutDetails(date)}>Show Details</button>
		  </li>
		{/each}
	  </ul>
	{/if}
  
	{#if Object.keys(datesAndSplits).length > 0}
	  <h2>Dates and Splits</h2>
	  <ul>
		{#each Object.entries(datesAndSplits) as [date, splits]}
		  <li>
			<strong>Date:</strong> {date}<br>
			<strong>Splits:</strong> {splits.join(', ')}
		  </li>
		{/each}
	  </ul>
	{/if}
  
	{#if workoutDetails}
	  <h2>Workout Details for {selectedDate}</h2>
	  <pre>{JSON.stringify(workoutDetails, null, 2)}</pre>
	{/if}
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
