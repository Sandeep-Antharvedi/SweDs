<script>
  import axios from 'axios';
  import Chart from 'chart.js/auto';

  let timePoints = [
    { Hemoglobin: 10.0, Hematocrit: 30.0, Platelet_Count: 150.0, INR_PT: 1.0, PTT: 25.0 },
    { Hemoglobin: 15.0, Hematocrit: 45.0, Platelet_Count: 300.0, INR_PT: 1.5, PTT: 50.0 },
    { Hemoglobin: 18.0, Hematocrit: 55.0, Platelet_Count: 500.0, INR_PT: 2.0, PTT: 100.0 },
  ];

  let hemorrhageRisk = null;
  let loading = false;
  let error = null;

  let hemorrhageHistory = [];
  let chart = null;

  // Generate a random offset, I used this earlier to test graph functionality
  const randomOffset = () => Math.random() * 0;

  const getSequence = (count) => {
    let seq = timePoints.slice(0, count);
    while (seq.length < 3) {
      seq.push({ ...seq[seq.length - 1] });
    }
    return seq;
  };

  const predictForCount = async (count) => {
    try {
      const response = await axios.post('http://localhost:8000/predict', { time_series: getSequence(count) });
      const adjustedHemorrhage = response.data.hemorrhage_risk + randomOffset();
      return { hemorrhage: adjustedHemorrhage };
    } catch (err) {
      console.error(err);
      return { hemorrhage: null };
    }
  };

  const predictSequence = async () => {
    loading = true;
    error = null;

    try {
      const res1 = await predictForCount(1);
      const res2 = await predictForCount(2);
      const res3 = await predictForCount(3);

      hemorrhageHistory = [res1.hemorrhage, res2.hemorrhage, res3.hemorrhage];
      hemorrhageRisk = res3.hemorrhage;
      renderChart();
    } catch (err) {
      error = 'Error making prediction. Please check your inputs and try again.';
    } finally {
      loading = false;
    }
  };

  const renderChart = () => {
    const ctx = document.getElementById('predictionChart').getContext('2d');

    if (chart) {
      chart.destroy();
    }

    const minVal = Math.min(...hemorrhageHistory);
    const maxVal = Math.max(...hemorrhageHistory);
    const yMin = Math.max(0, minVal - 2);
    const yMax = Math.min(100, maxVal + 2);

    chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['After 1st Point', 'After 2nd Point', 'After 3rd Point'],
        datasets: [
          {
            label: 'Hemorrhage Risk (%)',
            data: hemorrhageHistory,
            borderColor: 'red',
            borderWidth: 3,
            pointRadius: 5,
            pointHoverRadius: 7,
            fill: false,
            tension: 0.1
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Hemorrhage Risk Evolution'
          },
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            min: yMin,
            max: yMax
          }
        }
      }
    });
  };
</script>

<main>
  <h1>Hemorrhage Risk Prediction</h1>
  {#each timePoints as point, index}
    <fieldset>
      <legend>Time Point {index + 1}</legend>
      
      <label>
        Hemoglobin ({point.Hemoglobin.toFixed(1)}):
        <input type="range" min="0" max="20" step="0.1" bind:value={point.Hemoglobin} />
      </label>
      
      <label>
        Hematocrit ({point.Hematocrit.toFixed(1)}):
        <input type="range" min="0" max="60" step="0.1" bind:value={point.Hematocrit} />
      </label>
      
      <label>
        Platelet Count ({point.Platelet_Count.toFixed(1)}):
        <input type="range" min="0" max="1000" step="1" bind:value={point.Platelet_Count} />
      </label>
      
      <label>
        INR(PT) ({point.INR_PT.toFixed(1)}):
        <input type="range" min="0" max="10" step="0.1" bind:value={point.INR_PT} />
      </label>
      
      <label>
        PTT ({point.PTT.toFixed(1)}):
        <input type="range" min="0" max="200" step="1" bind:value={point.PTT} />
      </label>
    </fieldset>
  {/each}

  <button on:click={predictSequence} disabled={loading}>
    {#if loading} Predicting... {:else} Predict {/if}
  </button>

  {#if hemorrhageHistory.length === 3}
    <h2>Hemorrhage Risk Progression</h2>
    <p><strong>After 1st Point:</strong> {hemorrhageHistory[0].toFixed(2)}%</p>
    <p><strong>After 2nd Point:</strong> {hemorrhageHistory[1].toFixed(2)}%</p>
    <p><strong>After 3rd Point:</strong> {hemorrhageHistory[2].toFixed(2)}%</p>

    <h2>Final Hemorrhage Risk (After 3rd Point)</h2>
    <p><strong>Hemorrhage Risk Probability:</strong> {hemorrhageRisk.toFixed(2)}%</p>

    <!-- Display WARNING if the third prediction is > 17% -->
    {#if hemorrhageHistory[2] > 17}
      <p style="color: red; font-weight: bold;">WARNING</p>
    {/if}

    <canvas id="predictionChart" width="400" height="200"></canvas>
  {/if}

  {#if error}
    <p style="color: red;">{error}</p>
  {/if}
</main>

<style>
  fieldset {
    margin-bottom: 1rem;
    padding: 1rem;
    border: 1px solid #ccc;
  }
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: bold;
  }
  input[type=range] {
    width: 100%;
    margin: 0.5rem 0;
  }
  button {
    padding: 0.5rem 1rem;
    margin-bottom: 1rem;
    font-size: 1rem;
  }
  canvas {
    margin-top: 2rem;
  }
</style>
